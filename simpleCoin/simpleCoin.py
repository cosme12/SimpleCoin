import time
import hashlib as hasher
import json
import requests
from flask import Flask
from flask import request
from multiprocessing import Process

from miner_config import MINER_ADDRESS, PEER_NODES

node = Flask(__name__)


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
    return Block(0, time.time(), 
        {"proof-of-work": 9,"transactions": None},
         "0")


# Node's blockchain copy
BLOCKCHAIN = []
BLOCKCHAIN.append(create_genesis_block())

# Store the transactions that this node has, in a list
#global NODE_PENDING_TRANSACTIONS
NODE_PENDING_TRANSACTIONS = []


def proof_of_work(last_proof,blockchain):
  # Create a variable that we will use to find our next proof of work
  incrementor = last_proof + 1
  # Get start time
  start_time = time.time()
  # Keep incrementing the incrementor until it's equal to a number divisible by 9
  # and the proof of work of the previous block in the chain
  while not (incrementor % 7919 == 0 and incrementor % last_proof == 0):
    incrementor += 1
    start_time = time.time()
    # Check if any node found the solution every 60 seconds
    if (int((time.time()-start_time)%60)==0):
        # If any other node got the proof, stop searching
        new_blockchain = consensus(blockchain)
        if new_blockchain != False:
            #(False:another node got proof first, new blockchain)
            return (False,new_blockchain)
  # Once that number is found, we can return it as a proof of our work
  return (incrementor,blockchain)


def mine(blockchain,node_pending_transactions):
    BLOCKCHAIN = blockchain
    NODE_PENDING_TRANSACTIONS = node_pending_transactions
    while True:
        #print("start mining")
        """Mining is the only way that new coins can be created.
        In order to prevent to many coins to be created, the process
        is slowed down by a proof of work algorithm.
        """
        # Get the last proof of work
        last_block = BLOCKCHAIN[len(BLOCKCHAIN) - 1]
        last_proof = last_block.data['proof-of-work']
        # Find the proof of work for the current block being mined
        # Note: The program will hang here until a new proof of work is found
        proof = proof_of_work(last_proof, BLOCKCHAIN)
        # If we didn't guess the proof, start mining again
        if proof[0] == False:
            # Update blockchain and save it to file
            BLOCKCHAIN = proof[1]
            save_to_file(0,BLOCKCHAIN)
            continue
        else:
            # Once we find a valid proof of work, we know we can mine a block so 
            # we reward the miner by adding a transaction
            NODE_PENDING_TRANSACTIONS.append(
            { "from": "network",
              "to": MINER_ADDRESS,
              "amount": 1 }
            )
            # Now we can gather the data needed to create the new block
            new_block_data = {
            "proof-of-work": proof[0],
            "transactions": list(NODE_PENDING_TRANSACTIONS)
            }
            new_block_index = last_block.index + 1
            new_block_timestamp = time.time()
            last_block_hash = last_block.hash
            # Empty transaction list
            NODE_PENDING_TRANSACTIONS[:] = []
            # Now create the new block
            mined_block = Block(new_block_index, new_block_timestamp, new_block_data, last_block_hash)
            BLOCKCHAIN.append(mined_block)
            # Let the client know this node mined a block
            #print("end mined")
            print(json.dumps({
              "index": new_block_index,
              "timestamp": str(new_block_timestamp),
              "data": new_block_data,
              "hash": last_block_hash
            }) + "\n")
            #save_to_file(0,BLOCKCHAIN)


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

def consensus(blockchain):
    # Get the blocks from other nodes
    other_chains = find_new_chains()
    # If our chain isn't longest, then we store the longest chain
    BLOCKCHAIN = blockchain
    longest_chain = BLOCKCHAIN
    for chain in other_chains:
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

'''
def save_to_file(mode,data):
    """Use mode == 0 to save blockchain
    Use mode == 1 to save pending transactions"""
    if mode == 0:
        print(data)
        with open("BLOCKCHAIN.json", "w") as file:
            json.dump(data,file)
    if mode == 1:
        with open("PENDING_TXION.txt", "w") as file:
            text_file.write(data)

def read_file():
    """Read current blockchain"""
    with open("BLOCKCHAIN.json", "w") as file:
        return(json.loads(file.read()))
'''

@node.route('/blocks', methods=['GET'])
def get_blocks():
    # Load current blockchain
    #chain_to_send = read_file()
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

    print(chain_to_send)
    # Send our chain to whomever requested it
    chain_to_send = json.dumps(chain_to_send_json)
    return chain_to_send


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
        #global NODE_PENDING_TRANSACTIONS
        NODE_PENDING_TRANSACTIONS.append(new_txion)
        # Because the transaction was successfully
        # submitted, we log it to our console
        print("New transaction")
        print("FROM: {0}".format(new_txion['from']))
        print("TO: {0}".format(new_txion['to']))
        print("AMOUNT: {0}\n".format(new_txion['amount']))
        # Then we let the client know it worked out
        return "Transaction submission successful\n"


if __name__ == '__main__':
    #Start mining
    p1 = Process(target = mine(BLOCKCHAIN,NODE_PENDING_TRANSACTIONS))
    p1.start()
    #Start server to recieve transactions
    p2 = Process(target = node.run())
    p2.start()