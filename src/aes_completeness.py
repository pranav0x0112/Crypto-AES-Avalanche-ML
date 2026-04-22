"""
AES Completeness Analysis
Determines which output bits are affected by each input bit across rounds.

For each input bit position:
- Generate random plaintexts
- Flip that input bit
- Encrypt both versions
- Track which output bits change
- Build a 128x128 dependency matrix

Completeness = proportion of output bits affected by at least one input bit
"""

from aes import AES, bytes2matrix, matrix2bytes
from aes import sub_bytes, shift_rows, mix_columns, add_round_key
import os
import random
import numpy as np
import matplotlib.pyplot as plt


def flip_bit(data, bit_pos):
    """Flip a single bit in data."""
    data = bytearray(data)
    data[bit_pos // 8] ^= (1 << (bit_pos % 8))
    return bytes(data)


def get_bit(data, bit_pos):
    """Extract a single bit from data."""
    byte_idx = bit_pos // 8
    bit_idx = bit_pos % 8
    return (data[byte_idx] >> bit_idx) & 1


class AESWithStates(AES):
    """AES variant that exposes intermediate round states."""
    
    def encrypt_block_with_states(self, plaintext):
        """Encrypt and return state after each round."""
        assert len(plaintext) == 16
        
        state = bytes2matrix(plaintext)
        states = []
        
        # Initial AddRoundKey (Round 0)
        add_round_key(state, self._key_matrices[0])
        states.append(matrix2bytes(state))
        
        # Main rounds (1-9 for AES-128)
        for i in range(1, self.n_rounds):
            sub_bytes(state)
            shift_rows(state)
            mix_columns(state)
            add_round_key(state, self._key_matrices[i])
            states.append(matrix2bytes(state))
        
        # Final round (no MixColumns)
        sub_bytes(state)
        shift_rows(state)
        add_round_key(state, self._key_matrices[-1])
        states.append(matrix2bytes(state))
        
        return states


def analyze_completeness_for_input_bit(input_bit, samples=100):
    """
    For a specific input bit, test how many output bits it affects across rounds.
    
    Returns:
        dependency_matrix: shape (11, 128) where dependency_matrix[round][output_bit]
                         = proportion of samples where input_bit affected output_bit
    """
    dependency_matrix = np.zeros((11, 128))
    
    for _ in range(samples):
        key = os.urandom(16)
        aes = AESWithStates(key)
        
        # Generate plaintext and flip specific input bit
        plaintext = os.urandom(16)
        plaintext_flipped = flip_bit(plaintext, input_bit)
        
        # Encrypt both
        states1 = aes.encrypt_block_with_states(plaintext)
        states2 = aes.encrypt_block_with_states(plaintext_flipped)
        
        # For each round, check which output bits changed
        for round_num in range(11):
            for output_bit in range(128):
                bit1 = get_bit(states1[round_num], output_bit)
                bit2 = get_bit(states2[round_num], output_bit)
                
                if bit1 != bit2:
                    dependency_matrix[round_num][output_bit] += 1
    
    # Normalize by number of samples
    dependency_matrix /= samples
    
    return dependency_matrix


def compute_full_completeness_analysis(samples_per_bit=100, threshold=0.1):
    """
    Analyze completeness for all 128 input bits.
    
    Args:
        samples_per_bit: Number of samples per input bit
        threshold: Minimum dependency probability to count as affected (default 0.1 = 10%)
    
    Returns:
        completeness_matrix: shape (128, 11) where [input_bit][round] = 
                           proportion of output bits affected
        full_dependency: shape (11, 128) aggregated dependency matrix
    """
    completeness_matrix = np.zeros((128, 11))
    full_dependency = np.zeros((11, 128))
    
    print(f"Analyzing completeness for each input bit (threshold={threshold:.0%})...")
    print(f"{'Bit':>4} | Round Progress")
    print("-" * 50)
    
    for input_bit in range(128):
        if input_bit % 16 == 0:
            print(f"{input_bit:3d}  | ", end="", flush=True)
        
        # Get dependency pattern for this input bit
        dep = analyze_completeness_for_input_bit(input_bit, samples=samples_per_bit)
        
        # Completeness = how many output bits are affected (threshold = affected in >threshold% of samples)
        for round_num in range(11):
            affected_bits = np.sum(dep[round_num] > threshold)
            completeness_matrix[input_bit][round_num] = affected_bits / 128.0
            full_dependency[round_num] += (dep[round_num] > threshold).astype(float)
        
        if (input_bit + 1) % 16 == 0:
            print(f"✓ {input_bit + 1:3d}/128")
    
    print("\nAnalysis complete!\n")
    
    # Normalize full dependency
    full_dependency /= 128
    
    return completeness_matrix, full_dependency


def print_completeness_summary(completeness_matrix):
    """Print summary statistics."""
    print("=" * 70)
    print("COMPLETENESS ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"\n{'Round':>5} | {'Min':>6} | {'Avg':>6} | {'Max':>6} | Status")
    print("-" * 70)
    
    for round_num in range(11):
        scores = completeness_matrix[:, round_num]
        min_c = np.min(scores)
        avg_c = np.mean(scores)
        max_c = np.max(scores)
        
        # Status indicator
        if avg_c >= 0.95:
            status = "✓ Full diffusion"
        elif avg_c >= 0.75:
            status = "✓ Good diffusion"
        elif avg_c >= 0.50:
            status = "◐ Partial diffusion"
        else:
            status = "✗ Limited diffusion"
        
        print(f"{round_num:5d} | {min_c:6.2%} | {avg_c:6.2%} | {max_c:6.2%} | {status}")
    
    print("=" * 70)
    print(f"Goal: Completeness ≥ 95% by final round (ideal avalanche)")
    print("=" * 70)


def visualize_completeness(completeness_matrix, full_dependency):
    """Create visualizations of completeness."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Average completeness per round
    avg_completeness = np.mean(completeness_matrix, axis=0)
    ax = axes[0, 0]
    ax.plot(range(11), avg_completeness, marker='o', linewidth=2.5, markersize=8)
    ax.axhline(0.95, color='green', linestyle='--', label='95% threshold')
    ax.axhline(0.5, color='orange', linestyle='--', label='50% threshold')
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Average Completeness', fontsize=11)
    ax.set_title('Average Completeness Across Rounds', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xticks(range(11))
    
    # 2. Min/Max completeness per round
    ax = axes[0, 1]
    min_comp = np.min(completeness_matrix, axis=0)
    max_comp = np.max(completeness_matrix, axis=0)
    ax.fill_between(range(11), min_comp, max_comp, alpha=0.3, label='Min-Max range')
    ax.plot(range(11), avg_completeness, marker='o', linewidth=2, label='Average')
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Completeness', fontsize=11)
    ax.set_title('Completeness Range (Min-Max) per Round', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xticks(range(11))
    
    # 3. Heatmap of completeness matrix (input bits vs rounds)
    ax = axes[1, 0]
    im = ax.imshow(completeness_matrix, aspect='auto', cmap='RdYlGn', vmin=0, vmax=1)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Input Bit', fontsize=11)
    ax.set_title('Completeness per Input Bit vs Round', fontsize=12, fontweight='bold')
    ax.set_xticks(range(11))
    ax.set_yticks([0, 32, 64, 96, 127])
    plt.colorbar(im, ax=ax, label='Completeness')
    
    # 4. Dependency matrix heatmap (final round)
    ax = axes[1, 1]
    im = ax.imshow(full_dependency[-1].reshape(16, 8), cmap='Blues', vmin=0, vmax=1)
    ax.set_xlabel('Output Bits (grouped)', fontsize=11)
    ax.set_ylabel('Output Bits (grouped)', fontsize=11)
    ax.set_title('Final Round: Output Bit Dependencies', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Dependency frequency')
    
    plt.tight_layout()
    plt.savefig('results/aes_completeness.png', dpi=300, bbox_inches='tight')
    print("\n✓ Visualization saved to results/aes_completeness.png")
    plt.show()


# Main execution
if __name__ == '__main__':
    print("=" * 70)
    print("AES-128 COMPLETENESS ANALYSIS")
    print("=" * 70)
    print("\nDetermining input-output bit dependencies across rounds...")
    print("(This may take 1-2 minutes)\n")
    
    # Run analysis with lower threshold (10% = affected in ≥10% of samples)
    completeness_matrix, full_dependency = compute_full_completeness_analysis(
        samples_per_bit=100,
        threshold=0.1
    )
    
    # Print summary
    print_completeness_summary(completeness_matrix)
    
    # Visualize
    visualize_completeness(completeness_matrix, full_dependency)
    
    # Save data
    np.save('results/completeness_matrix.npy', completeness_matrix)
    np.save('results/full_dependency.npy', full_dependency)
    print("\n✓ Data saved to results/completeness_matrix.npy and results/full_dependency.npy")
