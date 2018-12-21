"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import time
from queue import Queue
import sys
from operator import attrgetter
import pickle
import json
import argparse
from random import randint
from threading import Thread
import peer
import numpy as np


class Fakeapi:
    def __init__(self, bootstrap, bootsloc, miner, difficulty, transactionBuffer=None):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self._own = bootsloc
        self._bootstrap = bootstrap
        self._miner = miner
        self._blockchain = Blockchain(self,
                                      difficulty=difficulty,
                                      transactionBuffer=transactionBuffer)

    def isMiner(self):
        return self._miner

    def addTransaction(self, transaction):
        self._blockchain.addTransaction(transaction)


class Transaction:
    def __init__(self, key, value, timestamp=time.time()):
        """
        A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self._key = key
        self._value = value
        self._timestamp = timestamp

    @classmethod
    def fromJsonDict(cls, dict):
        return cls(dict['_key'], dict['_value'], dict['_timestamp'])

    def __str__(self):
        dict = self.getDict()
        return json.dumps(dict, indent = 4, sort_keys=True)

    def __eq__ (self, other):
        return self._key == other._key and\
               self._value == other._value and\
               self._timestamp == other._timestamp

    def toHtml(self):
        myStr = "<tr>"
        myStr += "<th>{}</th>".format(self._key)
        myStr += "<th>{}</th>".format(self._value)
        myStr += "<th>{}</th>".format(self._timestamp)
        myStr += "</tr>"
        return myStr

    def getDict(self):
        dict = {}
        dict["Key"] = self._key
        dict["Value"] = self._value
        dict["timestamp"] = self._timestamp
        return dict

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)

    def getKey(self):
        return self._key

    def getTimestamp(self):
        return self._timestamp


class MerkleLeaf:
    def __init__(self, transaction, prefixes=None, nonce=None, hash=None, genesis=False ,leaf=True):
        self._transaction = transaction
        if prefixes is not None:
            self._prefixes = prefixes
        else:
            self._prefixes = self.computePrefixes()

        if nonce is not None:
            self._nonce = nonce
        else:
            if genesis:
                self._nonce = 0
            else:
                self._nonce = randint(0, 1000)
        if hash is not None:
            self._hash = hash
        else:
            self._hash = self.computeHash()
        self._leaf = leaf

    @classmethod
    def fromJsonDict(cls, dict):
        return cls(Transaction.fromJsonDict(dict['_transaction']),
                   dict['_prefixes'],
                   dict['_nonce'],
                   dict['_hash'],
                   dict['_leaf'])

    def __str__(self):
        dict = {}
        dict["prefixes"] = self._prefixes
        dict["transaction"] = self._transaction.toJson()
        dict['nonce'] = self._nonce
        return json.dumps(dict, indent=4, sort_keys=True)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)

    def toHtml(self):
        return self._transaction.toHtml()

    def getHash(self):
        return self._hash

    def getTransaction(self):
        return self._transaction

    def computePrefixes(self):
        return [str(self._transaction.getKey()),str(self._transaction.getKey())]

    def computeHash(self):
        hashString = str(self)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine(self, difficulty):
        print("Start Mining leaf...")
        self._nonce = randint(0, 1000)
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.computeHash()
        print("leaf mined")

    def isValid(self):
        if self._hash != self.computeHash():
            print("LEAF")
            return False
        return True

    def inTree(self, key, get=False, all=None):
        if get:
            if self._transaction.getKey() == key:
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
            return self._transaction.getKey() == key

    def getTransactions(self):
        return [self._transaction]


class MerkleNode:
    def __init__(self, left, right, leftHash=None, rightHash=None, prefixes=None, nonce=None, hash=None, genesis=False):
        self._left = left
        self._right = right
        if leftHash is not None:
            self._leftHash = leftHash
        else:
            self._leftHash = left.getHash()

        if rightHash is not None:
            self._rightHash = rightHash
        else:
            self._rightHash = right.getHash()

        if prefixes is not None:
            self._prefixes = prefixes
        else:
            self._prefixes = self.computePrefixes()

        if nonce is not None:
            self._nonce = nonce
        else:
            if genesis:
                self._nonce = 0
            else:
                self._nonce = randint(0, 1000)

        if hash is not None:
            self._hash = hash
        else:
            self._hash = self.computeHash()
    @classmethod
    def fromJsonDict(cls, dict):
        dict_left = dict['_left']
        dict_right = dict['_right']
        leftHash = dict['_leftHash']
        rightHash = dict['_rightHash']
        prefixes = dict['_prefixes']
        nonce = dict['_nonce']
        hash = dict['_hash']

        if '_leaf' in dict_left.keys():
            left = MerkleLeaf.fromJsonDict(dict_left)

        else:
            left = MerkleNode.fromJsonDict(dict_left)

        if '_leaf' in dict_right.keys():
            right = MerkleLeaf.fromJsonDict(dict_right)
        else:
            right = MerkleNode.fromJsonDict(dict_right)
        return cls(left, right, leftHash, rightHash, prefixes, nonce, hash)

    def __str__(self):
        dict = {}
        dict['prefixes'] = self._prefixes
        dict['Left Hash'] = self._leftHash
        dict['Right Hash'] = self._rightHash
        dict['nonce'] = self._nonce
        return json.dumps(dict, indent=4, sort_keys=True)

    def toHtml(self):
        return self._left.toHtml() + self._right.toHtml()

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)

    def getHash(self):
        return self._hash

    def computePrefixes(self):

        return [self.computeLeftPrefix(self._left._prefixes[0],
                                         self._right._prefixes[0]),
                self.computeRightPrefix(self._left._prefixes[1],
                                          self._right._prefixes[1])
               ]

    def computeRightPrefix(self, left, right):
        sorted_prefix = sorted([left, right])
        return sorted_prefix[1]

    def computeLeftPrefix(self, left, right):
        if left == right:
            return left
        list = [left , right]
        smallest = min(list, key=len)
        longest = max(list, key=len)
        for i, c in enumerate(smallest):
            if c != longest[i]:
                return longest[:i]
        return smallest

    def computeHash(self):
        hashString = str(self)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine(self, difficulty):
        print("Start mining left node...")
        self._left.mine(difficulty)
        print("Left node mined")
        print("Start mining Right node...")
        self._right.mine(difficulty)
        print("Right node mined")
        self._leftHash = self._left.getHash()
        self._rightHash = self._right.getHash()
        self._nonce = randint(0, 1000)
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.computeHash()

    def getTransactions(self):
        return self._left.getTransactions() + self._right.getTransactions()

    def isValid(self):
        if self._hash != self.computeHash():
            return False
        if self._leftHash != self._left.getHash():
            return False
        if self._rightHash != self._right.getHash():
            return False
        else:
            return self._left.isValid() and self._right.isValid()

    def inTree(self, key, get=False, all=None):
        if get:
            if all is None:
                is_inside_l, trans_l = self._left.inTree(key, get, all)
                is_inside_r, trans_r = self._right.inTree(key, get, all)
                if is_inside_l:
                    return True, trans_l
                elif is_inside_r:
                    return True, trans_r
                else:
                    return True, None
            else:
                all = self._left.inTree(key, get, all)
                all = self._right.inTree(key, get, all)
                return all

        else:
            is_inside = self._left.inTree(key, get) or self._right.inTree(key, get, all)
            if is_inside:
                return True
            else:
                return False

        smallest = self.computeLeftPrefix(self._prefixes[0], key, all)
        largest = self.computeRightPrefix(self._prefixes[1], key, all)
        #if the key is inbetween the two keyes
        if largest == self._prefixes[1] and smallest == self._prefixes[0]:
            if get:
                if all is not None:
                    is_inside_left, trans_left = self._left.inTree(key, get, all)
                    is_inside_right, trans_right = self._right.inTree(key, get, all)
                    if trans_left is not None:
                        return True, trans_left
                    if trans_right is not None:
                        return True, trans_right
                    return False, None
            return self._left.inTree(key, get, all) or self._right.inTree(key, get, all)


class MerkleTree:
    def __init__(self, transactions=None, genesis=False):
        self._one = False
        if genesis:
            self._nonce = 0
        else:
            self._nonce = randint(0, 1000)
        if transactions is not None:
            if len(transactions) > 1:
                self._tree = self.buildMT(transactions.copy(), genesis)
            else:
                self._tree = MerkleLeaf(transactions[0], genesis=genesis)
                self._one = True
            self._treeHash = self._tree.getHash()
            self._hash = self.computeHash()
        else:
            self._tree = None
            self._hash = 0

    @classmethod
    def fromJsonDict(cls, dict):
        tree = dict['_tree']
        object = cls()
        object._one = dict['_one']
        if object._one:
            object._tree = MerkleLeaf.fromJsonDict(tree)
        else:
            object._tree = MerkleNode.fromJsonDict(tree)
        object._nonce = dict['_nonce']
        object._hash = dict['_hash']
        object._treeHash = dict['_treeHash']
        return object

    def __str__(self):
        dict = {}
        dict['one'] = self._one
        dict['nonce'] = self._nonce
        dict['root_hash'] = self._tree.getHash()
        return json.dumps(dict, indent = 4, sort_keys=True)

    def toHtml(self):
        return self._tree.toHtml()

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)

    def getHash(self):
        return self._hash

    def setNonce(self, nonce):
        self._nonce = nonce

    def buildMT(self, transactions, genesis):
        #first we sort the merkleTree
        transactions = sorted(transactions, key=attrgetter('_key'))
        transactions = sorted(transactions, key=attrgetter('_timestamp'), reverse=True)
        to_process = Queue()
        jump_next = False
        for i, transaction in enumerate(transactions):
            if jump_next:
                jump_next = False
            else:
                leftHash = MerkleLeaf(transaction, genesis=genesis)
                rightHash = None
                if i < len(transactions) - 1:
                    rightHash = MerkleLeaf(transactions[i+1], genesis=genesis)
                if rightHash is not None:
                    to_process.put([leftHash, rightHash])
                else:
                    to_process.put([leftHash])
                jump_next = True

        tree = None
        while not to_process.empty():
            list1 = to_process.get()
            #last node to process
            if to_process.empty():
                if len(list1) > 1:
                    tree = MerkleNode(list1[0], list1[1], genesis=genesis)
                else:
                    tree = list1[0]
                break

            list2 = to_process.get()


            if len(list1) > 1 and len(list2) > 1:
                to_process.put([MerkleNode(list1[0], list1[1], genesis=genesis),
                                MerkleNode(list2[0], list2[1], genesis=genesis)])
            elif len(list1) > 1:
                next = MerkleNode(list1[0], list1[1], genesis=genesis)
                to_process.put([next, list2[0]])
            elif len(list2) > 1:
                next = MerkleNode(list2[0], list2[1], genesis=genesis)
                to_process.put([list1[0], next])
            else:
                to_process.put([list1[0], list2[0]])

        return tree

    def mine(self, difficulty):
        print('Start mining tree...')
        self._tree.mine(difficulty)
        print('tree mined')
        self._nonce = randint(0, 1000)
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.computeHash()

    def computeHash(self):
        hashString = str(self)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def getTransactions(self):
        return self._tree.getTransactions()

    def isValid(self):
        if self._hash != self.computeHash():
            return False
        if self._treeHash != self._tree.getHash():
            return False
        return self._tree.isValid()

    def isInside(self, key, get=False, all=None):
        return self._tree.inTree(key, get, all)


class Block:
    def __init__(self,
                 timestamp,
                 transactions,
                 previousHash = "",
                 nonce=None,
                 transactionsHash=None,
                 hash=None,
                 notrans=None,
                 genesis=False,
                 block_number=0):
        """Describe the properties of a block."""
        self._block_number = block_number
        self._timestamp = timestamp

        if notrans is None:
            if transactions is None:
                self._transactions = transactions
                self._notrans = True
                self._transactionsHash = None
            else:
                self._transactions = MerkleTree(transactions, genesis)
                self._notrans = False
                self._transactionsHash = self._transactions.getHash()
        else:
            self._transactions = transactions
            self._notrans = notrans
            self._transactionsHash = transactionsHash

        self._previousHash = previousHash
        self.flag_received = False

        if nonce is not None:
            self._nonce = nonce
        else:
            if genesis:
                self._nonce = 0
            else:
                self._nonce = randint(0, 1000)

        if hash is not None:
            self._hash = hash
        else:
            self._hash = self.computeHash()

    @classmethod
    def fromJsonDict(cls, dict):
        block_number = dict['_block_number']
        notrans = dict['_notrans']
        if notrans:
            transactions = dict['_transactions']
        else:
            transactions = MerkleTree.fromJsonDict(dict['_transactions'])
        previousHash = dict['_previousHash']
        timestamp = dict['_timestamp']
        nonce = dict['_nonce']
        hash = dict['_hash']
        transactionsHash = dict['_transactionsHash']
        return cls(timestamp,
                   transactions,
                   previousHash,
                   nonce,
                   transactionsHash,
                   hash,
                   notrans,
                   False,
                   block_number)

    def __str__(self):
        dict = {}
        dict['timestamp'] = self._timestamp
        dict['block number'] = self._block_number
        dict['transHash'] = self._transactionsHash
        dict['nonce'] = self._nonce
        dict['previousHash'] = self._previousHash
        return json.dumps(dict, indent = 4, sort_keys=True)

    def toHtml(self):
        myStr = "<li> Block metaData <ul>"
        myStr += "<li>nonce: {}</li>".format(self._nonce)
        myStr += "<li>prev hash: {}</li>".format(self._previousHash)
        myStr += "<li>hash: {}</li>".format(self._hash)
        myStr += "<li>timestamp: {}</li>".format(self._timestamp)
        myStr += "<li>block number: {}</li>".format(self._block_number)
        myStr += "<li>transHash: {}</li>".format(self._transactionsHash)
        myStr += "</ul>"
        myStr += "<h3>transactions</h3>"
        if self._notrans:
            myStr += "<p>NO TRANSACTION IN THIS BLOCK <br></p>"
        else:
            myStr += "<table style=\"width:100%\">"
            myStr += "<tr>"
            myStr += "<th>Key</th>"
            myStr += "<th>Value</th>"
            myStr += "<th>Timestamp</th>"
            myStr += "</tr>"
            myStr += self._transactions.toHtml()
            myStr += "</table>"
        myStr += "</li>"
        return myStr

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)

    def setPreviousHash(self, hash):
        self._previousHash = hash

    def getPreviousHash(self):
        return self._previousHash

    def getHash(self):
        return self._hash

    def computeHash(self):
        """Compute hash value of the current block"""
        hashString = str(self)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine(self, difficulty):
        while self._hash[0:difficulty] != "0"*difficulty and self.flag_received is False:
            self._nonce += 1
            self._hash = self.computeHash()

        self.flag_received = False

    def getTransactions(self):
        """Returns the list of transactions associated with this block."""
        if self._notrans:
            return []
        return self._transactions.getTransactions()

    def isValid(self):

        if self._hash != self.computeHash():
            return False
        if self._transactions is not None:
            if self._transactionsHash != self._transactions.getHash():
                return False
            return self._transactions.isValid()

        else:
            return True

    def isInside(self, key, get=False, all=None):
        if self._transactions is not None:
            return self._transactions.isInside(key, get, all)
        else:
            if get:
                if all is None:
                    return False, None
                else:
                    return all
            else:
                return False

    def getBlockNumber(self):
        return self._block_number

class Blockchain:
    def __init__(self, api, difficulty=None, blocks=None, transactionBuffer=None):
        """
        The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        addres, download the peerlist, and start the bootstrapping procedure.
        """


        # Initialize blockchain and transactionBuffer HERE
        # Initialize the properties.
        self._difficulty = difficulty
        self._newBlock = None
        self._blockReceived = None
        self._miner = api._miner
        self._attacker = api.attacker

        if blocks is None:
            self._blocks = [self._addGenesisBlock()]
        else:
            self._blocks = blocks


        if transactionBuffer is None:
            self._transactionBuffer = []
        else:
            self._transactionBuffer = transactionBuffer

        self._newBlock = None

        self._peer = peer.Peer(self, api._bootstrap, api._own)
        if self._miner:
            print("START MINING")
            consensusThread = Thread(target = self.lauchMining, args = [])
            consensusThread.start()

    @classmethod
    def fromJsonDict(cls, dict):
        difficulty = dict['_difficulty']
        transactionBufferDict = dict['_transactionBuffer']
        transactionBuffer = []
        for t in transactionBufferDict:
            transactionBuffer.append(Transaction.fromJsonDict(t))
        blockDict = dict['_blocks']
        block = []
        for b in blockDict:
            block.append(Block.fromJsonDict(b))

        return cls(None, difficulty, block, transactionBuffer)

    def setStorage(self, objBC):
        blocks = []
        transactionBuffer = []
        self._blocks = []
        for b in objBC[0]:
            self._blocks.append(Block.fromJsonDict(b))

        for t in objBC[1]:
            self.addTransaction(Transaction.fromJsonDict(t), False)
        self._difficulty = objBC[2]

    def __str__(self):
        myStr = ""
        for block in self._blocks:
            myStr = myStr +\
                    "\n" +\
                    "="*25 +\
                    "\n" +\
                    str(block) +\
                    "\n" +\
                    "hash :{}".format(block.getHash()) +\
                    "\n" +\
                    "="*25 +\
                    "\n"
        return myStr

    def toHtml(self):
        def print_trans(transactions):
             myStr = "<table style=\"width:100%\">"
             myStr += "<tr>"
             myStr += "<th>Key</th>"
             myStr += "<th>Value</th>"
             myStr += "<th>Timestamp</th>"
             myStr += "</tr>"
             for t in transactions:
                 myStr += t.toHtml()
             myStr += "</table>"
             return myStr

        def print_chain(blocks):
            myStr = "<h2> Blockchain</h2>"
            myStr += "<ol type=\"1\">"
            for block in blocks:
                myStr += block.toHtml()
            myStr += "</ol>"
            return myStr

        myStr = "<h2> Transaction pending</h2>" + print_trans(self._transactionBuffer)
        if not self.isValid():
            return myStr + "<h2> Blockchain corrupted </h2>"
        myStr += print_chain(self._blocks)
        return myStr

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, sort_keys=True)

    # Used when nodes conntect to network and ask for the blockchain
    def toJson2(self):
        return json.dumps([self._blocks,
                           self._transactionBuffer,
                           self._difficulty],
                           default=lambda o: o.__dict__, indent=4, sort_keys=True)

    def lastElement(self):
        return self._blocks[len(self._blocks) - 1]

    def getHash(self):
        return self.lastElement().getHash()

    def _addGenesisBlock(self):
        genBlock = Block(0, None, "0", genesis=True)
        return genBlock

    def length(self):
        return len(self._blocks)

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def addTransactions(self, transactions):
        for t in transactions:
            self.addTransaction(t, broadcast=False)

    def addTransaction(self, transaction, broadcast=True):
        """
        Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.
        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        self.addLocTransaction(transaction.toJson())
        if broadcast:
            #MODIF HERE
            self._peer.broadcastTransaction(transaction)

    def addLocTransaction(self, json_transaction):
        self._transactionBuffer.append(Transaction.fromJsonDict(json.loads(json_transaction)))

    def getTransactions(self):
        return self._transactionBuffer

    def lauchMining(self):
        while True:
            #mine block
            block_found = self.mine()
            #if H found broadcast
            if block_found is not None:
                self.addLocBlock(block_found)
                self.broadcastFoundBlock(block_found)
                self._newBlock = None
            #at the same time listen server to know if other found H block
            else:
                if self.getBlockReceived().isValid():
                    self.addLocBlock(self.getBlockReceived())
                    self.setBlockReceived(None)
                    self._newBlock = None
                else:
                    self._peer.askBC()

    def mine(self):
        """Implements the mining procedure."""
        #We should block any procces attemding to write a new transaction in the
        # transactions set.
        if self._newBlock is None:
            print('Start mining new block...')

            transactions = self._transactionBuffer.copy()

            if transactions == []:
                self._newBlock = Block(time.time(), None, block_number=len(self._blocks))
            else:
                self._newBlock = Block(time.time(), transactions, block_number=len(self._blocks))
            self._newBlock.setPreviousHash(self.lastElement().getHash())

        else:
            print('Resume block mining...')

        self._newBlock.mine(self._difficulty)

        if self.getBlockReceived() is None:
            print('Block mined')
            return self._newBlock

        else:
            return None

    def adjustBC(self, faulty):
        correction = self._peer.askBCCorrections(faulty)

    def broadcastFoundBlock(self,block_found):
        #print('BC :', type(block_found), block_found)
        self._peer.broadcastFoundBlock(block_found)

    def setFlagReceived(self):
        self._newBlock.flag_received = True

    def addLocBlock(self, block):
        for t in block.getTransactions():
            if t in self._transactionBuffer:
                self._transactionBuffer.remove(t)

        self._blocks.append(block)

    def getBlockReceived(self):
        return self._blockReceived

    def setBlockReceived(self, block):
        if block is None:
            self._blockReceived = block
        else:
            block = Block.fromJsonDict(json.loads(block))
            if self._miner:
                self._blockReceived = block
                self.setFlagReceived()
            else:
                self.addLocBlock(block)

    def isValid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        for i in range(1, len(self._blocks)):
            current = self._blocks[i]
            prev = self._blocks[i - 1]
            # check if the current hash pointer points to the correct element
            if not current.isValid():
                return False
            if current.getPreviousHash() != prev.computeHash():
                return False
            # check is the node hasn't been modified
            if current.getHash() != current.computeHash():
                return False

        return True

    def isInside(self, key, get=False, all=None):
        for i in reversed(range(len(self._blocks))):
            if all is None:
                print("all is None")
                new_all = None
            else:
                new_all = []

            current = self._blocks[i]
            result = current.isInside(key, get, new_all)

            if get:
                if all is None:
                    if result[0]:
                        return result[1]

                else:
                    for res in result:
                        all.append(res)
            else:
                return result
        return all


