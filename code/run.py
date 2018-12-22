from application import Application
import argparse
import time

def allocate_application(arguments):
    application = Application(
        bootstrap=arguments.bootstrap,
        bootsloc="192.168.1.25:{}".format(arguments.port),
        miner=arguments.miner,
        difficulty=arguments.difficulty,
        attacker=arguments.attacker,
        attack_context=arguments.attack_context)

    return application


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--miner", type=bool, default=True, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default='192.168.1.25:8000',
                        help="Sets the address of the bootstrap node.")
    parser.add_argument("--port", '-p', type=str, default='8000',
                        help="Sets the address of the local node.")
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")
    parser.add_argument("--attacker", "-a", action='store_true')
    parser.add_argument('--attack_context', '-ac', action='store_true')
    arguments = parser.parse_args()
    return arguments

def main(arguments):
    app = allocate_application(arguments)

    # Adding a key-value pair to the storage.
    value = input("Value to link at 'key1' :\n")
    app.put("key1", value, block=False)
    app.put("key2", value, block=False)

    #Check last version of a key
    key = input("Verify last version of a key:\n")
    print(app.retrieve(key))

    #Check all versions of a key
    key = input("Verify all versions of a key:\n")
    retrieved_list = app.retrieveAll(key)
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
