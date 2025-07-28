# server/generate_keys.py
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

# Ensure common/ exists
os.makedirs("common", exist_ok=True)

# Paths
priv_path = "common/server_private_key.pem"
pub_path  = "common/server_public_key.pem"

# Generate 2048-bit RSA keypair
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Write private key (PKCS8 PEM, no password)
with open(priv_path, "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Write public key (SubjectPublicKeyInfo PEM)
with open(pub_path, "wb") as f:
    f.write(key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print(f"Keys generated:\n  PRIVATE: {priv_path}\n  PUBLIC:  {pub_path}")