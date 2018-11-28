"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import time
from queue import Queue
import sys
from operator import attrgetter
import json

class MerkleLeaf:
    def __init__(self, transaction):
        self._transaction = transaction
        self._prefixes = self.compute_prefixes()
        self._nonce = 0
        self._hash = self.compute_hash()

    def get_hash(self):
        return self._hash

    def get_transaction(self):
        return self._transaction

    def compute_prefixes(self):
        return [str(self._transaction.get_key()),str(self._transaction.get_key())]

    def compute_hash(self):
        hashString = str(self._transaction) + str(self._nonce)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine(self, difficulty):
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.compute_hash()

    def __str__(self):
        myStr = "\t\tPrefix: " + self._prefixes[0] + " " + self._prefixes[1]\
                + "\n\t\t" + str(self._transaction)
        return myStr

    def is_valid(self):
        if self._hash != self.compute_hash():
            return False
        return True

    def in_tree(self, key, get=False, all=None):
        if get:
            if self._transaction.get_key() == key:
                if all is None:
                    return True, self._transaction
                else:
                    all.append(self._transaction)
                    return all
            else:
                if all is None:
                    return False, None
                else:
                    return all
        else:
            return self._transaction.get_key() == key

    def toJson(self):
        dict = {}
        dict["hash"] = self._hash
        dict["prefixes"] = self._prefixes
        dict["transaction"] = self._transaction.toJson()
        dict['nonce'] = self._nonce
        return dict

class MerkleNode:
    def __init__(self, left, right):
        self._left = left
        self._right = right
        self._leftHash = left.get_hash()
        self._rightHash = right.get_hash()
        self._prefixes = self.compute_prefixes()
        self._nonce = 0
        self._hash = self.compute_hash()

    def get_hash(self):
        return self._hash

    def compute_prefixes(self):

        return [self.compute_left_prefix(self._left._prefixes[0],
                                         self._right._prefixes[0]),
                self.compute_right_prefix(self._left._prefixes[1],
                                          self._right._prefixes[1])
               ]

    def compute_right_prefix(self, left, right):
        sorted_prefix = sorted([left, right])
        return sorted_prefix[1]

    def compute_left_prefix(self, left, right):
        if left == right:
            return left
        list = [left , right]
        smallest = min(list, key=len)
        longest = max(list, key=len)
        for i, c in enumerate(smallest):
            if c != longest[i]:
                return longest[:i]
        return smallest

    def compute_hash(self):
        hashString = self._left._hash + self._right._hash + str(self._nonce)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine(self, difficulty):
        self._left.mine(difficulty)
        self._right.mine(difficulty)
        self._leftHash = self._left.get_hash()
        self._rightHash = self._right.get_hash()
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.compute_hash()

    def __str__(self):
        myStr = "Common prefix : " + str(self._prefixes)\
                + "\nPrefix left : " + str(self._left._prefixes)\
                + "\n\t\t " + str(self._left)\
                + "\nPrefix right : " + str(self._right._prefixes)\
                + ":\n\t\t " + str(self._right) + "\n"
        return myStr

    def is_valid(self):
        if self.get_hash() != self.compute_hash():
            return False
        if self._leftHash != self._left.get_hash():
            return False
        if self._rightHash != self._right.get_hash():
            return False
        else:
            return self._left.is_valid() and self._right.is_valid()

    def in_tree(self, key, get=False, all=None):
        if get:
            if all is None:
                is_inside_l, trans_l = self._left.in_tree(key, get, all)
                is_inside_r, trans_r = self._right.in_tree(key, get, all)
                if is_inside_l:
                    return True, trans_l
                elif is_inside_r:
                    return True, trans_r
                else:
                    return True, None
            else:
                all = self._left.in_tree(key, get, all)
                all = self._right.in_tree(key, get, all)
                return all

        else:
            is_inside = self._left.in_tree(key, get) or self._right.in_tree(key, get, all)
            if is_inside:
                return True
            else:
                return False

        smallest = self.compute_left_prefix(self._prefixes[0], key, all)
        largest = self.compute_right_prefix(self._prefixes[1], key, all)
        #if the key is inbetween the two keyes
        if largest == self._prefixes[1] and smallest == self._prefixes[0]:
            if get:
                if all is not None:
                    is_inside_left, trans_left = self._left.in_tree(key, get, all)
                    is_inside_right, trans_right = self._right.in_tree(key, get, all)
                    if trans_left is not None:
                        return True, trans_left
                    if trans_right is not None:
                        return True, trans_right
                    return False, None
            return self._left.in_tree(key, get, all) or self._right.in_tree(key, get, all)

    def toJson(self):
        dict = {}
        dict['hash'] = self._hash
        dict['prefixes'] = self._prefixes
        dict['Left Hash'] = self._leftHash
        dict['Left'] = self._left.toJson()
        dict['Right Hash'] = self._rightHash
        dict['Right'] = self._right.toJson()
        dict['nonce'] = self._nonce
        return dict

