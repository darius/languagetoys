"""
Given a line of space-separated words, permute them into their most
probable order according to a language model. Also output the log-
probability.

This is meant for ranking anagrams from an anagram generator.
"""

import math
import operator
import sys

import bigram
import pdist

def main():
    best_score = best_bigram_score
    for line in sys.stdin:
        score, words = best_score(line.lower().split())
        print '%g\t%s' % (score, ' '.join(words))

def best_bigram_score(words):
    if len(words) == 1:
        score = pdist.Pw(words[0])
    else:
        score, words = max(map(bigram_score, permutations(words)))
    return -math.log(score, 2), words

def bigram_score(words):
    return bigram_prob(words), words

def bigram_prob(words):
    return product(pdist.cPw(word, prev)
                   for prev, word in zip(['<S>'] + words, words))

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
