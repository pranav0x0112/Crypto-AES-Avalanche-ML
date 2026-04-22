from aes import AES, bytes2matrix, matrix2bytes
import os, random
import matplotlib.pyplot as plt

def count_bits(x):
    return bin(x).count("1")

def flip_bit(data, bit_pos):
    data = bytearray(data)
    data[bit_pos // 8] ^= (1 << (bit_pos % 8))
    return bytes(data)

# 🔥 Modified AES to expose round states
class AESWithStates(AES):
    def encrypt_block_with_states(self, plaintext):
        assert len(plaintext) == 16

        state = bytes2matrix(plaintext)
        states = []

        # Round 0
        add_round_key(state, self._key_matrices[0])
        states.append(matrix2bytes(state))

        # Rounds 1–9
        for i in range(1, self.n_rounds):
            sub_bytes(state)
            shift_rows(state)
            mix_columns(state)
            add_round_key(state, self._key_matrices[i])
            states.append(matrix2bytes(state))

        # Final round
        sub_bytes(state)
        shift_rows(state)
        add_round_key(state, self._key_matrices[-1])
        states.append(matrix2bytes(state))

        return states


# ⚠️ import needed functions from original file
from aes import sub_bytes, shift_rows, mix_columns, add_round_key


def test_round_avalanche(samples=300):
    round_avalanches = [[] for _ in range(11)]

    for _ in range(samples):
        key = os.urandom(16)
        aes = AESWithStates(key)

        p1 = os.urandom(16)
        bit = random.randint(0, 127)
        p2 = flip_bit(p1, bit)

        states1 = aes.encrypt_block_with_states(p1)
        states2 = aes.encrypt_block_with_states(p2)

        for r in range(11):
            diff = int.from_bytes(states1[r], 'big') ^ int.from_bytes(states2[r], 'big')
            avalanche = count_bits(diff) / 128
            round_avalanches[r].append(avalanche)

    return [sum(x)/len(x) for x in round_avalanches]


# 🚀 Run
print("AES Round Avalanche")

avg = test_round_avalanche(300)

for i, v in enumerate(avg):
    print(f"Round {i:2d} → {v:.4f}")

# 📊 Plot
plt.plot(range(11), avg, marker='o')
plt.axhline(0.5, linestyle='--')
plt.xlabel("Round")
plt.ylabel("Avalanche")
plt.title("AES Avalanche Across Rounds")
plt.grid()
plt.show()