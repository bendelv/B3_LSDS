"""
User-level application (stub).

NB: Feel free to extend or modify.
"""
import time
import argparse
"from blockchain import Blockchain"

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

class Transaction:
    def __init__(self, origin, key, value, timestamp=time.time()):
        """
        A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self._origin = origin
        self._key = key
        self._value = value
        self._timestamp = timestamp

    @classmethod
    def fromJsonDict(cls, dict):
        return cls(dict['_origin'], dict['_key'], dict['_value'], dict['_timestamp'])

    def __str__(self):
        dict = {}
        dict["Origin"] = self._origin
        dict["Key"] = self._key
        dict["Value"] = self._value
        dict["timestamp"] = self._timestamp
        return json.dumps(dict, indent = 4)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def get_key(self):
        return self._key

    def get_timestamp(self):
        return self._timestamp

class Application:
    def __init__(self, bootstrap, bootsloc, miner, difficulty):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self._bootsloc = bootsloc
        self._bootstrap = bootstrap
        self._miner = miner
        self._blockchain = Blockchain(self, difficulty)

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        transaction = Transaction(self._bootsloc, key, value)
        self._blockchain.add_transaction(self, transaction)

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
        value = self._blockchain.is_inside(key, True)
        return value

    def retrieveAll(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        valueList = self._blockchain.is_inside(key, True, [])
        return valueList

def main(args):
    
    pass
if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
