"""
Some code taken from Peter Norvig's forthcoming article for _Beautiful Data_.
"""

import re, string, random, glob, operator, heapq
from collections import defaultdict
from math import log10

################ Utilities

def product(nums):
    return reduce(operator.mul, nums, 1)

def memo(f):
    "Memoize function f."
    table = {}
    def fm(*x):
        if x not in table:
            table[x] = f(*x)
        return table[x]
    fm.memo = table
    return fm

class Memo(dict):
    def __init__(self, f):
        self.f = f
    def __call__(self, *x):
        return self[x]
    def __missing__(self, key):
        result = self.f(*key)
        self[key] = result
        return result

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[], N=None, missingfn=None):
        for key,count in data:
            if key != '<S>': key = key.lower()
            self[key] = self.get(key, 0) + int(count)
        self.N = float(N or sum(self.itervalues()))
        self.missingfn = missingfn or (lambda k, N: 1./N)
    def __call__(self, key): 
        if key in self: return self[key]/self.N  
        else: return self.missingfn(key, self.N)

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in file(name):
        yield line.split(sep)

def avoid_long_words(key, N):
    "Estimate the probability of an unknown word."
    return 10./(N * 10**len(key))

################ Loading Data

# About 7% of 5gram counts missing
#NT = 1024908267229 ## Number of tokens
#Pw  = Pdist(datafile('vocab_canon_cs_3'), NT, avoid_long_words)
#Pw2 = Pdist(datafile('2gm-common6'), NT)
NT = 1024908267229 + 1e10 ## Number of tokens -- contractions added
Pw  = Pdist(datafile('contractionmodel.unigram'), NT, avoid_long_words)
Pw2 = Pdist(datafile('contractionmodel.bigram'), NT)

#NT = 641241
#Pw  = Pdist(datafile('vocab_austen'), NT, avoid_long_words)
#Pw2 = Pdist(datafile('2gm-austen'), NT)

#NT = 475637
#Pw  = Pdist(datafile('vocab_tolkien'), NT, avoid_long_words)
#Pw2 = Pdist(datafile('2gm-tolkien'), NT)

#NT = 821133
#Pw  = Pdist(datafile('vocab_bible'), NT, avoid_long_words)
#Pw2 = Pdist(datafile('2gm-bible'), NT)

def cPw(word, prev):
    "Conditional probability of word, given previous word."
    try:
        return Pw2[prev + ' ' + word]/float(Pw[prev])
    except KeyError:
        return Pw(word)

def bigram_prob(words):
    return product(cPw(word, prev)
                   for prev, word in zip(['<S>'] + words, words))

## bigram_prob('when in the course'.split())
#. 3.2269955740033603e-10

import math
## -math.log(3.2269955740033603e-10, 2)
#. 31.529089349780651

## map(Pw, 'when in the course'.split())
#. [0.00063480918127341898, 0.008263573669766917, 0.022573582340740989, 0.00017365129903887668]

