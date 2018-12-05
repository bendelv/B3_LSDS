# 1. Info8002_LSDS Project

## 1.1 Notes

- merkleTree is build as follow, we lsit all transaction and sort them according to
the alphabetical order of the key, and we break the ties be sortinc according to the
timestamp. Then we build the leaf on in a buttom up way we build the tree.
- To mine the tree we first mine the leafs, then update the hashes.
After that we mine every node in the tree and finally we mine the root of the tree.
- To search presence in the tree, we use a array of prefixes attached to each node.
The first element of the array indicate the lowest value present in the tree.
The second element indicates the largest value in the tree.
- The blockchain is dumped to json format in order to be send through messages.
The is also a method of the chain in order to build the object from the json string.

## 1.2 Links

- [Orverleaf link](https://www.overleaf.com/5154783312jffsnfwyqfqp)
- [Unit tests](https://docs.python.org/3.5/library/unittest.html)
- [Bitcoin](https://bitcoin.org/bitcoin.pdf)
- [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

## 1.3 Remarque

difficulty implementation is based on bitcoin paper __Chapter 4 (proof of work)__.
We define the difficulty as being the number of 0 as the prefix of the hash value.
Using an incrementing nonce we can thus implement a proof a work. As mentioned in
the reference paper the amount of work is exponential w.r.t the number of 0s.
## 1.4 TODO

1. [x] implement single blockchain.
2. [ ] implement broadcast system. (Pierre)
3. [x] implement set of transaction as merkel tree. (Pierre)
4. [ ] implement unit tests. (ALL)
5. [ ] run test with 51% of the network.
6. [ ] Implement API. (Alex)
7. [x] Add timestamp to each transaction to know which key is the oldest.
8. [ ] Table containing key values (but how to protect it from hacker)


### 1.4.1 TODO Pierre

- [x] implement search in the tree by adding min and max prefix to merkleTreeNodes.
- [x] Verify existence travel through min max prefixes.
- [x] __create one abstract class which will be used in treenoed/leaf and block__ (Is this really necessary)
- [x] look for dumping in json.
- [x] change compute hash to use json version, reduce number of important variables in json dumping for hash nor for serialization
- [x] solve issuie with first prefix.
- [x] implement serialization

### 1.4.2 TODO unit Tests

List of all the unit test we need to do

#### 1.4.3 Blockchain

- try adding element and check validity
- try altering one transaction
- try altering hashes
- try altering multiple transaction
- dumb and load different level of the blockchain

# 2. Broadcast system

* Broadcast a new key/value to all users which update buffer. Create merkel tree at time t,
   how to know if all users mine the same block? Consensus, which one?

# 3. Network

## 3.1 Transactions

  - put(k, v), broadcast transaction
  - when new block, consensus on block to mine.
  - transmit mined block.

## 3.2 Connection

  - [x] add new address to bootstrap server.
  - [x] broadcast new address.
  - [ ] broadcast blockChain and current transactionBuffer if miner to new peer.

## 3.3 Retrieve

  - get local from local version of blockchain.

# 4. Consensus
