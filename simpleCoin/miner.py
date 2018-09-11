import time
import hashlib
import sys
import json
import requests
import secrets
import string
import base64
from flask import Flask, request
from multiprocessing import Process, Pipe
import ecdsa
import secrets
import string
import logging
import simpleCoin.user as user
from simpleCoin.Block import Block
from simpleCoin.miner_config import MINER_NODE_URL, PEER_NODES, PORT


try:
    assert user.public_key != "" and user.private_key != ""
except AssertionError:
    print("You need to generate keys in your wallet")
    sys.exit()

from flask_sqlalchemy import SQLAlchemy

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



node = Flask(__name__)
node.config['SQLALCHEMY_DATABASE_URI'] = ""
node.config['SECRET_KEY'] = user.secret_key

work = 2


def create_genesis_block():
    """To create each block, it needs the hash of the previous one. First
    block has no previous, so it must be created manually (with index zero
     and arbitrary previous hash)"""
    global work
    pow = "0" * work
    pad = "1337"
    for i in range(4, 64):
        pow += pad[i % work]
    b = Block(0, time.time(), {
        "proof-of-work": pow,
        "transactions": None},
              "0")
    # print(json.dumps({
    #     "index": b.index,
    #     "timestamp": str(b.timestamp),
    #     "data": b.data,
    #     "hash": b.hash
    # }) + "\n")
    return b


# Node's blockchain copy
BLOCKCHAIN = [create_genesis_block()]
""" Stores the transactions that this node has in a list.
If the node you sent the transaction adds a block
it will get accepted, but there is a chance it gets
discarded and your transaction goes back as if it was never
processed"""
NODE_PENDING_TRANSACTIONS = []


def proof_of_work(last_block, transactions):
    data = {"transactions": list(transactions)}
    pow = ""

    def random_str():
        # Generate a random size string from 3 - 27 characters long
        rand_str = ''
        for i in range(0, 0 + secrets.randbelow(25)):
            rand_str += string.ascii_lowercase[secrets.randbelow(26)]  # each char is a random downcase letter [a-z]
        return rand_str

    def genhash():
        pow = random_str()
        m = hashlib.sha3_256()
        data["proof-of-work"] = pow
        m.update((str(last_block.index) + str(last_block.timestamp) + str(data) + str(last_block.previous_hash)).encode('utf-8'))
        return pow, m.hexdigest()

    pow, pow_hash = genhash()
    start_time = time.time()
    # check to see if the first <work> characters of the string are 0
    global work
    while not (pow_hash[0:work] == ("0" * work)):

        # Check if any node found the solution every 60 seconds
        if int((time.time() - start_time) % 60) == 0:
            # If any other node got the proof, stop searching
            new_blockchain = consensus()
            if new_blockchain:
                # (False: another node got proof first, new blockchain)
                return False, new_blockchain
        # generate new hash for next time
        pow, pow_hash = genhash()
    # Once that hash is found, we can return it as a proof of our work
    return pow, pow_hash


def mine(a, blockchain, node_pending_transactions):
    global BLOCKCHAIN
    NODE_PENDING_TRANSACTIONS = node_pending_transactions
    while True:
        """Mining is the only way that new coins can be created.
        In order to prevent too many coins to be created, the process
        is slowed down by a proof of work algorithm.
        """
        # Get the last proof of work
        last_block = BLOCKCHAIN[len(BLOCKCHAIN) - 1]
        NODE_PENDING_TRANSACTIONS = requests.get(MINER_NODE_URL + ":"+PORT+"/txion?update=" + user.public_key).content
        NODE_PENDING_TRANSACTIONS = json.loads(NODE_PENDING_TRANSACTIONS)
        # Then we add the mining reward
        NODE_PENDING_TRANSACTIONS.append({
            "from": "network",
            "to": user.public_key,
            "amount": 1.0})

        # Find the proof of work for the current block being mined
        # Note: The program will hang here until a new proof of work is found

        proof = proof_of_work(last_block, NODE_PENDING_TRANSACTIONS)
        # If we didn't guess the proof, start mining again
        if not proof[0]:
            # Update blockchain and save it to file
            BLOCKCHAIN = proof[1]
            a.send(BLOCKCHAIN)
            continue
        else:

            # Now we can gather the data needed to create the new block
            new_block_data = {
                "proof-of-work": proof[1],
                "transactions": list(NODE_PENDING_TRANSACTIONS)
            }
            new_block_index = last_block.index + 1
            new_block_timestamp = time.time()

            # Empty transaction list
            NODE_PENDING_TRANSACTIONS = []
            # Now create the new block
            mined_block = Block(new_block_index, new_block_timestamp, new_block_data, last_block.hash)

            BLOCKCHAIN.append(mined_block)
            # Let the client know this node mined a block
            # print(json.dumps({
            #     "index": new_block_index,
            #     "timestamp": str(new_block_timestamp),
            #     "data": new_block_data,
            #     "hash": last_block_hash
            # }) + "\n")
            a.send(BLOCKCHAIN)
            requests.get(MINER_NODE_URL + ":"+PORT+"/blocks?update=" + user.public_key)


def find_new_chains():
    # Get the blockchains of every other node
    other_chains = []
    for node_url in PEER_NODES:
        # Get their chains using a GET request
        blocks = None
        try:
            blocks = requests.get(node_url+":"+PORT + "/blocks").content
        except:
            pass
        # Convert the JSON object to a Python dictionary
        if blocks is not None:
            blocks = json.loads(blocks)
            # Verify other node block is correct
            validated = validate_blockchain(blocks)
            if validated:
                # Add it to our list
                other_chains.append(blocks)
    return other_chains


