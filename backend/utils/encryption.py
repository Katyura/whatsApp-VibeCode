"""Encryption utilities for end-to-end encryption"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import base64
import json

def generate_rsa_keys():
    """Generate RSA public/private key pair"""
    key = RSA.generate(2048)
    public_key = key.publickey().export_key().decode('utf-8')
    private_key = key.export_key().decode('utf-8')
    return public_key, private_key


def encrypt_message(message, recipient_public_key):
    """Encrypt message with recipient's public key"""
    try:
        public_key = RSA.import_key(recipient_public_key.encode('utf-8'))
        cipher = PKCS1_OAEP.new(public_key)
        encrypted_message = cipher.encrypt(message.encode('utf-8'))
        return base64.b64encode(encrypted_message).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_message(encrypted_message, private_key):
    """Decrypt message with private key"""
    try:
        private_key_obj = RSA.import_key(private_key.encode('utf-8'))
        cipher = PKCS1_OAEP.new(private_key_obj)
        encrypted_bytes = base64.b64decode(encrypted_message)
        decrypted_message = cipher.decrypt(encrypted_bytes)
        return decrypted_message.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def hash_otp(otp):
    """Hash OTP for secure storage"""
    from django.contrib.auth.hashers import make_password
    return make_password(otp)


def verify_otp(otp, otp_hash):
    """Verify OTP against hash"""
    from django.contrib.auth.hashers import check_password
    return check_password(otp, otp_hash)
