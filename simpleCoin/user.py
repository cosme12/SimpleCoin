import hashlib
m = hashlib.sha3_256()
m.update("This is your password now!".encode('utf-8'))
secret_key = ""
private_key = ""
public_key = ""