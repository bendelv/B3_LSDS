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
from peer import Peer


class FakeApplication:
    def __init__(self, bootstrap, bootsloc, miner, difficulty):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self._bootsloc = bootsloc
        self._bootstrap = bootstrap
        self._miner = miner
        self._blockchain = Blockchain(self)


class MerkleLeaf:
    def __init__(self, transaction, prefixes=None, nonce=0, hash=None, leaf=True):
        self._transaction = transaction
        if prefixes is not None:
            self._prefixes = prefixes
        else:
            self._prefixes = self.compute_prefixes()
        if nonce != 0:
            self.nonce = nonce
        else:
            self._nonce = randint(0, 1000)
        if hash is not None:
            self._hash = hash
        else:
            self._hash = self.compute_hash()
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
        return json.dumps(dict, indent=4)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def get_hash(self):
        return self._hash

    def get_transaction(self):
        return self._transaction

    def compute_prefixes(self):
        return [str(self._transaction.get_key()),str(self._transaction.get_key())]

    def compute_hash(self):
        hashString = str(self)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine(self, difficulty):
        print("Start Mining leaf...")
        self._nonce = randint(0, 1000)
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.compute_hash()
        print("leaf mined")

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


class MerkleNode:
    def __init__(self, left, right, leftHash=None, rightHash=None, prefixes=None, nonce=None, hash=None):
        self._left = left
        self._right = right
        if leftHash is not None:
            self._leftHash = leftHash
        else:
            self._leftHash = left.get_hash()

        if rightHash is not None:
            self._rightHash = rightHash
        else:
            self._rightHash = right.get_hash()

        if prefixes is not None:
            self._prefixes = prefixes
        else:
            self._prefixes = self.compute_prefixes()

        if nonce is not None:
            self._nonce = nonce
        else:
            self._nonce = randint(0, 1000)

        if hash is not None:
            self._hash = hash
        else:
            self._hash = self.compute_hash()

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
        return json.dumps(dict, indent=4)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

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
        self._leftHash = self._left.get_hash()
        self._rightHash = self._right.get_hash()
        self._nonce = randint(0, 1000)
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.compute_hash()

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


class MerkleTree:
    def __init__(self, transactions=None):
        self._one = False
        self._nonce = randint(0, 1000)
        if transactions is not None:
            if len(transactions) > 1:
                self._tree = self.buildMT(transactions.copy())
            else:
                self._tree = MerkleLeaf(transactions[0])
                self._one = True
            self._hash = self.compute_hash()
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
        return object

    def __str__(self):
        dict = {}
        dict['one'] = self._one
        dict['nonce'] = self._nonce
        dict['root_hash'] = self._tree.get_hash()
        return json.dumps(dict, indent = 4)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def get_hash(self):
        return self._hash

    def buildMT(self, transactions):
        #first we sort the merkleTree
        transactions = sorted(transactions, key=attrgetter('_key'))
        transactions = sorted(transactions, key=attrgetter('_timestamp'), reverse=True)
        to_process = Queue()
        jump_next = False
        for i, transaction in enumerate(transactions):
            if jump_next:
                jump_next = False
            else:
                leftHash = MerkleLeaf(transaction)
                rightHash = None
                if i < len(transactions) - 1:
                    rightHash = MerkleLeaf(transactions[i+1])
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

    def mine(self, difficulty):
        print('Start mining tree...')
        self._tree.mine(difficulty)
        print('tree mined')
        self._nonce = randint(0, 1000)
        while self._hash[0:difficulty] != "0"*difficulty:
            self._nonce += 1
            self._hash = self.compute_hash()

    def compute_hash(self):
        hashString = str(self)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def is_valid(self):
        if self._hash != self._tree.get_hash():
            return False
        return self._tree.is_valid()

    def is_inside(self, key, get=False, all=None):
        return self._tree.in_tree(key, get, all)


