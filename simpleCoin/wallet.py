"""This is going to be your wallet. Here you can do several things:
- Generate a new address (public and private key). You are going
to use this address (public key) to send or receive any transactions. You can
have as many addresses as you wish, but keep in mind that if you
lose its credential data, you will not be able to retrieve it.

- Send coins to another address
- Retrieve the entire blockchain and check your balance

If this is your first time using this script don't forget to generate
a new address and edit miner config file with it (only if you are
going to mine).

Timestamp in hashed message. When you send your transaction it will be received
by several nodes. If any node mine a block, your transaction will get added to the
blockchain but other nodes still will have it pending. If any node see that your
transaction with same timestamp was added, they should remove it from the
node_pending_transactions list to avoid it get processed more than 1 time.
"""

import requests
import time
import base64
import ecdsa
from cryptography.fernet import Fernet, InvalidToken
from hashlib import md5
from json import loads, dumps
import os


def wallet():
    response = None
    while response not in ["1", "2", "3"]:
        response = input("""What do you want to do?
        1. Generate new wallet
        2. Send coins to another wallet
        3. Check transactions\n""")
    if response == "1":
        # Generate new wallet
        print("""=========================================\n
IMPORTANT: save this credentials or you won't be able to recover your wallet\n
=========================================\n""")
        generate_ECDSA_keys()
    elif response == "2":
        files_in_directory = []# All files with .wallet extension in the current directory
        for file in os.listdir("./"):
            if file.endswith(".wallet"):
                files_in_directory.append(file)# Add all wallet files found

        if len(files_in_directory) == 0:
            # If there's not any wallet files, the 'manual' process is used
            addr_from = input("From: introduce your wallet address (public key)\n")
            private_key = input("Introduce your private key\n")
        elif len(files_in_directory) == 1:
            wallet = get_data_from_file(files_in_directory[0])
            addr_from, private_key = wallet["public_key"], wallet["private_key"]
        elif len(files_in_directory) > 1:
            print("Various wallets detected:")
            for i in files_in_directory:
                print(i)
            while True:
                wallet_file = input("Which one do you want to use?: ")
                try:
                    wallet = get_data_from_file(wallet_file)
                    break
                except InvalidToken:
                        print("There was an error decrypting the private key.\nEither the password is not correct or the file is corrupted.")
                except FileNotFoundError:
                    print("There was an error finding the file.")

        addr_from, private_key = wallet["public_key"], wallet["private_key"]
        addr_to = input("To: introduce destination wallet address\n")
        amount = input("Amount: number stating how much do you want to send\n")
        print("=========================================\n\n")
        print("Is everything correct?\n")
        print("From: {0}\nPrivate Key: {1}\nTo: {2}\nAmount: {3}\n".format(addr_from, private_key, addr_to, amount))
        response = input("y/n\n")
        if response.lower() == "y":
            send_transaction(addr_from, private_key, addr_to, amount)
    else:  # Will always occur when response == 3.
        check_transactions()

def get_data_from_file(wallet_file):
    """Gets from a .wallet file the following wallet object:
    
            {
                "public_key":"publicKey",
                "private_key":"privateKey",
                "encryption":True or False
            }"""
    with open(wallet_file, "r") as f:
        content = loads(f.read())# Gets the content of the .wallet file
        f.close()
    if content["encryption"]:# If the private key is encrypted
        password = input("The wallet file detected has been encrypted. Please, input the password: ")
        key = gen_encryption_key(password)# Get the password key
        f = Fernet(key)# Create the decryption object with the key
        content["private_key"] = f.decrypt( content["private_key"].encode() ).decode()
    else:# If not, just loads the json object
        print("Not-encrypted wallet file detected.")
    return content

