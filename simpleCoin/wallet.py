"""This is going to be your wallet. Here you can do several things:
- Generate a new address (public and private key). You are going
to use this address (public key) to send or recieve any transactions. You can
have as many addresses as you wish, but keep in mind that if you
lose its credential data, you will not be able to retrieve it.

- Send coins to another address
- Retrieve the entire blockchain and check your balance

If this is your first time using this script don't forget to generate
a new address and edit miner config file with it (only if you are
going to mine).

TODO:
-add timestamp to hashed message. When you send your transaction it will be recieved
by several nodes. If any node mine a block, your transaction will get added to the
blockchain but other nodes still will have it pending. If any node see that your
transaction with same timestamp was added, they should remove it from th
"""

import requests
import ecdsa
import base64

def welcome_msg():
    print("""       =========================================\n
        SIMPLE COIN v1.0.0 - BLOCKCHAIN SYSTEM\n
       =========================================\n\n
        You can find more help at: https://github.com/cosme12/SimpleCoin\n
        Make sure you are using the latest version or you may end in
        a parallel chain.\n\n\n""")


def wallet():
    response = False
    while response not in ["1","2","3"]:
        response = input("""What do you want to do?
        1. Generate new address
        2. Send coins to another wallet
        3. Check transactions\n""")
    if response in "1":
        # Generate new wallet
        print("""=========================================\n
IMPORTANT: save this credentials or you won't be able to recover your wallet\n
=========================================\n""")
        generate_ECDSA_keys()        
    elif response in "2":
        addr_from = input("From: introduce your address\n")
        secret_key = input("Introduce your secret key\n")
        addr_to = input("To: introduce destination address\n")
        amount = input("Amount: number stating how much do you want to send\n")
        print("=========================================\n\n")
        print("Is everything correct?\n")
        print("From: {0}\nSecret Key: {1}\nTo: {2}\nAmount: {3}\n".format(addr_from,secret_key,addr_to,amount))
        response = input("y/n\n")
        if response.lower() == "y":
            send_transaction(addr_from,secret_key,addr_to,amount)
    elif response == "3":
        check_transactions()


def send_transaction(addr_from,secret_key,addr_to,amount):
    """Sends your transaction to different nodes. Once any of the nodes manage
    to mine a block, your transaction will be added to the blockchain. Dispite
    that, there is a ow chance your transaction gets canceled due to other nodes
    having a longer chain. So make sure your transaction is deep into the chain
    before claiming it as approved!
    """
    if len(addr_from) == 64 and len(addr_to) == 64:
        url     = 'http://localhost:5000/txion'
        payload = {"from": addr_from, "to": addr_to, "amount": amount, "message": "message"}
        headers = {"Content-Type": "application/json"}

        res = requests.post(url, json=payload, headers=headers)
        print(res.text)
    else:
        print("Wrong address lenght! Verify and try again.")

def check_transactions():
    """Will give you back the entire blockchain. With this you can check your
    wallets balance. If the blockchain is to long, it may take some time to load.
    """
    res = requests.get('http://localhost:5000/blocks')
    print(res.text)

def generate_ECDSA_keys():
    """This function takes care of creating your private and public (your address) keys.
    It's very important you don't lose any of them or those wallets will be lost
    forever. If someone else get access to your private key, you risk losing your coins.
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1) #this is your sign (private key)
    private_key = sk.to_string().hex() #convert your private key to hex
    vk = sk.get_verifying_key() #this is your virification key (public key)
    public_key = vk.to_string().hex()
    #signature = sk.sign(b"message") #this will add your sign to the message
    #verify is the message is signed by you, using your public key
    #assert vk.verify(signature, b"message")
    print("Private key: {0}".format(private_key))
    #print("Public key: {0}".format(public_key))
    #we are going to encode the public key to make it shorter (from 128 to 64 chars)
    print(base64.b64encode(bytes.fromhex(public_key)))


if __name__ == '__main__':
    welcome_msg()
    wallet()
    input("Press any key to exit...")

