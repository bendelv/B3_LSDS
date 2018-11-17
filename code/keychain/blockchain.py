"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import time

class Block:
    def __init__(self, timestamp, transactions, previousHash = ""):
        """Describe the properties of a block."""
        self._timestamp = timestamp
        self._transactions = transactions
        self._previousHash = previousHash
        self._nonce = 0
        self._hash = self.compute_hash()

    def set_previous_hash(self, hash):
        self._previousHash = hash

    def get_previous_hash(self):
        return self._previousHash

    def get_hash(self):
        return self._hash

    def refresh_hash(self):
        self._hash = self.compute_hash()

    def trans2str(self):
        myStr = ""
        for t in self._transactions:
            myStr += str(t)
        return myStr

    def compute_hash(self):
        """Compute hash value of the current block"""
        hashString = str(self._timestamp) + self.trans2str()\
                     + self._previousHash + str(self._nonce)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine_block(self, difficulty):
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.compute_hash()

    def proof(self):
        """Return the proof of the current block."""
        raise NotImplementedError

    def transactions(self):
        """Returns the list of transactions associated with this block."""
        return self._transactions

    def __str__(self):
        return "*"*25 + "\ntimestamp: " + str(self._timestamp)\
               + "\ntransaction:\n" + self.trans2str()\
               + "\nPrevious hash: " + self._previousHash\
               + "\nHash: " + self._hash\
               + "\nnonce: " + str(self._nonce) + "\n" + "*"*25

# TODO transaction are the key-value stored in our blockchain, we need to change
# data in the constructor of a block ot a transaction/set of transactions.
class Transaction:
    def __init__(self, origin, key, value):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self._origin = origin
        self._key = key
        self._value = value

    def __str__(self):
        return "\torigin: " + self._origin\
               + "\n\tkey: " + str(self._key)\
               + "\n\tvalue: " + self._value + "\n"

class Peer:
    def __init__(self, address):
        """Address of the peer.

        Can be extended if desired.
        """
        self._address = address


class Blockchain:
    def __init__(self, bootstrap, difficulty):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        addres, download the peerlist, and start the bootstrapping procedure.
        """
        # Initialize the properties.
        self._difficulty = difficulty
        self._blocks = [self._add_genesis_block()]
        self._transactionBuffer = []
        #self._peers = []


        # Bootstrap the chain with the specified bootstrap address.
        #self._bootstrap(bootstrap)

    def __str__(self):
        for block in self._blocks:
            print(block)
        return ""

    def last_element(self):
        return self._blocks[len(self._blocks) - 1]

    def _add_genesis_block(self):
        genTrans = Transaction("none", None, "")
        genBlock = Block(time.time(), [genTrans], "0")
        genBlock.mine_block(self._difficulty)
        return genBlock

    def _bootstrap(self, address):
        """Implements the bootstrapping procedure."""
        peer = Peer(address)
        raise NotImplementedError

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.

        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        # TODO broadcasts the buffer
        self._transactionBuffer.append(transaction)

    def mine(self):
        """Implements the mining procedure."""
        #We should block any procces attemding to write a new transaction in the
        # transactions set.
        newBlock = Block(time.time(), self._transactionBuffer.copy())
        self._transactionBuffer = []
        newBlock.set_previous_hash(self.last_element().get_hash())
        newBlock.mine_block(self._difficulty)
        self._blocks.append(newBlock)

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        for i in range(1, len(self._blocks)):
            current = self._blocks[i]
            prev = self._blocks[i - 1]
            # check if the current hash pointer points to the correct element
            if current.get_previous_hash() != prev.compute_hash():
                return False
            # check is the node hasn't been modified
            if current.get_hash() != current.compute_hash():
                return False
        return True


def main():
    blockchain = Blockchain("bootstrap", 3)
    print(blockchain)
    blockchain.add_transaction(Transaction("pierre", 2, "some value 1"))
    blockchain.add_transaction(Transaction("pierre", 3, "some value 2"))
    blockchain.add_transaction(Transaction("pierre", 4, "some value 3"))
    blockchain.add_transaction(Transaction("pierre", 2, "some other value"))
    blockchain.mine()
    print(blockchain)
    #newBlock.set_previous_hash("some hash value")
    #print(blockchain.is_valid())

if __name__ == "__main__":
    main()
