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
import sqlite3
import requests
import time
import base64
import ecdsa
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
from datetime import datetime


# my code-------------------------------------------------------------------------------------------------------------
def acc_check():
    login_check = input("Do you have an account?(y/n): ")
    if login_check.lower() == 'y':
        login()
    elif login_check.lower() == 'n':
        reg_check = input("Do you want to register?(y/n): ")
        if reg_check.lower() == 'y':
            reg()
        else:
            print("Goodbye")
            end()
    else:
        print("Invalid input")
        end()


def reg():
    with sqlite3.connect("accounts.db") as db:
        cursor = db.cursor()
    # create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user(
    email VARCHAR(50) PRIMARY KEY,
    firstname VARCHAR(20) NOT NULL,
    surname VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL);
    ''')
    # insert values to table from user input
    u_email = input('Please Enter Your Email: ')
    u_fname = input('Please Enter Your First Name: ')
    u_lname = input('Please Enter Your Last Name: ')
    u_password = input('Please Enter Your Password: ')
    cursor.execute(""" 
    INSERT INTO user(email, firstname, surname, password)
    VALUES (?,?,?,?)   
    """, (u_email, u_fname, u_lname, u_password))
    db.commit()
    print("Data entered successfully")
    db.close()
    print("Please Login Your Account")
    login()


def login():
    email = input("Enter Your Email: ")
    password = input("Enter Your password: ")
    with sqlite3.connect("accounts.db") as db:
        cursor = db.cursor()
    find_user = ("SELECT * FROM user WHERE email = ? AND password = ?")
    cursor.execute(find_user, [(email), (password)])
    results = cursor.fetchall()

    if results:
        for i in results:
            print("Welcome " + i[2])
            wallet()  # connect with main program here

    else:
        print("Email and password not recognised")
        again = input("Do you want to try again?(y/n): ")
        if again.lower() == "n":
            print("Goodbye")
            end()
        elif again.lower() == "y":
            login()
        else:
            end()


# my code-------------------------------------------------------------------------------------------------------------
def wallet():
    response = None
    while response not in ["1", "2", "3", "4", "5"]:
        response = input("""What do you want to do?
        1. Generate new wallet
        2. Send coins to another wallet
        3. Check transactions
        4. Check transactions history (enhanced)
        5. Exit program\n""")

    if response == "1":
        # Generate new wallet
        print("""=========================================\n
IMPORTANT: save this credentials or you won't be able to recover your wallet\n
=========================================\n""")
        generate_ECDSA_keys()
    elif response == "2":
        addr_from = input("From: introduce your wallet address (public key)\n")
        private_key = input("Introduce your private key\n")
        addr_to = input("To: introduce destination wallet address\n")
        amount = input("Amount: number stating how much do you want to send\n")
        print("=========================================\n\n")
        print("Is everything correct?\n")
        print("From: {0}\nPrivate Key: {1}\nTo: {2}\nAmount: {3}\n".format(addr_from, private_key, addr_to, amount))
        response = input("y/n\n")
        if response.lower() == "y":
            send_transaction(addr_from, private_key, addr_to, amount)
    elif response == "4":
        trans_improved()
    elif response == "5":
        end()
    else:  # Will always occur when response == 3.
        check_transactions()


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
        # my program -------------------------------------------------------------
        with sqlite3.connect("translog.db") as db2:
            cursor2 = db2.cursor()
            # create table
            cursor2.execute('''
                CREATE TABLE IF NOT EXISTS transactions(
                private_k VARCHAR(250) NOT NUll,
                sender_k VARCHAR(250) NOT NULL,
                receiver_k VARCHAR(250) NOT NULL,
                c_amount INTEGER NOT NULL,
                dNt TEXT NOT NULL);
                ''')
            # insert values to table from user input

            pri_key = private_key
            pub_key = addr_from
            r_pub_k = addr_to
            c_amount = amount
            dt_for = datetime.now().strftime("%B %d, %Y %I:%M%p")
            cursor2.execute(""" 
                INSERT INTO transactions(private_k, sender_k, receiver_k, c_amount, dNt)
                VALUES (?,?,?,?,?)   
                """, (pri_key, pub_key, r_pub_k, c_amount, dt_for))
            db2.commit()
            # print("Data entered successfully")

        # my code -------------------------------------------------------------
        # my code----------------------------------------------------------------
        share_m = input("Do you want to share this transfer details with email?\n(y/n): ")
        if share_m.lower() == 'y':
            share_with_m()
        elif share_m.lower() == 'n':
            wallet()
        else:
            print("Invalid input")
            print("Auto cancelled")
            wallet()
        # my code----------------------------------------------------------------

    else:
        print("Wrong address or key length! Verify and try again.")


# my code------------------------------------------------------------
def share_with_m():
    r_mail = input("Enter the receiver mail address: ")
    email = 'simplecoinproject@gmail.com'  # Your email
    password = '123Abc321!'  # Your email account password
    send_to_email = r_mail  # Who you are sending the message to
    subject = 'SimpleCoin Transaction Alert'  # The subject line
    message = ''  # The message in the email
    file_location = r'C:\Users\hp\Downloads\SimpleCoin-master\SimpleCoin-master\simpleCoin\transactions_share.txt'
    #file_location = r'C:\Users\hp\Downloads\SimpleCoin-master enhanced (KND)\SimpleCoin-master\simpleCoin\transactions_share.txt'

    with open(file_location) as f:
        message = f.read()

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    # Attach the message to the MIMEMultipart object
    msg.attach(MIMEText(message, 'plain'))

    # Setup the attachment
    filename = os.path.basename(file_location)
    attachment = open(file_location, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()  # You now need to convert the MIMEMultipart object to a string to send
    server.sendmail(email, send_to_email, text)
    server.quit()
    print("Sent Successfully!!!!")
    wallet()


# my code------------------------------------------------------------
def trans_improved():
    pri_k = input("Enter your private key: ")
    with sqlite3.connect("translog.db") as db2:
        cursor2 = db2.cursor()

    cursor2.execute("SELECT * FROM transactions WHERE private_k = '%s'" % pri_k)
    data1 = cursor2.fetchall()
    if len(data1) == 0:
        print("DATA IS NOT FOUND")
    else:
        for row in data1:
            # pri_key = row[0]
            pub_key = row[1]
            r_pub_k = row[2]
            c_amount = row[3]
            dt_for = row[4]
            # print(pri_key)
            print('')
            print("Date and Time: ", dt_for)
            print("From:", pub_key)
            print("To:", r_pub_k)
            print("Amount: ", c_amount)
            print('')
            print('-----------------------------------------------------------------')
    wallet()
# my code------------------------------------------------------------

def check_transactions():
    """Retrieve the entire blockchain. With this you can check your
    wallets balance. If the blockchain is to long, it may take some time to load.
    """
    res = requests.get('http://localhost:5000/blocks')
    print(res.text)
    wallet()


def generate_ECDSA_keys():
    """This function takes care of creating your private and public (your address) keys.
    It's very important you don't lose any of them or those wallets will be lost
    forever. If someone else get access to your private key, you risk losing your coins.

    private_key: str
    public_ley: base64 (to make it shorter)
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # this is your sign (private key)
    private_key = sk.to_string().hex()  # convert your private key to hex
    vk = sk.get_verifying_key()  # this is your verification key (public key)
    public_key = vk.to_string().hex()
    # we are going to encode the public key to make it shorter
    public_key = base64.b64encode(bytes.fromhex(public_key))

    filename = input("Write the name of your new address: ") + ".txt"
    with open(filename, "w") as f:
        f.write("Private key: {0}\nWallet address / Public key: {1}".format(private_key, public_key.decode()))
    print("Your new address and private key are now in the file {0}".format(filename))
    wallet()


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


def end():
    print("This program is closed.")
    exit()


if __name__ == '__main__':
    print("""       =========================================\n
        SIMPLE COIN v1.0.0 - BLOCKCHAIN SYSTEM\n
       =========================================\n\n
        You can find more help at: https://github.com/cosme12/SimpleCoin\n
        Make sure you are using the latest version or you may end in
        a parallel chain.\n\n\n""")
    acc_check()
    input("Press ENTER to exit...")
