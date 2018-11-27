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

## Todo

1. ~~implement single blockchain.~~
2. implement broadcast system. (Beniboy)
3. implement set of transaction as merkel tree. (Pierre)
4. implement unit tests.
5. run test with 51% of the network.
6. Implement API. (Alex)
7. Add timestamp to each transaction to know which key is the oldest.
8. Table containing key values (but how to protect it from hacker)