class MerkleTree:
    def __init__(self, transactions):
        self.one = False
        if len(transactions) > 1:
            self._tree = self.buildMT(transactions.copy())
        else:
            self._tree = MerkleLeaf(transactions[0])
            self.one = True
        self._hash = self._tree.get_hash()

    def get_hash(self):
        return self._hash

    def buildMT(self, transactions):
        #first we sort the merkleTree
        transactions = sorted(transactions, key=attrgetter('_key'))
        transactions= sorted(transactions, key=attrgetter('_timestamp'), reverse=True)
        to_process = Queue()
        jump_next = False
        for i, transaction in enumerate(transactions):
            if jump_next:
                jump_next = False
            else:
                self.leftHash = MerkleLeaf(transaction)
                self.rightHash = None
                if i < len(transactions) - 1:
                    self.rightHash = MerkleLeaf(transactions[i+1])
                if self.rightHash is not None:
                    to_process.put([self.leftHash, self.rightHash])
                else:
                    to_process.put([self.leftHash])
                jump_next = True

        tree = None
        while not to_process.empty():
            list1 = to_process.get()
            #last node to process
            if to_process.empty():
                if len(list1) > 1:
                    tree = MerkleNode(list1[0], list1[1])
                else:
                    tree = list1[0]
                break

            list2 = to_process.get()


            if len(list1) > 1 and len(list2) > 1:
                to_process.put([MerkleNode(list1[0], list1[1]), MerkleNode(list2[0], list2[1])])
            elif len(list1) > 1:
                next = MerkleNode(list1[0], list1[1])
                to_process.put([next, list2[0]])
            elif len(list2) > 1:
                next = MerkleNode(list2[0], list2[1])
                to_process.put([list1[0], next])
            else:
                to_process.put([list1[0], list2[0]])

        return tree

    def __str__(self):
        myStr = "prefxes :" + str([str(x) + " " for x in self._tree._prefixes]) + "\n"
        myStr += "hash :" + self._tree._hash + "\n"
        if self.one:
            myStr += str(self._tree)
        else:
            myStr += str(self._tree._left)\
                + str(self._tree._right)
        return myStr

    def mine(self, difficulty):
        self._tree.mine(difficulty)
        self._hash = self._tree.get_hash()

    def is_valid(self):
        if self._hash != self._tree.get_hash():
            return False
        return self._tree.is_valid()

    def is_inside(self, key, get=False, all=None):
        return self._tree.in_tree(key, get, all)

    def toJson(self):
        dict = {}
        dict['hash'] = self._hash
        dict['transactions'] = self._tree.toJson()
        return dict

class Transaction:
    def __init__(self, origin, key, value):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self._origin = origin
        self._key = key
        self._value = value
        self._timestamp = time.time()

    def get_key(self):
        return self._key

    def get_timestamp(self):
        return self._timestamp

    def __str__(self):
        return "\torigin: " + self._origin\
               + "\n\tkey: " + str(self._key)\
               + "\n\tvalue: " + self._value\
               + "\n\ttimestamp: " + str(self._timestamp) + "\n"

    def toJson(self):
        dict = {}
        dict["Origin"] = self._origin
        dict["Key"] = self._key
        dict["Value"] = self._value
        dict["timestamp"] = self._timestamp
        return dict


