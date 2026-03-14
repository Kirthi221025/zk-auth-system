import hashlib
import os

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def generate_challenge():
    return os.urandom(16).hex()