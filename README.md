# Info8002_LSDS Project

## 1. Notes

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

## 2. Links

- [Orverleaf link](https://www.overleaf.com/5154783312jffsnfwyqfqp)
- [Unit tests](https://docs.python.org/3.5/library/unittest.html)
- [Bitcoin](https://bitcoin.org/bitcoin.pdf)
- [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

## 3. Remarque

difficulty implementation is based on bitcoin paper __Chapter 4 (proof of work)__.
We define the difficulty as being the number of 0 as the prefix of the hash value.
Using an incrementing nonce we can thus implement a proof a work. As mentioned in
the reference paper the amount of work is exponential w.r.t the number of 0s.

## 4. TODO
### Unit test

- [ ] implement unit tests. (ALL)
- [ ] run test with 51% of the network.
- [ ] try adding element and check validity
- [ ] try altering one transaction
- [ ] try altering hashes
- [ ] try altering multiple transaction
- [ ] dumb and load different level of the blockchain

### User/high level application

- [ ] Implement API. (Alex)
- [ ] Joint all features (Ben)

### Blockchain

- [x] implement single blockchain.
- [x] implement set of transaction as merkel tree. (Pierre)
- [x] Add timestamp to each transaction to know which key is the oldest.
- [ ] Table containing key values (but how to protect it from hacker)?
- [x] implement search in the tree by adding min and max prefix to merkleTreeNodes.
- [x] Verify existence travel through min max prefixes.
- [x] __create one abstract class which will be used in treenoed/leaf and block__ (Is this really necessary)
- [x] look for dumping in json.
- [x] change compute hash to use json version, reduce number of important variables in json dumping for hash nor for serialization
- [x] solve issuie with first prefix.
- [x] implement serialization

### Consensus

### Broadcast

- [ ] implement broadcast system. (Pierre)

### Network

- [x] add new address to bootstrap server.
- [x] broadcast new address.
- [ ] broadcast JSon objects trough broadcast system. (in particular Blockchain, new key/value, list of connected peer)
- [ ] get local from remote version of blockchain and transmit to Blockchain level

### Low level features

- [x] Perfect link
- [x] fail silent detector
