import hashlib
password = "Desktop boys"
m = hashlib.sha3_256()
m.update(password.encode('utf-8'))
secret_key = m.hexdigest()
private_key = "6e88f8181f002b07e1a7c7b0bc7cff176865670f381e45e305939903c49bdc90"
public_key = "xICxx0YyiVg0tf5nhWPUI/WUvX0/rs/jJXUI5vTxb87VJ1w9Va7xdbRWK37/hap/5HtAAAM6X312IUJpyyAM3A=="