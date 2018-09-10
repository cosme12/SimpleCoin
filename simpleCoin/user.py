import hashlib
m = hashlib.sha3_256()
m.update("This is your password now!".encode('utf-8'))
secret_key = m.hexdigest()
private_key = "b87cfd49cfe5d3d0ef64094f97e40435cd0e0087661ea97a0679b97f7f2e0fc7"
public_key = "9ZTW4v76LnVTZUQu9mZrFru/0IEAc6xQJqb/OpSYFQ90eQvpbUZmn140WhvlidWrMsWA2jTaz8cKEtSX0nlTmw=="