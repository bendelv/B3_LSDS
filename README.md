# info8002_LSDS Project

## Notes

## Links

- [Orverleaf link](https://www.overleaf.com/5154783312jffsnfwyqfqp)
- [Unit tests](https://docs.python.org/3.5/library/unittest.html)
- [Bitcoin](https://bitcoin.org/bitcoin.pdf)
- [Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

## Remarque

difficulty implementation is based on bitcoin paper __Chapter 4 (proof of work)__.
We define the difficulty as being the number of 0 as the prefix of the hash value.
Using an incrementing nonce we can thus implement a proof a work. As mentioned in
the reference paper the amount of work is exponential w.r.t the number of 0s.
## TODO

1. [x] implement single blockchain.
2. [ ] implement broadcast system. (Beniboy)
3. [x] implement set of transaction as merkel tree. (Pierre)
4. [ ] implement unit tests. (ALL)
5. [ ] run test with 51% of the network.
6. [ ] Implement API. (Alex)
7. [x] Add timestamp to each transaction to know which key is the oldest.
8. [ ] Table containing key values (but how to protect it from hacker)


### TODO Pierre

- [x] implement search in the tree by adding min and max prefix to merkleTreeNodes.
- [x] Verify existence travel through min max prefixes.
- [ ] __create one abstract class which will be used in treenoed/leaf and block__ (Is this really necessary)
- [x] look for dumping in json.
- [x] change compute hash to use json version, reduce number of important variables in json dumping for hash nor for serialization
- [x] solve issuie with first prefix.
- [x] implement serialization

### TODO unit Tests
List of all the unit test we need to do
#### Blockchain

- try adding element and check validity
- try altering one transaction
- try altering hashes
- try altering multiple transaction
- dumb and load different level of the blockchain

#Broadcast system

  *Broadcast a new key/value to all users which update buffer. Create merkel tree at time t,
   how to know if all users mine the same block? Consensus, which one?

## Todo

1. ~~implement single blockchain.~~
2. implement broadcast system. (Beniboy)
3. implement set of transaction as merkel tree. (Pierre)
4. implement unit tests. (ALL)
5. run test with 51% of the network.
6. Implement API. (Alex)
7. ~~Add timestamp to each transaction to know which key is the oldest.~~
8. Table containing key values (but how to protect it from hacker)
