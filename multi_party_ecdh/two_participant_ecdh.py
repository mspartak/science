from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

# Alice: Generate key pair
alice_private_key = X25519PrivateKey.generate()
alice_public_key = alice_private_key.public_key()

# Bob: Generate key pair
bob_private_key = X25519PrivateKey.generate()
bob_public_key = bob_private_key.public_key()

# Alice obtains shared key based on Bob`s public key
alice_shared_key = alice_private_key.exchange(bob_public_key)
# Bob obtains shared key based on Alice`s public key
bob_shared_key = bob_private_key.exchange(alice_public_key)

print(f"Alice`s shared key: {alice_shared_key.hex()}")
print(f"Bob`s shared key: {bob_shared_key.hex()}")