class Block:
    def __init__(self, timestamp, transactions, previousHash = "", nonce=None, transactionsHash=None, hash=None, notrans=None):
        """Describe the properties of a block."""
        self._timestamp = timestamp

        if notrans is None:
            if transactions is None:
                self._transactions = transactions
                self._notrans = True
                self._transactionsHash = None
            else:
                self._transactions = MerkleTree(transactions)
                self._notrans = False
                self._transactionsHash = self._transactions.get_hash()
        else:
            self._transactions = transactions
            self._notrans = notrans
            self._transactionsHash = transactionsHash

        self._previousHash = previousHash

        if nonce is not None:
            self._nonce = nonce
        else:
            self._nonce = randint(0, 1000)

        if hash is not None:
            self._hash = hash
        else:
            self._hash = self.compute_hash()

        self.blockReceived = None

    @classmethod
    def fromJsonDict(cls, dict):
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
        return cls(timestamp, transactions, previousHash, nonce, transactionsHash, hash, notrans)

    def __str__(self):
        dict = {}
        dict['timestamp'] = self._timestamp
        dict['transactions_hash'] = self._transactionsHash
        dict['nonce'] = self._nonce
        dict['previousHash'] = self._previousHash
        return json.dumps(dict, indent = 4)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def set_previous_hash(self, hash):
        self._previousHash = hash

    def get_previous_hash(self):
        return self._previousHash

    def get_hash(self):
        return self._hash

    def compute_hash(self):
        """Compute hash value of the current block"""
        hashString = str(self)
        hash_object = hashlib.sha256(hashString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def mine(self, difficulty):
        """
        print("Start mining transactions...")
        self._transactions.mine(difficulty)
        print("Transactions mined")
        """

        "self._nonce = randint(0, 1000)"
        while self._hash[0:difficulty] != "0"*difficulty and self.blockReceived is None:
            self._nonce += 1
            self._hash = self.compute_hash()

    def transactions(self):
        """Returns the list of transactions associated with this block."""
        return self._transactions

    def is_valid(self):
        return self._transactions.is_valid()

    def is_inside(self, key, get=False, all=None):
        return self._transactions.is_inside(key, get, all)


class Blockchain:
    def __init__(self, application, difficulty=None, blocks=None, transactionBuffer=None):
        """
        The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        addres, download the peerlist, and start the bootstrapping procedure.
        """

        self._peer = Peer(self, application._bootstrap, application._bootsloc)

        # Initialize blockchain and transactionBuffer HERE
        # Initialize the properties.
        self._difficulty = difficulty
        """
        if blocks is None:
            self._blocks = [self._add_genesis_block()]
        else:
            self._blocks = blocks

        if transactionBuffer is None:
            self._transactionBuffer = []
        else:
            self._transactionBuffer = transactionBuffer

        self._newBlock = None

        if application.miner = True:
            consensusThread = Thread(target = self.lauchMining, args = [])
            consensusThread.start()
        """

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
        load = json.loads(objBC)
        self._blocks = load[0]
        self._transactionBuffer = load[1]

    def __str__(self):
        myStr = ""
        for block in self._blocks:
            myStr = myStr + "\n" + "="*25 + "\n" + str(block) + "\n" + "="*25 + "\n"
        return myStr

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def toJson2(self):
        return json.dumps([self._blocks, self._transactionBuffer])

    def last_element(self):
        return self._blocks[len(self._blocks) - 1]

    def _add_genesis_block(self):
        genTrans = Transaction("none", None, "")
        genBlock = Block(time.time(), [genTrans], "0")
        return genBlock

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def loc_add_transaction(transaction):
        self._transactionBuffer.append(transaction)

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.
        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """

        self._peer.clientSide.broadcastTransaction(transaction)
        self.loc_add_transaction(transaction)

    def lauchMining():
        while True:
            #mine block
            block_found = self.mine()
            #if H found broadcast
            if block_found is not None:
                self._peer.broadcast_foundBlock(block_found)
                self._blocks.append(block_found)
                self._newBlock = None
            #at the same time listen server to know if other found H block
            else:
                if self.get_blockReceived().is_valid():
                    self._blocks.append(block_found)
                    self._newBlock = None
                else:
                    print("Block received non valid..")

    def mine(self):
        """Implements the mining procedure."""
        #We should block any procces attemding to write a new transaction in the
        # transactions set.
        if self._newBlock is None:
            print('Start mining new block...')
            self._newBlock = Block(time.time(), self._transactionBuffer.copy())
            self._transactionBuffer = []
            newBlock.set_previous_hash(self.last_element().get_hash())

        else:
            print('Resume block mining...')

        self._newBlock.mine(self._difficulty)

        if self._newBlock.blockReceived is None:
            print('Block mined')
            return newBlock

        else:
            return None

    def set_blockReceived(self, jsonBlock):
        self._newBlock.blockReceived = self.Block.fromJsonDict(jsonBlock)

    def get_blockReceived(self):
        return self._newBlock.blockReceived

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
    bc.add_transaction(t1)
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
    bc.add_transaction(t1)
    bc.add_transaction(t2)
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
    bc.add_transaction(t1)
    bc.add_transaction(t2)
    bc.add_transaction(t3)
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
    bc.add_transaction(t1)
    bc.add_transaction(t2)
    bc.add_transaction(t3)
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
    bc.add_transaction(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    bc.add_transaction(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    bc.add_transaction(t3)
    t4 = Transaction("pierre3", "key44", "some random other value")
    bc.add_transaction(t4)
    bc.mine()
    t21 = Transaction("pierre4", "key4", "some value set to 0")
    bc.add_transaction(t21)
    t22 = Transaction("pierre5", "key4", "some key value")
    bc.add_transaction(t22)
    t23 = Transaction("pierre6", "key44", "some other value")
    bc.add_transaction(t23)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''

    '''
    bc= Blockchain("bootstrap", 3)
    t1 = Transaction("pierre1", "key4", "some value set to 0")
    bc.add_transaction(t1)
    t2 = Transaction("pierre2", "key4", "some key value")
    bc.add_transaction(t2)
    t3 = Transaction("pierre3", "key44", "some other value")
    bc.add_transaction(t3)
    t4 = Transaction("pierre3", "key44", "some random other value")
    bc.add_transaction(t4)
    bc.mine()
    t21 = Transaction("pierre4", "key4", "some value set to 0")
    bc.add_transaction(t21)
    t22 = Transaction("pierre5", "key4", "some key value")
    bc.add_transaction(t22)
    t23 = Transaction("pierre6", "key44", "some other value")
    bc.add_transaction(t23)
    bc.mine()
    t31 = Transaction("pierre7", "key4", "some value set to 0")
    bc.add_transaction(t31)
    t32 = Transaction("pierre8", "key4", "some key value")
    bc.add_transaction(t32)
    t33 = Transaction("pierre9", "key44", "some other value")
    bc.add_transaction(t33)
    t34 = Transaction("pierre10", "key44", "some random other value")
    bc.add_transaction(t34)
    bc.mine()
    bc2 = Blockchain.fromJsonDict(json.loads(bc.toJson()))
    print(bc2.toJson() == bc.toJson())
    sys.exit()
    '''


    bootstrap = "192.168.1.25:8000"
    bootsloc = "192.168.1.25:{}".format(args.bootsloc)
    app = FakeApplication(bootstrap, bootsloc, False, 1)

    input()

    #peer.removeConnection()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bootsloc', '-b',
        default="8001")
    args = parser.parse_args()
    main(args)
