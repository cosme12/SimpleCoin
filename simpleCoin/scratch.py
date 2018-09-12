import hashlib
from simpleCoin.Block import Block,buildpow,validate
b0 = Block(0,1536720033.1050985,'0133713371337133713371337133713371337133713371337133713371337','e',{'transactions': None},'0')
# i: 0 time: 1536720033.1050985 	pow: 0133713371337133713371337133713371337133713371337133713371337 effort: e data: {'transactions': None} 	previous: 0 hash: f23c20d1cfcc300bf93dcb2dbca764b0b5ee572b60d1d373f9151fbf31d8bd70
# 11536720034.1133897nrdwmclxbcjguewnfcxqs{'transactions': [{'from': 'network', 'to': 'FNHlQZtOXBoUGiUL3qcOLppy5UuakcYaNrs6KeEMXVUHDOqGWwRjGswBVcXlT4R3B2MDY1dYZelcq4OjMeQ00g==', 'amount': 1.0}]}f23c20d1cfcc300bf93dcb2dbca764b0b5ee572b60d1d373f9151fbf31d8bd70
# i: 1 time: 1536720034.1133897 	pow: 36201854fa4195c9f09f746a1639d34b5d5c34634d0e6edc5bbb11e736490a90 effort: nrdwmclxbcjguewnfcxqs data: {'transactions': [{'from': 'network', 'to': 'FNHlQZtOXBoUGiUL3qcOLppy5UuakcYaNrs6KeEMXVUHDOqGWwRjGswBVcXlT4R3B2MDY1dYZelcq4OjMeQ00g==', 'amount': 1.0}]} 	previous: f23c20d1cfcc300bf93dcb2dbca764b0b5ee572b60d1d373f9151fbf31d8bd70 hash: b88710787bda6449ed2f7631d6240f9e034bbc52c65027ea3efd6ca606225fdd
b1 =  Block(1,1536720034.1133897,'36201854fa4195c9f09f746a1639d34b5d5c34634d0e6edc5bbb11e736490a90','nrdwmclxbcjguewnfcxqs',{'transactions': [{'from': 'network', 'to': 'FNHlQZtOXBoUGiUL3qcOLppy5UuakcYaNrs6KeEMXVUHDOqGWwRjGswBVcXlT4R3B2MDY1dYZelcq4OjMeQ00g==', 'amount': 1.0}]},'f23c20d1cfcc300bf93dcb2dbca764b0b5ee572b60d1d373f9151fbf31d8bd70')
# 21536720034.1184013gckvrsf{'transactions': [{'from': 'network', 'to': 'FNHlQZtOXBoUGiUL3qcOLppy5UuakcYaNrs6KeEMXVUHDOqGWwRjGswBVcXlT4R3B2MDY1dYZelcq4OjMeQ00g==', 'amount': 1.0}]}b88710787bda6449ed2f7631d6240f9e034bbc52c65027ea3efd6ca606225fdd
# i: 2 time: 1536720034.1184013 	pow: 0ce49ef80516b73e33b9adf98c7a59f67155e0f328e0846cc3400bdf7851ba14 effort: gckvrsf data: {'transactions': [{'from': 'network', 'to': 'FNHlQZtOXBoUGiUL3qcOLppy5UuakcYaNrs6KeEMXVUHDOqGWwRjGswBVcXlT4R3B2MDY1dYZelcq4OjMeQ00g==', 'amount': 1.0}]} 	previous: b88710787bda6449ed2f7631d6240f9e034bbc52c65027ea3efd6ca606225fdd hash: 6e3dd1e9fea3ad2a868ddfe503827c2d7e685c366218bb3c0d26418d51203a01
b2 =  Block(2,1536720034.1184013,'0ce49ef80516b73e33b9adf98c7a59f67155e0f328e0846cc3400bdf7851ba14','gckvrsf',{'transactions': [{'from': 'network', 'to': 'FNHlQZtOXBoUGiUL3qcOLppy5UuakcYaNrs6KeEMXVUHDOqGWwRjGswBVcXlT4R3B2MDY1dYZelcq4OjMeQ00g==', 'amount': 1.0}]},'b88710787bda6449ed2f7631d6240f9e034bbc52c65027ea3efd6ca606225fdd')
work = 1
blockchain = [b0,b1,b2]



def validate_blockchain(blockchain):
    global work

    def leadingzeroes(digest):
        n = 0
        result = ''.join(format(x, '08b') for x in bytearray(digest))
        for c in result:
            if c == '0':
                n += 1
            else:
                break
        return n

    previous = ""
    for i in range(0,len(blockchain)-1):
        if blockchain[i].index == 0:
            continue

        if not validate(blockchain[i]):
            print("failed to validate",i)
            return False
        for transaction in blockchain[i].data['transactions']:
            if transaction['from'] == "network" and transaction['amount'] != 1:
                print("failed to transaction", i)
                return False
        #(index,timestamp,effort,data,previous_hash):
        lead = leadingzeroes(buildpow(blockchain[i].index,blockchain[i].timestamp,blockchain[i].effort,blockchain[i].data,blockchain[i-1].hash).digest())
        if lead < work:
            print("failed lead", i)
            return False

    return True

print(validate_blockchain(blockchain))