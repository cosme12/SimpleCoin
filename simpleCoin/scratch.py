import hashlib
import secrets
import string

def leadingzeroes(digest):
    #binary = ' '.join(map(bin,bytearray(sample_string,encoding='utf-8')))
    n = 0
    result = ''.join(format(x, '08b') for x in bytearray(digest))
    for c in result:
        if c == '0':
            n+=1
        else:
            break
    return n
def random_str():
    # Generate a random size string from 3 - 27 characters long
    rand_str = ''
    for i in range(0, 1 + secrets.randbelow(25)):
        rand_str += string.ascii_lowercase[secrets.randbelow(26)]  # each char is a random downcase letter [a-z]
    return rand_str


work = 13
for i in range(0,5):
    m = hashlib.sha256()
    m.update(random_str().encode('utf-8'))
    test = m.hexdigest()
    #while test[0:work] != "0"*work:
    n = leadingzeroes(m.digest())
    while n < work:
        m = None
        r = None
        m = hashlib.sha256()
        r = random_str()
        m.update(r.encode('utf-8'))
        test = m.hexdigest()
        n = leadingzeroes(m.digest())

    print(test,leadingzeroes(m.digest()))
