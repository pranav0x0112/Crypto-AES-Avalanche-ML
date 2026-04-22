from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import random
import csv

def count_bits(x):
    return bin(x).count("1")

def flip_bit(data, bit_pos):
    byte_index = bit_pos // 8
    bit_index = bit_pos % 8
    data = bytearray(data)
    data[byte_index] ^= (1 << bit_index)
    return bytes(data)

def test_avalanche(plaintext_size, samples=1000):
    """
    Test AES avalanche effect for a given plaintext size.
    
    AES avalanche is defined per 128-bit block, not per full plaintext.
    This ensures we measure avalanche correctly regardless of message size.
    
    Args:
        plaintext_size: Size of plaintext in bytes (16, 32, 64, etc.)
        samples: Number of test samples to run
    
    Returns:
        Tuple of (average_avalanche, all_scores)
    """
    key = get_random_bytes(16)
    avalanche_scores = []
    total_bits = plaintext_size * 8
    
    for _ in range(samples):
        cipher = AES.new(key, AES.MODE_ECB)
        
        # Generate random plaintext of specified size
        plaintext = get_random_bytes(plaintext_size)
        
        # Flip a random bit in the plaintext
        bit_pos = random.randint(0, total_bits - 1)
        flipped = flip_bit(plaintext, bit_pos)
        
        # Encrypt both plaintexts
        c1 = cipher.encrypt(plaintext)
        c2 = cipher.encrypt(flipped)
        
        # Determine which AES block was affected
        # Avalanche is measured per AES block, so only the affected block is considered
        affected_block = bit_pos // 128
        start = affected_block * 16
        end = start + 16
        
        # Extract only the affected 16-byte block from both ciphertexts
        block1 = c1[start:end]
        block2 = c2[start:end]
        
        # XOR the affected blocks and count differing bits
        diff = int.from_bytes(block1, 'big') ^ int.from_bytes(block2, 'big')
        changed_bits = count_bits(diff)
        
        # Calculate avalanche score per block (changed bits / 128)
        avalanche = changed_bits / 128
        avalanche_scores.append(avalanche)
    
    avg_avalanche = sum(avalanche_scores) / len(avalanche_scores)
    return avg_avalanche, avalanche_scores

# Test different plaintext sizes
plaintext_sizes = [16, 32, 64]
samples_per_size = 1000

print("=" * 70)
print("AES Avalanche Effect - Multiple Plaintext Sizes")
print("=" * 70)

results_summary = []

for size in plaintext_sizes:
    avg_avalanche, scores = test_avalanche(size, samples_per_size)
    results_summary.append([size, avg_avalanche])
    print(f"Plaintext size: {size:2d} bytes → Avg avalanche ≈ {avg_avalanche:.4f}")

print("=" * 70)

# Save detailed results for each size
for size in plaintext_sizes:
    avg_avalanche, scores = test_avalanche(size, samples_per_size)
    filename = f"data/avalanche_dataset_{size}bytes.csv"
    
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["size_bytes", "avalanche_score"])
        for score in scores:
            writer.writerow([size, score])
    
    print(f"Saved {samples_per_size} samples for {size}-byte plaintexts to {filename}")

print("\nExperiment complete.")
