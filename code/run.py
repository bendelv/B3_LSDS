from application import Application
import argparse
import time

def allocate_application(arguments):
    application = Application(
        bootstrap=arguments.bootstrap,
        bootsloc="192.168.1.41:{}".format(arguments.port),
        miner=arguments.miner,
        difficulty=arguments.difficulty)

    return application


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--miner", type=bool, default=True, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default='192.168.1.41:8000',
                        help="Sets the address of the bootstrap node.")
    parser.add_argument("--port", '-p', type=str, default='8000',
                        help="Sets the address of the local node.")
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")
    arguments = parser.parse_args()
    return arguments

def main(arguments):
    app = allocate_application(arguments)

    # Adding a key-value pair to the storage.
    value = input("Value: ")
    app.put("T", value, block=False)

    input()
    print(app.retrieve("T"))

    input()

    retrieved_list = app.retrieveAll("T")
    for retrieved in retrieved_list:
        print(retrieved)
        
    """
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
    """

if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
