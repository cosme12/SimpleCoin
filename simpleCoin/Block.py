import hashlib
class Block():
    def __init__(self, index, timestamp, pow, effort,data, previous_hash):
        """Returns a new Block object. Each block is "chained" to its previous
        by calling its unique hash.

        Args:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            data (dict): Data to be sent.
            previous_hash(str): String representing previous block unique hash.

        Attrib:
            index (int): Block number.
            timestamp (int): Block creation timestamp.
            data (dict): Data to be sent.
            previous_hash(str): String representing previous block unique hash.
            hash(str): Current block unique hash.

        """
        self.index = index
        self.timestamp = timestamp

        self.proof_of_work = pow
        self.effort = effort
        self.data = data
        '''
        data contains:
         transactions: list
        '''
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        """Creates the unique hash for the block. It uses sha256."""
        m = hashlib.sha256()
        m.update((str(self.index) + str(self.timestamp) +str(self.proof_of_work)+ str(self.effort) + str(self.data) + str(self.previous_hash)).encode('utf-8'))
        return m.hexdigest()



    def __repr__(self):
        #def __init__(self, index, timestamp, pow, effort,data, previous_hash):
        return "Block({},{},'{}','{}',{},'{}')".format(self.index,self.timestamp,self.proof_of_work,self.effort,self.data,self.previous_hash)

    def __str__(self):
        return "i: {} time: {} \tpow: {} effort: {} data: {} \tprevious: {} hash: {}".format(self.index, self.timestamp,self.proof_of_work, self.effort, self.data, self.previous_hash, self.hash)

def buildpow(index,timestamp,effort,data,previous_hash):
    m = hashlib.sha256()
    m.update((str(index) + str(timestamp) + str(effort) + str(data) + str(previous_hash)).encode('utf-8'))
    return m
def validate(block):
    pow = buildpow(block.index,block.timestamp,block.effort,block.data,block.previous_hash)
    if block.proof_of_work == pow.hexdigest():
        return True