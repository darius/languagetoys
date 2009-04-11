"""
Given a line of space-separated words, permute them into their most
probable order according to a language model. Also output the log-
probability.

This is meant for ranking anagrams from an anagram generator.
"""

import math
import operator
import re
import sys

import bigram

def main():
    best_score = unigram_score
    best_score = best_bigram_score
    for line in sys.stdin:
        score, words = best_score(line.lower().split())
        print '%g\t%s' % (score, ' '.join(words))

def read_dictionary(file):
    "Return a map from words to their costs."
    costs = {}
    for line in file:
        coststr, word = line.split()
        word = normalize(word)
        # TODO: compute combined cost, not min
        costs[word] = min(float(coststr), costs.get(word, 1000.0))
    return costs

def normalize(word):
    "Put word in standard form to avoid trivial mismatches."
    return re.sub(r'[^a-z]+', '', word.lower())

dictionary = read_dictionary(open('combined.photonet3'))
unknown_score = max(dictionary.values()) + 0.1

bigram_model = bigram.BigramModel()
bigram_model.load(open('bigdict'))

# def unigram_score(words):
#     return (sum(dictionary.get(word, unknown_score)
#                 for word in words),
#             words)

import pdist

def unigram_score(words):
    p = reduce(operator.mul, map(pdist.Pw, words), 1)
    return -math.log(p, 2), words

def best_bigram_score(words):
    if len(words) == 1: return unigram_score(words)
    score, words = max(map(bigram_score, permutations(words)))
    return (-math.log(score, 2), words)

cache = {}
def P(key):
    if key not in cache:
        cache[key] = bigram_model.p(*key)
    return cache[key]

def bigram_score(words):
    return bigram_prob(words), words

#def bigram_score(words):
#    return (product(map(P, zip(words[:-1], words[1:]))),
#            words)

def bigram_prob(words):
    return product(pdist.cPw(word, prev)
                   for prev, word in zip(['<S>'] + words, words))

## bigram_prob('when in the course'.split())
#. 3.2269955740033603e-10

def product(xs):
    return reduce(operator.mul, xs, 1)

def permutations(items):
    return combinations(items, len(items))

def combinations(items, n):
    if n == 0:
        yield []
    else:
        for i in xrange(len(items)):
            for cc in combinations(items[:i] + items[i+1:], n-1):
                yield [items[i]] + cc

if __name__ == '__main__':
    main()
