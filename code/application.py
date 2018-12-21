"""
User-level application (stub).

NB: Feel free to extend or modify.
"""
import time
import argparse

from blockchain import Blockchain, Transaction

class Callback:
    def __init__(self, transaction, chain):
        self._transaction = transaction
        self._chain = chain

    def wait(self):
        """Wait until the transaction appears in the blockchain."""
        raise NotImplementedError

    def completed(self):
        """Polls the blockchain to check if the data is available."""
        raise NotImplementedError

class Application:
    def __init__(self, bootstrap, bootsloc, miner, difficulty):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self._own = bootsloc
        self._bootstrap = bootstrap
        self._miner = miner
        self._blockchain = Blockchain(self, difficulty)

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        transaction = Transaction(key, value)
        self._blockchain.addTransaction(transaction)

        callback = Callback(transaction, self._blockchain)
        if block:
            callback.wait()

        return callback

    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
        value = self._blockchain.isInside(key, get=True)
        return value

    def retrieveAll(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        valueList = self._blockchain.isInside(key, True, [])
        return valueList
