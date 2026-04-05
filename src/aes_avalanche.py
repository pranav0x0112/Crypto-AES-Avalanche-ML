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

key = get_random_bytes(16)
samples = 2000

results = []

for _ in range(samples):

    cipher = AES.new(key, AES.MODE_ECB)

    plaintext = get_random_bytes(16)

    bit_pos = random.randint(0,127)
    flipped = flip_bit(plaintext, bit_pos)

    c1 = cipher.encrypt(plaintext)
    c2 = cipher.encrypt(flipped)

    diff = int.from_bytes(c1, 'big') ^ int.from_bytes(c2, 'big')
    changed_bits = count_bits(diff)

    avalanche = changed_bits / 128

    results.append([bit_pos, avalanche])

with open("data/avalanche_dataset.csv","w",newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["bit_flipped","avalanche"])
    writer.writerows(results)

print("Dataset generated.")
