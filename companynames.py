"""
Generate random Web2.0 company names, along with a plausibility rating
for each.
Run companynames.sh first to grab the data.
(Quick-and-dirty hack.)
"""

import math
import operator
import random
import re

N = 3                        # Markov model order
nwords = 10000               # How many names to generate
min_length = 5               # Print only names at least this long
max_length = 10              # and no longer than this
penalize_length = True       # If true, longer names get worse ratings

def main():
    for i in range(nwords):
        name = gen_name()
        print '%5.2f %s' % (cross_entropy(name), name.encode('utf8'))

def cross_entropy(name):
    p = model_probability(name)
    e = -math.log10(p)
    return e if penalize_length else e/len(name)

def model_probability(name):
    return product(cPw(ng[-1], ng[:-1])
                   for ng in ngrams(wrap(name)))

def product(numbers):
    return reduce(operator.mul, numbers, 1)

def cPw(letter, prefix):
    choices = collect_choices(prefix)
    return float(choices[letter]) / sum(choices.values())

def gen_name():
    for candidate in gen_lots():
        if is_acceptable(candidate):
            return candidate

def is_acceptable(candidate):
    return (candidate.isalpha()
            and min_length <= len(candidate) <= max_length
            and candidate not in companynames)

def gen_lots():
    while True:
        yield gen()

def gen():
    state = '#' * N
    rv = ''
    while len(rv) <= 25:
        state = state[1:]
        letter = pick_next(state)
        if letter == '#':
            break
        rv += letter
        state += letter
    return rv

def pick_next(state):
    return weighted_choice(collect_choices(state))

def collect_choices(state):
    choices = {}
    for c in alphabet:
        if state+c in counts:
            choices[c] = counts[state+c]
    return choices

def weighted_choice(choices):
    r = random.randint(0, sum(choices.values()))
    for choice, k in choices.items():
        r -= k
        if r <= 0:
            return choice
    raise Exception("Can't happen")

def ngrams(string):
    return [string[i:i+N] for i in range(len(string) - N + 1)]

def clean(string):
    return re.sub(r'&amp;', '&', string.lower())

def wrap(name):
    return '#'*(N-1) + name + '#'

companynames = set(clean(unicode(line.rstrip('\n'), 'utf8'))
                   for line in open('companynames'))
counts = {}
for name in companynames:
    for ngram in ngrams(wrap(name)):
        counts[ngram] = counts.get(ngram, 0) + 1

alphabet = set(''.join(counts.keys()))

## gen()
#. u'hertionet'

main()
#. 1.14 senes
#. 1.28 actuvus
#. 0.86 prons
#. 0.98 softwevox
#. 0.94 zooks
#. 1.39 litspa
#. 1.26 auffby
#. 0.96 edion
#. 0.83 stedia
#. 0.89 tecties
#. 
