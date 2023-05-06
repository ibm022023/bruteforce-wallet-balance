import binascii
from hashlib import sha256
import itertools
import random
import sys


def getRandomSeedList(withSize=False):
    g=open("./wordlist_BIP39.txt","r")
    bip39_words_list = [line.rstrip() for line in g]

    i=0
    seed_string=""
    while i<11:
        seed_string+=random.sample(bip39_words_list,1)[0].strip("\n")+" "
        i+=1
    #print(seed_string)

    # convert string to list
    seed_list = seed_string.split(' ')
    # remove eventual whitespaces in list
    seed_list = [word.strip() for word in seed_list if word]
    #print(seed_list)

    bits_string = ''
    for word in seed_list:
        decimal_index = bip39_words_list.index(word)
        binary_index = bin(decimal_index)[2:].zfill(11)
        bits_string += binary_index
    bits_to_add = None
    chars_for_checksum = None
    if len(seed_list) == 11:
        bits_to_add = 7
        chars_for_checksum = 1
    elif len(seed_list) == 23:
        bits_to_add = 3
        chars_for_checksum = 2

    combos = itertools.product(['0', '1'], repeat=bits_to_add)
    combos = [ ''.join(list(i)) for i in combos]
    combos = sorted(combos, key=lambda x: int(x, 2))

    lastWord=[]
    #candidates = '\n\nMISSING BITS - WORD:\n'
    for combo in combos:
        entropy = '{}{}'.format(bits_string, combo)
        hexstr = "{0:0>4X}".format(int(entropy,2)).zfill(int(len(entropy)/4))
        data = binascii.a2b_hex(hexstr)
        hs = sha256(data).hexdigest()
        last_bits = ''.join([ str(bin(int(hs[i], 16))[2:].zfill(4)) for i in range  (0, chars_for_checksum) ])
        last_word_bin = '{}{}'.format(combo, last_bits)
        #candidates += '{} - {}\n'.format(combo, bip39_words_list[int(last_word_bin,     2)])

        dummy=bip39_words_list[int(last_word_bin, 2)]

        if withSize:
            return [seed_string+dummy]

        lastWord.append(dummy)

    seed_string_final=[]
    for word in lastWord:
        seed_string_final.append(seed_string+word)

    return seed_string_final


def getRandomSeedListWithSize(size):
    result=[]
    for i in range(size):
        if len(result)==size: #the list is complete
            break
        if len(result)+128<=size:
            for seed in getRandomSeedList():
                result.append(seed)
        result.append(getRandomSeedList(True)[0])
    return result

def getRandomSeedListWithSizeNaive(size):
    result=[]
    for i in range(size):
        if len(result)==size: #the list is complete
            break
        result.append(getRandomSeedList()[0])



