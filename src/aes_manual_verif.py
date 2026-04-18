from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def bytes_to_binary(data):
    return ' '.join(f'{b:08b}' for b in data)

# fixed key so the example stays reproducible
key = get_random_bytes(16)

cipher = AES.new(key, AES.MODE_ECB)

# generate plaintext
plaintext = get_random_bytes(16)

# flip a single bit
flipped = bytearray(plaintext)
flipped[0] ^= 1
flipped = bytes(flipped)

# encrypt
cipher1 = cipher.encrypt(plaintext)
cipher2 = cipher.encrypt(flipped)

print("\n===== AES Manual Verification Sample =====\n")

print("Plaintext (hex):")
print(plaintext.hex())

print("\nFlipped Plaintext (hex):")
print(flipped.hex())

print("\nCiphertext 1 (hex):")
print(cipher1.hex())

print("\nCiphertext 2 (hex):")
print(cipher2.hex())

print("\nCiphertext 1 (binary):")
print(bytes_to_binary(cipher1))

print("\nCiphertext 2 (binary):")
print(bytes_to_binary(cipher2))

print("\nNext step (manual):")
print("1. XOR the two ciphertext binary values")
print("2. Count the number of 1 bits")
print("3. Avalanche = changed_bits / 128")