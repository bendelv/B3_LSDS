"""
User-level application (stub).

NB: Feel free to extend or modify.
"""

import argparse
from peer import Peer

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
    def __init__(self, bootstrap, miner, difficulty):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self._peer = Peer(bootstrap)
        self._blockchain = Blockchain()

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        raise NotImplementedError
        transaction = Transaction(...)
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
        raise NotImplementedError

    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        raise NotImplementedError


def allocate_application(arguments):
    application = Application(
        bootstrap=arguments.bootstrap,
        miner=arguments.miner,
        difficulty=arguments.difficulty)

    return application


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")
    arguments, _ = parser.parse_known_args()

    return arguments

def main(arguments):
    app = allocate_application(arguments)

    # Adding a key-value pair to the storage.
    key = "info8002"
    value = "fun"
    callback = app.put(key, value, block=False)

    # Depending on how fast your blockchain is,
    # this will return a proper result.
    print(app.retrieve(key))

    # Using the callback object,
    # you can also wait for the operation to be completed.
    callback.wait()

    # Now the key should be available,
    # unless a different node `put` a new value.
    print(app.retrieve(key))

    # Show all values of the key.
    print(app.retrieve_all(key))


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
