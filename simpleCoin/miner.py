import time
import hashlib
import sys
import json
import requests
import os
import secrets
import string
import base64
from flask import Flask, request
from multiprocessing import Process, Queue
import ecdsa
import secrets
import string
import logging
import simpleCoin.user as user
from simpleCoin.Block import Block,buildpow
from simpleCoin.miner_config import MINER_NODE_URL, PEER_NODES, PORT

try:
    assert user.public_key != "" and user.private_key != ""
except AssertionError:
    print("You need to generate keys in your wallet")
    sys.exit()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

node = Flask(__name__)
node.config['SECRET_KEY'] = user.secret_key

work = 14
try:
    assert work > 0 and work < 65
except AssertionError:
    print("Work value must be greater than 0 and less than 65")


def create_genesis_block():
    """To create each block, it needs the hash of the previous one. First
    block has no previous, so it must be created manually (with index zero
     and arbitrary previous hash)"""
    global work
    work_ez = int(work / 4) + 1
    pow = "0" * work_ez
    pad = "1337"
    for i in range(4, 64):
        pow += pad[i % len(pad)]
    b = Block(0, time.time(), pow, "e", {
        "transactions": None},
              "0")
    return b


# Node's blockchain copy

""" Stores the transactions that this node has in a list.
If the node you sent the transaction adds a block
it will get accepted, but there is a chance it gets
discarded and your transaction goes back as if it was never
processed"""
NODE_PENDING_TRANSACTIONS = []

BLOCKCHAIN = [create_genesis_block()]
# print("b0 =",repr(BLOCKCHAIN[0]))
# print("#",BLOCKCHAIN[0])
def proof_of_work(last_block, data):

    new_block_index = last_block.index + 1
    new_block_timestamp = time.time()

    NODE_PENDING_TRANSACTIONS = []


    def random_str():
        # Generate a random size string from 3 - 27 characters long
        rand_str = ''
        for i in range(0, 1 + secrets.randbelow(25)):
            rand_str += string.ascii_lowercase[secrets.randbelow(26)]  # each char is a random downcase letter [a-z]
        return rand_str

    def genhash():
        effort = random_str()
        return effort, buildpow(new_block_index,new_block_timestamp,effort,data,last_block.hash)

    def leadingzeroes(digest):
        n = 0
        result = ''.join(format(x, '08b') for x in bytearray(digest))
        for c in result:
            if c == '0':
                n += 1
            else:
                break
        return n

    effort, pow_hash = genhash()
    start_time = time.time()
    global work
    lead = leadingzeroes(pow_hash.digest())
    while lead < work:

        # Check if any node found the solution every 60 seconds
        if int((time.time() - start_time) % 60) == 0:
            # If any other node got the proof, stop searching
            new_blockchain = consensus()
            if new_blockchain:
                # (False: another node got proof first, new blockchain)
                return False, new_blockchain
        # generate new hash for next time
        effort, pow_hash = genhash()
        lead = leadingzeroes(pow_hash.digest())

    # Once that hash is found, we can return it as a proof of our work
    mined_block = Block(new_block_index, new_block_timestamp, pow_hash.hexdigest(),effort, data, last_block.hash)
    return True, mined_block


def mine(a, blockchain, node_pending_transactions):
    global BLOCKCHAIN
    global work
    NODE_PENDING_TRANSACTIONS = node_pending_transactions
    while True:
        """Mining is the only way that new coins can be created.
        In order to prevent too many coins to be created, the process
        is slowed down by a proof of work algorithm.
        """
        # Get the last proof of work
        last_block = BLOCKCHAIN[len(BLOCKCHAIN) - 1]

        NODE_PENDING_TRANSACTIONS = requests.get(
            "http://" + MINER_NODE_URL + ":" + str(PORT) + "/txion?update=" + user.public_key).content
        NODE_PENDING_TRANSACTIONS = json.loads(NODE_PENDING_TRANSACTIONS)

        # Then we add the mining reward
        NODE_PENDING_TRANSACTIONS.append({
            "from": "network",
            "to": user.public_key,
            "amount": 1.0})

        new_block_data = {"transactions": list(NODE_PENDING_TRANSACTIONS)}
        proof = proof_of_work(last_block, new_block_data)
        if not proof[0]:
            BLOCKCHAIN = proof[1]
            a.put(BLOCKCHAIN)
            continue
        else:
            mined_block = proof[1]

            '''
            String
            '''
            # print("#",mined_block)
            '''
            String
            '''
            '''
            REPR
            '''
            # print("b{} = ".format(mined_block.index), repr(mined_block))
            # if last_block.index == 1:
            #     print('work = {}'.format(work))
            #     print("blockchain = [", end="")
            #     for i in range(0, len(BLOCKCHAIN)+1):
            #         print("b{}".format(i), end=",")
            #     print("]")
            #     sys.exit()

            '''
            END REPR
            '''
            BLOCKCHAIN.append(mined_block)
            a.put(BLOCKCHAIN)
            requests.get("http://" + MINER_NODE_URL + ":" + str(PORT) + "/blocks?update=" + user.public_key)


