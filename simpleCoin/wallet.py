"""This is going to be your wallet. Here you can do several things:
- Generate a new address (public and private key). You are going
to use this address to send or recieve any transsaction. You can
have as many addresses as you wish, but keep in mind that if you
lose its credential data, you will not be able to retrieve it.

- Here you will also be able to send coins to another address

If this is your first time using this script don't forget to generate
a new address and edit miner config file with it (only if you are
going to mine).
"""

import requests


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
        print("=========================================\n\n")
        #new wallet
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
    url     = 'http://localhost:5000/txion'
    payload = {"from": addr_from, "to": addr_to, "amount": amount}
    headers = {"Content-Type": "application/json"}

    res = requests.post(url, json=payload, headers=headers)
    print(res.text)

def check_transactions():
    res = requests.get('http://localhost:5000/blocks')
    print(res.text)


if __name__ == '__main__':
    welcome_msg()
    wallet()
    input("Press any key to exit")