def send_transaction(addr_from, private_key, addr_to, amount):
    """Sends your transaction to different nodes. Once any of the nodes manage
    to mine a block, your transaction will be added to the blockchain. Despite
    that, there is a low chance your transaction gets canceled due to other nodes
    having a longer chain. So make sure your transaction is deep into the chain
    before claiming it as approved!
    """
    # For fast debugging REMOVE LATER
    # private_key="181f2448fa4636315032e15bb9cbc3053e10ed062ab0b2680a37cd8cb51f53f2"
    # amount="3000"
    # addr_from="SD5IZAuFixM3PTmkm5ShvLm1tbDNOmVlG7tg6F5r7VHxPNWkNKbzZfa+JdKmfBAIhWs9UKnQLOOL1U+R3WxcsQ=="
    # addr_to="SD5IZAuFixM3PTmkm5ShvLm1tbDNOmVlG7tg6F5r7VHxPNWkNKbzZfa+JdKmfBAIhWs9UKnQLOOL1U+R3WxcsQ=="

    if len(private_key) == 64:
        signature, message = sign_ECDSA_msg(private_key)
        url = 'http://localhost:5000/txion'
        payload = {"from": addr_from,
                   "to": addr_to,
                   "amount": amount,
                   "signature": signature.decode(),
                   "message": message}
        headers = {"Content-Type": "application/json"}

        res = requests.post(url, json=payload, headers=headers)
        print(res.text)
    else:
        print("Wrong address or key length! Verify and try again.")


def check_transactions():
    """Retrieve the entire blockchain. With this you can check your
    wallets balance. If the blockchain is to long, it may take some time to load.
    """
    res = requests.get('http://localhost:5000/blocks')
    print(res.text)

def gen_encryption_key(password):
        """A plain text password can't be used for encrpting or decrypting with Fernet.
        This function returns a 32 bit url-safe base64 encoded key version of the password.
        This key is valid for encrypting and decrypting."""
        h = md5()
        h.update(password.encode())
        return base64.urlsafe_b64encode(h.hexdigest().encode())
        # Now it's ready to use.

def generate_ECDSA_keys():
    """This function takes care of creating your private and public (your address) keys.
    It's very important you don't lose any of them or those wallets will be lost
    forever. If someone else get access to your private key, you risk losing your coins.

    private_key: str
    public_ley: base64 (to make it shorter)
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) #this is your sign (private key)
    private_key = sk.to_string().hex() #convert your private key to hex
    vk = sk.get_verifying_key() #this is your verification key (public key)
    public_key = vk.to_string().hex()
    #we are going to encode the public key to make it shorter
    public_key = base64.b64encode(bytes.fromhex(public_key))
    
    # The private and public key are assembled into a dictionary.
    # Dumping and loading this object with json format will make
    # them easier to manage.
    content = {"public_key":public_key.decode(), "private_key":private_key, "encryption":False}

    filename = input("Write the name of your new address: ") + ".wallet"
    password = input("""
Write a password to encript the new wallet file.
Protecting your file with a password prevents your private key for being
stolen by someone that could have access to the wallet file.
Leave in blank to not use any password. (NOT RECOMMENDED)

Password: """)

    if password != "":
        key = gen_encryption_key(password)# Get the key version of the password
        f = Fernet(key)# Create encryption object with the key version of the password
        content["private_key"] = f.encrypt(content["private_key"].encode()).decode()# Use it to encrypt the private key
        content["encryption"] = True# Make the program know that this file requires a password.
        with open(filename, "w") as f:
            f.write(dumps(content))
    else:
        with open(filename, "w") as f:
            f.write(dumps(content))

    print("Your new address and private key are now in the file {0}".format(filename))

def sign_ECDSA_msg(private_key):
    """Sign the message to be sent
    private_key: must be hex

    return
    signature: base64 (to make it shorter)
    message: str
    """
    # Get timestamp, round it, make it into a string and encode it to bytes
    message = str(round(time.time()))
    bmessage = message.encode()
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    signature = base64.b64encode(sk.sign(bmessage))
    return signature, message


if __name__ == '__main__':
    print("""       =========================================\n
        SIMPLE COIN v1.0.0 - BLOCKCHAIN SYSTEM\n
       =========================================\n\n
        You can find more help at: https://github.com/cosme12/SimpleCoin\n
        Make sure you are using the latest version or you may end in
        a parallel chain.\n\n\n""")
    wallet()
    input("Press ENTER to exit...")
