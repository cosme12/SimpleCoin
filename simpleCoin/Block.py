import hashlib
class Block:
    def __init__(self, index, timestamp, effort, data, previous_hash):
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

        self.effort = effort
        self.data = data
        '''
        data contains:
         proof-of-work (str)
         transactions: (list?)

        '''
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        """Creates the unique hash for the block. It uses sha256."""
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode('utf-8'))
        return sha.hexdigest()

    def validate(self,effort):
        '''

        :param effort: number of digits of zero in proof of work
        :return: True or False if this block is valid
        '''
        if self.data['proof-of-work'][0:effort] != "0"*effort:
            return False
        return True

    def __repr__(self):
        return "Block({},{},'{}',{},'{}')".format(self.index,self.timestamp,self.effort,self.data,self.previous_hash)

    def __str__(self):
        return "i: {} time: {} effort: {} data: {} previous: {} hash: {}".format(self.index, self.timestamp, self.effort, self.data, self.previous_hash, self.hash)