from cryptography.hazmat.primitives import hashes

#  CAVS 11.0
#  "SHA-1 ShortMsg" information
#  Generated on Tue Mar 15 08:23:35 2011
#  File: SHA1ShortMsg.rsp
# SHA-1 NIST Test Vector
Len = 32 # message length in bits
Msg = '549e959e'
ExpectedHash = \
    'b78bae6d14338ffccfd5d5b5674a275f6ef9c717'

message = bytes.fromhex(Msg)

# Calculate SHA-1 using single update
digest = hashes.Hash(hashes.SHA1())
digest.update(message)
my_hash = digest.finalize()
print(f"my_hash: {my_hash.hex()}")

# Calculate SHA-1 using 2 updates
message1 = message[0:2] # The first part of the message
message2 = message[2:]  # The second part of the message
digest2 = hashes.Hash(hashes.SHA1())
digest2.update(message1) # process part 1 (update #1)
digest2.update(message2) # process part 2 (update #2)
my_hash2 = digest2.finalize()
print(f"my_hash2: {my_hash2.hex()}")