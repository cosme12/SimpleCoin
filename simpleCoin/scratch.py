import hashlib
import secrets
import string
import time
from multiprocessing import Process, Queue
import os

def random_str():
    # Generate a random size string from 3 - 27 characters long
    rand_str = ''
    for i in range(0, 1 + secrets.randbelow(25)):
        rand_str += string.ascii_lowercase[secrets.randbelow(26)]  # each char is a random downcase letter [a-z]
    return rand_str

def createhash():
    m = hashlib.sha256()
    m.update(random_str().encode(('utf-8')))
    return m.hexdigest()

def work(q):
    test = createhash()
    while test[0:4] != "0"*4 :
        test = createhash()
    print(test)
    q.put(test)

processes = []
if __name__ == '__main__':
    q = Queue()
    for i in range(os.cpu_count()-3):
        print('registering process %d' % i)
        processes.append(Process(target=work,args = (q,)) )
    start = time.time()
    print("start: ",start)
    for process in processes:
        process.start()
    while True:
        if not q.empty():
            test = q.get()
            print(test)
            for process in processes:
                process.terminate()

    end = time.time()
    print("end: ", end)
    print("delta: ", end - start)