def main(args):
    '''Test with 0 transaction.
            - Cannot be tested with merkleTree and no transactionsself.
            - OKaY with merkleTree
            - OKAY with blockchaine
    '''
    '''
    transactionBuffer = None
    bl = Block(time.time(), transactionBuffer, "")
    print(bl.toJson())
    bl2 = Block.fromJsonDict(json.loads(bl.toJson()))
    print(bl2.toJson())
    print(bl2.toJson() == bl.toJson())
    sys.exit()
    '''

    ''' OKAY  With blockChaine and 0 transaction   '''
    '''
    bc= Blockchain("bootstrap", 3)
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''

    '''Test with 1 transaction:
            - OKAY with merkleTree
            - OKAY with block
            - OKAY with blockchain
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    mt = MerkleTree(transactionBuffer)
    print(mt.toJson())
    mt2 = MerkleTree.fromJsonDict(json.loads(mt.toJson()))
    print(mt2.toJson() == mt.toJson())
    sys.exit()
    '''

    ''' OKAY  With block and 1 transaction   '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    bl = Block(time.time(), transactionBuffer, "")
    bl2 = Block.fromJsonDict(json.loads(bl.toJson()))
    print(bl2.toJson() == bl.toJson())
    sys.exit()
    '''

    ''' OKAY  With blockChaine and 1 transaction   '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    bc= Blockchain("bootstrap", 3)
    bc.addTransaction(t1)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''


    '''Test with 2 transactions:
            - OKAY with merkleTree
            - OKAY with block
            - OKAY with blockchain
    '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    transactionBuffer.append(t2)
    mt = MerkleTree(transactionBuffer)
    mt2 = MerkleTree.fromJsonDict(json.loads(mt.toJson()))
    print(mt2.toJson() == mt.toJson())
    sys.exit()
    '''

    ''' OKAY  With block and 2 transaction   '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    transactionBuffer.append(t2)
    bl = Block(time.time(), transactionBuffer, "")
    bl2 = Block.fromJsonDict(json.loads(bl.toJson()))
    print(bl2.toJson() == bl.toJson())
    sys.exit()
    '''

    ''' OKAY  With blockChaine and 1 transaction   '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    t2 = Transaction("pierre2", "key4", "some key value")
    bc= Blockchain("bootstrap", 3)
    bc.addTransaction(t1)
    bc.addTransaction(t2)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''



    '''Test with 3 transactions:
            - OKAY with merkleTree
            - OKAY with block
    '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    transactionBuffer.append(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    transactionBuffer.append(t3)
    mt = MerkleTree(transactionBuffer)
    #print(mt.toJson())
    mt2 = MerkleTree.fromJsonDict(json.loads(mt.toJson()))
    print(mt2.toJson())
    print(mt2.toJson() == mt.toJson())
    sys.exit()
    '''

    ''' OKAY  With block and 3 transaction  '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    transactionBuffer.append(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    transactionBuffer.append(t3)
    bl = Block(time.time(), transactionBuffer, "")
    bl2 = Block.fromJsonDict(json.loads(bl.toJson()))
    print(bl2.toJson() == bl.toJson())
    sys.exit()
    '''

    ''' OKAY  With blockChaine and 3 transaction   '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    t2 = Transaction("pierre2", "key4", "some key value")
    t3 = Transaction("pierre3", "key44", "some other value")
    bc= Blockchain("bootstrap", 3)
    bc.addTransaction(t1)
    bc.addTransaction(t2)
    bc.addTransaction(t3)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''

    '''Test with 4 transactions:
            - OKAY with merkleTree
            - OKAY with block
            - OKAY with blockchain
    '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    transactionBuffer.append(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    transactionBuffer.append(t3)
    t4 = Transaction("pierre3", "key44", "some random other value")
    transactionBuffer.append(t4)
    mt = MerkleTree(transactionBuffer)
    #print(mt.toJson())
    mt2 = MerkleTree.fromJsonDict(json.loads(mt.toJson()))
    print(mt2.toJson())
    print(mt2.toJson() == mt.toJson())
    sys.exit()
    '''

    ''' OKAY  With block and 4 transaction  '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    transactionBuffer.append(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    transactionBuffer.append(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    transactionBuffer.append(t3)
    t4 = Transaction("pierre3", "key44", "some random other value")
    transactionBuffer.append(t4)
    bl = Block(time.time(), transactionBuffer, "")
    bl2 = Block.fromJsonDict(json.loads(bl.toJson()))
    print(bl2.toJson() == bl.toJson())
    sys.exit()
    '''

    ''' OKAY  With blockChaine and 4 transaction   '''
    '''
    transactionBuffer = []
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    t2 = Transaction("pierre2", "key4", "some key value")
    t3 = Transaction("pierre3", "key44", "some other value")
    t4 = Transaction("pierre3", "key44", "some random other value")
    bc= Blockchain("bootstrap", 3)
    bc.addTransaction(t1)
    bc.addTransaction(t2)
    bc.addTransaction(t3)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''


    '''Test with 4 transactions and multiple blocks:
            - OKAY with 4 transaction and 2 blocks
    '''
    '''
    bc= Blockchain("bootstrap", 3)
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    bc.addTransaction(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    bc.addTransaction(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    bc.addTransaction(t3)
    t4 = Transaction("pierre3", "key44", "some random other value")
    bc.addTransaction(t4)
    bc.mine()
    t21 = Transaction("pierre4", "key4", "some value set to 0")
    bc.addTransaction(t21)
    t22 = Transaction("pierre5", "key4", "some key value")
    bc.addTransaction(t22)
    t23 = Transaction("pierre6", "key44", "some other value")
    bc.addTransaction(t23)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''

    '''
    bc= Blockchain("bootstrap", 3)
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    bc.addTransaction(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    bc.addTransaction(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    bc.addTransaction(t3)
    t4 = Transaction("pierre3", "key44", "some random other value")
    bc.addTransaction(t4)
    bc.mine()
    t21 = Transaction("pierre4", "key4", "some value set to 0")
    bc.addTransaction(t21)
    t22 = Transaction("pierre5", "key4", "some key value")
    bc.addTransaction(t22)
    t23 = Transaction("pierre6", "key44", "some other value")
    bc.addTransaction(t23)
    bc.mine()
    t31 = Transaction("pierre7", "key4", "some value set to 0")
    bc.addTransaction(t31)
    t32 = Transaction("pierre8", "key4", "some key value")
    bc.addTransaction(t32)
    t33 = Transaction("pierre9", "key44", "some other value")
    bc.addTransaction(t33)
    t34 = Transaction("pierre10", "key44", "some random other value")
    bc.addTransaction(t34)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''


    bootstrap = "192.168.1.25:8000"
    bootsloc = "192.168.1.25:{}".format(args.port)

    tBuff = None
    if args.port == "8000":
        tBuff = []
        t1 = Transaction("key4", "some value set to 0")
        tBuff.append(t1)
        t2 = Transaction("key4", "some key value")
        tBuff.append(t2)
        t3 = Transaction("key44", "some other value")
        tBuff.append(t3)
        t4 = Transaction("key44", "some random other value")
        tBuff.append(t4)
    app = Fakeapi(bootstrap, bootsloc, args.miner, 5, transactionBuffer=tBuff)

    input()
    if args.port == "8000":
        t1 = Transaction("Guy", "Raclette?")
        app.addTransaction(t1)
        t2 = Transaction("Ben", "OUII")
        app.addTransaction(t2)
        t3 = Transaction("Andrea", "Lovely")
        app.addTransaction(t3)
        t4 = Transaction("Antoine", "Ouais mais pas longtemps je dois bosser demain")
        app.addTransaction(t4)
    #app._blockchain._peer.removeConnection()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', '-p',
        default="8000")

    parser.add_argument(
        '--miner', '-m',
        action='store_true')

    args = parser.parse_args()
    main(args)
