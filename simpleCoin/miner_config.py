import simpleCoin.user
# Port to run on
PORT = 5000
# Write your node url or ip. If you are running it localhost use default
MINER_NODE_URL = "http://localhost:"+str(PORT)

# Store the url data of every other node in the network
# so that we can communicate with them
PEER_NODES = []
