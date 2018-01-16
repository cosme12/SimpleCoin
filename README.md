# SimpleCoin
Just a really simple, insecure and incomplete implementation of a blockchain for a cryptocurrency made in Python. The goal of this project is to make a working blockchain currency, keeping it as simple as posible, to be used as educational material.

>This project is just being made for fun. If you want to make your own cryptocurrency you should probably take a look at the [Bitcoin Repository](https://github.com/bitcoin/bitcoin).


## What is a blockchain?

Taking a look at the [Bitcoin organization wiki website](https://en.bitcoin.it/wiki/Main_Page) we can find this definition:

>A block chain is a transaction database shared by all nodes participating in a system based on the Bitcoin protocol. A full copy of a currency's block chain contains every transaction ever executed in the currency. With this information, one can find out how much value belonged to each address at any point in history. 

You can find more information in the original [Bitcoin Paper](https://bitcoin.org/bitcoin.pdf).

## How this code work?

There are 2 main scripts:

- ```miner.py```
- ```wallet.py```

### Miner.py

This file is probably the most import. Running it will create a node (like a server). From here you can connet to the blockchain and process transaction (that other users send) by mining. As a reward for this work, you recieve some coins. The more nodes exist, the more secure the blockchain gets.

### Wallet.py

This file is for those that don't want to be a node but simple users. Running this file allows you to generate a new address, send coins and check your transaction history.

## Contribution
Anybody is welcome to collaborate in this project. Feel free to push any pull request (even if you are new to coding).

Note: the idea of this project is to build a **really simple** blockchain system, so make sure all your code is easy to read (avoid to much code in 1 line) and don't introduce complex updates if they are not critical. In other words, keep it simple.


## Disclaimer
By no means this project should be used for real purposes, it lacks security and may contain several bugs.