import random
import string

def generate(domain="gmail.com"):
    """
    Random email generate karta hai
    """
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@{domain}"