def find_new_chains():
    # TODO maybe check the length of nodes before just downloading one at random.
    # TODO also if it fails validation, I never want to use that person again.
    # Get the blockchains of every other node
    other_chains = []
    for node_url in PEER_NODES:
        blockchains = None
        try:
            blockchains = requests.get(node_url + ":" + PORT + "/blocks").content
        except:
            pass
        # Convert the JSON object to a Python dictionary
        if blockchains is not None:
            blockchains = json.loads(blockchains)
            # Verify other node block is correct
            validated = validate_blockchain(blockchains)
            if validated:
                other_chains.append(blockchains)
    return other_chains


def consensus():
    # TODO I should look at the hashes of my coins versus there's and then only validate when they differ
    if len(PEER_NODES) == 0:
        return False
    global BLOCKCHAIN
    # Get the blocks from other nodes
    other_chains = find_new_chains()
    # If our chain isn't longest, then we store the longest chain
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
            m = hashlib.sha256()
            # m.update((str(last_block.index) + str(last_block.timestamp) + str(data) + str(last_block.previous_hash)).encode('utf-8'))
            m.update(
                (str(block.index) + str(block.timestamp) + str(block.data) + str(block.previous_hash)).encode('utf-8'))
            if m.hexdigest() != block.hash:
                return False
            if previous != block.previous_hash:
                return False
            previous = block.hash

    return True


def validate_signature(public_key, signature, message):
    # global BLOCKCHAIN
    # if BLOCKCHAIN[len(BLOCKCHAIN) - 1].index > 0:
    #     print("verify_signature")
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
    global BLOCKCHAIN
    # if BLOCKCHAIN[len(BLOCKCHAIN) - 1].index > 0:
    #     print("get_blocks")
    # Load current blockchain. Only you should update your blockchain
    if request.args.get("update") == user.public_key:
        # print("updating /blocks")
        if not a.empty():
            # print("b was not empty")
            BLOCKCHAIN = a.get()
    chain_to_send = BLOCKCHAIN
    # Converts our blocks into dictionaries so we can send them as json objects later
    chain_to_send_json = []
    for block in chain_to_send:
        chain_to_send_json.append(block.exportjson())

    # Send our chain to whomever requested it
    ip = request.remote_addr + ":" + str(PORT)
    if str(ip) != "127.0.0.1" and ip not in PEER_NODES:
        PEER_NODES.append(ip)
    chain_to_send = json.dumps(chain_to_send_json)
    return chain_to_send


@node.route('/txion', methods=['GET', 'POST'])
def transaction():
    # global BLOCKCHAIN
    # if BLOCKCHAIN[len(BLOCKCHAIN) - 1].index > 0:
    # print("transaction")

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

            # Push to all other available nodes
            for node_url in PEER_NODES:
                if node_url != request.remote_addr:
                    try:
                        headers = {"Content-Type": "application/json"}
                        requests.post(node_url + ":" + PORT + "/txion", json=new_txion, headers=headers)
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
    # if BLOCKCHAIN[len(BLOCKCHAIN) - 1].index > 0:
    #     print("Balances")
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
    a = Queue()
    p1 = Process(target=mine, args=(a, BLOCKCHAIN, NODE_PENDING_TRANSACTIONS))
    p1.start()
    # Start server to receive transactions
    p2 = Process(target=node.run(host="0.0.0.0", port=PORT), args=a)
    p2.start()
