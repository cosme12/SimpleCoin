import requests
import json
from ast import literal_eval
res = requests.get('http://localhost:5000/blocks')
chain = res.json()
balance = {
    "network":0
}
del chain[0]
for block in chain:
    data = block.get("data")
    data = literal_eval(data)
    transactions = data.get("transactions")
    transaction = (transactions[0])
    tx = transaction.get("from")
    rx = transaction.get("to")
    amount = transaction.get("amount")
    if tx in balance:
        balance[tx] = balance[tx]-int(amount)
    else:
        balance[tx] = 0-amount
    if rx in balance:
        balance[rx] = balance[rx]+int(amount)
    else:
        balance[rx] = amount
for adress in balance:
    if adress != "network":
        print(adress)
        print(balance[adress])
        print("\n")