def consensus():
    # Get the blocks from other nodes
    other_chains = find_new_chains()
    # If our chain isn't longest, then we store the longest chain
    global BLOCKCHAIN
    longest_chain = BLOCKCHAIN
    for chain in other_chains:
        if longest_chain == BLOCKCHAIN:
            continue
        if len(longest_chain) < len(chain):
            longest_chain = chain
    # If the longest chain wasn't ours, then we set our chain to the longest
    if longest_chain == BLOCKCHAIN:
        # Keep searching for proof
        return False
    else:
        # Give up searching proof, update chain and start over again
        BLOCKCHAIN = longest_chain
        return BLOCKCHAIN


def validate_blockchain(blockchain):
    global work

    previous = ""
    for block in blockchain:
        if not block.validate(work):
            return False
        for transaction in block.data['transactions']:
            if transaction['from'] == "network" and transaction['amount'] != 1:
                return False
        if block.index == 0:
            previous = block.hash
            continue
        else:
            sha = hashlib.sha256()
            sha.update((str(block.index) + str(block.timestamp) + str(block.data) + str(block.previous_hash)).encode('utf-8'))
            if sha.hexdigest() != block.hash:
                return False
            if previous != block.previous_hash:
                return False
            previous = block.hash

    return True


def validate_signature(public_key, signature, message):
    """Verifies if the signature is correct. This is used to prove
    it's you (and not someone else) trying to do a transaction with your
    address. Called when a user tries to submit a new transaction.
    """
    public_key = (base64.b64decode(public_key)).hex()
    signature = base64.b64decode(signature)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
    # Try changing into an if/else statement as except is too broad.
    try:
        return vk.verify(signature, message.encode())
    except:
        return False


def welcome_msg():
    print("""       =========================================\n
        SIMPLE COIN v1.0.0 - BLOCKCHAIN SYSTEM\n
       =========================================\n\n
        You can find more help at: https://github.com/cosme12/SimpleCoin\n
        Make sure you are using the latest version or you may end in
        a parallel chain.\n\n\n""")


@node.route('/blocks', methods=['GET'])
def get_blocks():
    # Load current blockchain. Only you should update your blockchain
    if request.args.get("update") == user.public_key:
        global BLOCKCHAIN
        BLOCKCHAIN = b.recv()
    chain_to_send = BLOCKCHAIN
    # Converts our blocks into dictionaries so we can send them as json objects later
    chain_to_send_json = []
    for block in chain_to_send:
        block = {
            "index": str(block.index),
            "timestamp": str(block.timestamp),
            "data": str(block.data),
            "hash": block.hash
        }
        chain_to_send_json.append(block)

    # Send our chain to whomever requested it
    ip = request.remote_addr+":"+PORT
    if str(ip) != "127.0.0.1" and ip not in PEER_NODES:
        PEER_NODES.append(ip)
    chain_to_send = json.dumps(chain_to_send_json)
    return chain_to_send


@node.route('/txion', methods=['GET', 'POST'])
def transaction():
    """Each transaction sent to this node gets validated and submitted.
    Then it waits to be added to the blockchain. Transactions only move coins, they don't create it.
    """

    if request.method == 'POST':
        # On each new POST request, we extract the transaction data
        new_txion = request.get_json()
        # Then we add the transaction to our list
        if validate_signature(new_txion['from'], new_txion['signature'], new_txion['message']):
            NODE_PENDING_TRANSACTIONS.append(new_txion)
            # Because the transaction was successfully
            # submitted, we log it to our console
            print("New transaction")
            print("FROM: {0}".format(new_txion['from']))
            print("TO: {0}".format(new_txion['to']))
            print("AMOUNT: {0}\n".format(new_txion['amount']))
            # Then we let the client know it worked out

            #Push to all other available nodes
            for node_url in PEER_NODES:
                if node_url != request.remote_addr:
                    try:
                        headers = {"Content-Type": "application/json"}
                        requests.post(node_url+":"+PORT+"/txion",json = new_txion,headers = headers)
                    except:
                        pass
            return "Transaction submission successful\n"
        else:
            return "Transaction submission failed. Wrong signature\n"
    # Send pending transactions to the mining process
    elif request.method == 'GET' and request.args.get("update") == user.public_key:
        pending = json.dumps(NODE_PENDING_TRANSACTIONS)
        # Empty transaction list
        NODE_PENDING_TRANSACTIONS[:] = []
        return pending


@node.route('/balances', methods=['GET'])
def get_balance():
    global BLOCKCHAIN
    working = BLOCKCHAIN
    balances = {}
    balances_json = []

    for block in working:
        if block.data['transactions'] is not None:
            for transaction in block.data['transactions']:
                to = transaction['to']
                source = transaction['from']
                amount = transaction['amount']

                if type(amount) == type("string"):
                    amount = eval(amount)

                if to in balances:
                    balances[to] += amount
                else:
                    balances[to] = amount
                if source != "network":
                    balances[source] -= amount

    for k, v in balances.items():
        account = {
            "address": str(k),
            "amount": str(v)
        }
        balances_json.append(account)

    return json.dumps(balances_json)


if __name__ == '__main__':
    welcome_msg()
    # Start mining
    a, b = Pipe()
    p1 = Process(target=mine, args=(a, BLOCKCHAIN, NODE_PENDING_TRANSACTIONS))
    p1.start()
    # Start server to receive transactions
    p2 = Process(target=node.run(host="0.0.0.0", port=PORT), args=b)
    p2.start()
