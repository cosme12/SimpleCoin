'''THIS IS THE MODULE THAT CONTAINS THE POW ALGORYTHM.
YOU CAN CALL THIS FUNCTION IMPORTING THIS MODULE:
import pow
pow.poof_of_work()

or

from pow import poof_of_work
proof_of_work()

or directly pasting this code into the script in which you want to use it :)
'''
import hashlib
import re
import string
from random import randrange

def proof_of_work():
    def random_str():
        '''GENERATES RANDOM STRING MADE OF DOWNCASE LETTERS [a-z]'''
        rand_str = ''
        for i in range(randrange(1, 20)):#the string length is random, from 1 to 20 chars...
            rand_str += string.ascii_lowercase[randrange(26)]#each char is a random downcase letter [a-z]
        return rand_str #returns the random string

    def check(str1, str2):
        '''SUMS 2 STRINGS, CREATES A MD5 HASH WITH THAT SUM AND CHECKS IF THE FIRST
        4 NUMBERS OF THE HASH ARE 0. THAT MAKES TO FIND A HASH A COMPUTATIONAL WORK'''
        sum_of_str = (str1 + str2).encode("utf_8")#sums 2 strings
        #now, lets convert them to a md5 hash
        m = hashlib.md5()
        m.update(sum_of_str)
        hash_generated = m.hexdigest()
        #done.

        if re.match("0000", str(hash_generated)):#now we see if the hash's first 4 chars are 0
            return True #if the hash is correct, return true
        else:
            return False #if the hash is not correct, return false
    
    '''MAIN PROCCES: '''
    string_one = random_str() #generates a random string...
    #... and try continuously to find another string that combined with
    #the first make a valid hash. That costs a computational effort :)
    while True:
        if check(string_one, random_str()):
            break