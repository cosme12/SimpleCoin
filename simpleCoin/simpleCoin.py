"""TODO LIST

validate other_chains in find_new_chains(): they must be a well created chains,
this prevent attacks that attemp to completly change the blockchain history

stop proof_of_work() if someonelse already got it: doing some research about it

improve proof_of_work() algorithm: make is harder to guess

add PEER_NODES dinamically

create wallet generator and user client

add POST and GET request in this script

verify transactions to avoid no funds or duplicate sent

"""
import datetime as date
import hashlib as hasher
import json
import requests
from flask import Flask
from flask import request

node = Flask(__name__)

# Write your generated adress here. All coins mined will go to this address
MINER_ADDRESS = "q3nf394hjg-random-miner-address-34nf3i4nflkn3oi"

# Node's blockchain copy
BLOCKCHAIN = []
BLOCKCHAIN.append(create_genesis_block())

# Store the url data of every other node in the network
# so that we can communicate with them
PEER_NODES = []

# Store the transactions that this node has in a list
NODE_PENDING_TRANSACTIONS = []



class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        """Return a new Block object. Each block is "chained" to it's previous
        by calling it's unique hash.

        Args:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            data (str): Data to be sent.
            previous_hash(str): String representing previous block unique hash.

        Attrib:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            data (str): Data to be sent.
            previous_hash(str): String representing previous block unique hash.
            hash(str): Current block unique hash.

        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()
  
    def hash_block(self):
        """Creates the unique hash for the block. It uses sha256."""
        sha = hasher.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode('utf-8'))
        return sha.hexdigest()

def create_genesis_block():
    """To create each block, it needs the hash of the previous one. First
    block has no previous, so it must be created manually (with index zero
     and arbitrary previous hash)"""
    return Block(0, date.datetime.now(), 
        {"proof-of-work": 9,"transactions": None},
         "0")


def next_block(last_block):
    """Creates next block"""
    this_index = last_block.index + 1
    this_timestamp = date.datetime.now()
    this_data = "Hey! I'm block " + str(this_index)
    this_hash = last_block.hash
    return Block(this_index, this_timestamp, this_data, this_hash)


@node.route('/txion', methods=['POST'])
def transaction():
    """Each transaction sent to this node gets validated and submitted.
    Then it waits to be added to the blockchain. Transactions only move
    coins, they don't create it.
    """
    if request.method == 'POST':
        # On each new POST request,
        # we extract the transaction data
        new_txion = request.get_json()
        # Then we add the transaction to our list
        NODE_PENDING_TRANSACTIONS.append(new_txion)
        # Because the transaction was successfully
        # submitted, we log it to our console
        print("New transaction")
        print("FROM: {0}".format(new_txion['from']))
        print("TO: {0}".format(new_txion['to']))
        print("AMOUNT: {0}\n".format(new_txion['amount']))
        # Then we let the client know it worked out
        return "Transaction submission successful\n"


def proof_of_work(last_proof):
  # Create a variable that we will use to find our next proof of work
  incrementor = last_proof + 1
  # Keep incrementing the incrementor until it's equal to a number divisible by 9
  # and the proof of work of the previous block in the chain
  while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
    incrementor += 1
  # Once that number is found, we can return it as a proof of our work
  return incrementor


@node.route('/mine', methods = ['GET'])
def mine():
    """Mining is the only way that new coins can be created.
    In order to prevent to many coins to be created, the process
    is slowed down by a proof of work algorithm.
    """
    # Get the last proof of work
    last_block = BLOCKCHAIN[len(BLOCKCHAIN) - 1]
    last_proof = last_block.data['proof-of-work']
    # Find the proof of work for the current block being mined
    # Note: The program will hang here until a new proof of work is found
    proof = proof_of_work(last_proof)
    # Once we find a valid proof of work, we know we can mine a block so 
    # we reward the miner by adding a transaction
    NODE_PENDING_TRANSACTIONS.append(
    { "from": "network",
      "to": MINER_ADDRESS,
      "amount": 1 }
    )
    # Now we can gather the data needed to create the new block
    new_block_data = {
    "proof-of-work": proof,
    "transactions": list(NODE_PENDING_TRANSACTIONS)
    }
    new_block_index = last_block.index + 1
    new_block_timestamp = this_timestamp = date.datetime.now()
    last_block_hash = last_block.hash
    # Empty transaction list
    NODE_PENDING_TRANSACTIONS[:] = []
    # Now create the new block
    mined_block = Block(
    new_block_index,
    new_block_timestamp,
    new_block_data,
    last_block_hash
    )
    BLOCKCHAIN.append(mined_block)
    # Let the client know this node mined a block
    return json.dumps({
      "index": new_block_index,
      "timestamp": str(new_block_timestamp),
      "data": new_block_data,
      "hash": last_block_hash
    }) + "\n"


@node.route('/blocks', methods=['GET'])
def get_blocks():
    chain_to_send = BLOCKCHAIN
    # Convert our blocks into dictionaries
    # so we can send them as json objects later
    chain_to_send_json = []
    for block in chain_to_send:
        block = {
            "index": str(block.index),
            "timestamp": str(block.timestamp),
            "data": str(block.data),
            "hash": block.hash
        }
        chain_to_send_json.append(block)

    print(chain_to_send_json)
    # Send our chain to whomever requested it
    chain_to_send = json.dumps(chain_to_send_json)
    return chain_to_send

def find_new_chains():
    # Get the blockchains of every other node
    other_chains = []
    for node_url in PEER_NODES:
        # Get their chains using a GET request
        block = requests.get(node_url + "/blocks").content
        # Convert the JSON object to a Python dictionary
        block = json.loads(block)
        # Add it to our list
        other_chains.append(block)
    return other_chains

def consensus():
    # Get the blocks from other nodes
    other_chains = find_new_chains()
    # If our chain isn't longest, then we store the longest chain
    longest_chain = BLOCKCHAIN
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            longest_chain = chain
    # If the longest chain wasn't ours, then we set our chain to the longest
    BLOCKCHAIN = longest_chain


node.run()
