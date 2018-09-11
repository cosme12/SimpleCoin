import hashlib
password = "github"
m = hashlib.sha3_256()
m.update(password.encode('utf-8'))
secret_key = m.hexdigest()
private_key = "04c64a452974be72ff789fa504a4322925e98a510a986309abafc63e4143b26d"
public_key = "FNHlQZtOXBoUGiUL3qcOLppy5UuakcYaNrs6KeEMXVUHDOqGWwRjGswBVcXlT4R3B2MDY1dYZelcq4OjMeQ00g=="