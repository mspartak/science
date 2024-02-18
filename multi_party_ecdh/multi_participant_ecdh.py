from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding

# Define number of participants in the group
participants_count = 4

class Participant():
    def __init__(self, id):
        self.id = id
        self.reset()

    # Reset all internal variables
    def reset(self):
        self.__prkey = None
        self.__pubkey = None
        self.__rx_pubkey = None
        self.public_bytes = None

    # Extracts bytes array from public key.
    def __make_public_bytes(self):
        self.public_bytes = \
            self.__pubkey.public_bytes(Encoding.Raw, PublicFormat.Raw)

    # Generate key pair for ECDH
    def generate_key_pair(self):
        self.__prkey = X25519PrivateKey.generate()
        self.__pubkey = self.__prkey.public_key()
        self.__make_public_bytes()

    # Receive public key as byte array and store internal public key
    def receive_public_key(self, pubkey_bytes):
        self.__received_public_key = \
            X25519PublicKey.from_public_bytes(pubkey_bytes)

    # Calculate next public key and shared secret
    def finish_round(self):
        public_bytes = self.__prkey.exchange(self.__received_public_key)
        self.__pubkey = X25519PublicKey.from_public_bytes(public_bytes)
        self.__make_public_bytes()

# Create list of participants
participants = [Participant(n) for n in range(participants_count) ]

# Number of rounds to obtain shared secret
rounds_count = participants_count - 1

# Each participant Generate Key pairs
for cur_participant in participants:
    print(f"Participant {cur_participant.id} generate key pair.")
    cur_participant.generate_key_pair()

# Perform rounds for shared secret distributions
for cur_round_idx in range(rounds_count):
    print(f"======== Start round {cur_round_idx} ========")
    # First transfer public keys (public bytes) to the next neighbours
    for cur_participant_idx in range(participants_count):
        prev_participant_idx = \
            (cur_participant_idx + participants_count - 1) % participants_count
        participants[cur_participant_idx].receive_public_key(
            participants[prev_participant_idx].public_bytes)
        print(f"Transfer public key from participant"
              f" {prev_participant_idx} to {cur_participant_idx}")
    # Second calculate next public key and shared secret
    for cur_participant in participants:
        cur_participant.finish_round()
        cur_public_bytes =  cur_participant.public_bytes
        print(f"Participant`s {cur_participant.id} shared secret: "
              f"{cur_public_bytes.hex()}")
