# common/encryption_utils.py
import os, base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization, hashes

def load_private_key(path: str):
    data = open(path, "rb").read()
    return serialization.load_pem_private_key(data, password=None)

def load_public_key(path: str):
    data = open(path, "rb").read()
    return serialization.load_pem_public_key(data)

def encrypt_key_rsa(sym_key: bytes, pub_key) -> bytes:
    return pub_key.encrypt(
        sym_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_key_rsa(enc_key: bytes, priv_key) -> bytes:
    return priv_key.decrypt(
        enc_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def aes_encrypt(plaintext: bytes, key: bytes) -> dict:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct    = aesgcm.encrypt(nonce, plaintext, None)
    return {"nonce": nonce, "ciphertext": ct}

def aes_decrypt(nonce: bytes, ciphertext: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def b64enc(data: bytes) -> str:
    return base64.b64encode(data).decode()

def b64dec(data_str: str) -> bytes:
    return base64.b64decode(data_str.encode())