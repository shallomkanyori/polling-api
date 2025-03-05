import hashlib

def get_ip_hash(ip):
    return hashlib.sha256(ip.encode()).hexdigest()