class Peer:
    def __init__(self, address):
        """Address of the peer.

        Can be extended if desired.
        """
        self._address = address



class Block:
    def __init__(self, timestamp, transactions, previousHash = ""):
        """Describe the properties of a block."""
        self._timestamp = timestamp
        if transactions is None:
            self._transactions = transactions
        else:
            self._transactions = MerkleTree(transactions)
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

    def compute_hash(self):
        """Compute hash value of the current block"""
        hashString = str(self._timestamp) + str(self._transactions)\
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

    def is_valid(self):
        return self._transactions.is_valid()

    def __str__(self):
        return "*"*25 + "\ntimestamp: " + str(self._timestamp)\
               + "\ntransaction:\n" + str(self._transactions)\
               + "\nPrevious hash: " + self._previousHash\
               + "\nHash: " + self._hash\
               + "\nnonce: " + str(self._nonce) + "\n" + "*"*25

    def is_inside(self, key, get=False, all=None):
        return self._transactions.is_inside(key, get, all)

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
        myStr = ""
        for block in self._blocks:
            myStr = myStr + "\n" + "="*25 + "\n" + str(block) + "\n" + "="*25 + "\n"
        return myStr

    def last_element(self):
        return self._blocks[len(self._blocks) - 1]

    def _add_genesis_block(self):
        genTrans = Transaction("none", None, "")
        genBlock = Block(time.time(), [genTrans], "0")
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
            if not current.is_valid():
                return False
            if current.get_previous_hash() != prev.compute_hash():
                return False
            # check is the node hasn't been modified
            if current.get_hash() != current.compute_hash():
                return False
        return True

    def is_inside(self, key, get=False, all=None):
        for i in reversed(range(len(self._blocks))):
            if all is None:
                new_all = None
            else:
                new_all = []
            current = self._blocks[i]
            resutl = current.is_inside(key, get, new_all)
            if get:
                if all is None:
                    if resutl[0]:
                        return resutl[1]
                    else:
                        return None
                else:
                    for res in resutl:
                        all.append(res)
            else:
                return resutl
        return all

def main():

    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    #dict = t1.toJson()
    #print(json.dumps(dict, indent = 4))
    #leaf = MerkleLeaf(t1)
    #dict = leaf.toJson()
    #print(json.dumps(dict, indent = 4))




    transactionBuffer.append(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    transactionBuffer.append(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    transactionBuffer.append(t3)
    transactionBuffer2 = []
    t21 = Transaction("pierre4", "key4", "some value set to 0")
    transactionBuffer2.append(t21)
    t22 = Transaction("pierre5", "key4", "some key value")
    transactionBuffer2.append(t22)
    t23 = Transaction("pierre6", "key44", "some other value")
    transactionBuffer2.append(t23)
    merkleTree = MerkleTree(transactionBuffer2)

    dict = merkleTree.toJson()
    print(json.dumps(dict, indent = 4))
    sys.exit()

    print(merkleTree.is_inside("key44"))
    print(merkleTree.is_inside("key442"))
    print(merkleTree.is_inside("key4"))
    print(merkleTree.is_inside("key4", True)[1])
    print(merkleTree.is_inside("key"))
    print(merkleTree.is_inside("key4", True)[1])
    all = merkleTree.is_inside("key4", True, [])
    for a in all:
        print(a)
    print(merkleTree.is_valid())
    t1._key = "mouahahah"
    print(merkleTree.is_valid())


    blockchain = Blockchain("bootstrap", 3)
    blockchain.add_transaction(t1)
    blockchain.add_transaction(t2)
    blockchain.add_transaction(t3)
    blockchain.mine()
    blockchain.add_transaction(t21)
    blockchain.add_transaction(t22)
    blockchain.add_transaction(t23)
    blockchain.mine()
    print("*"*25)
    print("contains")
    print(blockchain.is_inside("key4"))
    print("GET")
    print(blockchain.is_inside("key44", True))
    print("ALL")
    all = blockchain.is_inside("key4", True, [])
    for a in all:
        print(a)
    print("*"*25)

    #newBlock.set_previous_hash("some hash value")
    #print(blockchain.is_valid())

if __name__ == "__main__":
    main()
