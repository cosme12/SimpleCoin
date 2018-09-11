import hashlib
password = "github"
m = hashlib.sha3_256()
m.update(password.encode('utf-8'))
secret_key = m.hexdigest()
private_key = "0529e7d13b2c56ececbe1579f27bb9a4e20f404d96c64d3101af5cd9054c6b90"
public_key = "OdKGVzvZb71iXV+HxM8tCmigtMqW0kF0fJahzZOy03xoIc8fZWjENh99qJcmZP1m6nKodgwA+wDVemDrijzunA=="