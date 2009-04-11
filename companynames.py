"""
Random Web2.0 company names.
Run companynames.sh first to grab the data.
(Quick-and-dirty hack.)
"""

import random
import re

N = 3                           # Markov model order
nwords = 20                     # How many names to generate
min_length = 5                  # Print only names at least this long
max_length = 9

def main():
    for i in range(nwords):
        print gen_name().encode('utf8')
    
def gen_name():
    for candidate in gen_lots():
        if is_acceptable(candidate):
            return candidate

def is_acceptable(candidate):
    return (candidate.isalpha()
            and min_length <= len(candidate) <= max_length)

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
    choices = {}
    for c in alphabet:
        if state+c in counts:
            choices[c] = counts[state+c]
    return weighted_choice(choices)

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

counts = {}
for line in open('companynames'):
    line = clean(unicode(line.rstrip('\n'), 'utf8'))
    for ngram in ngrams('#' * (N-1) + line + '#'):
        counts[ngram] = counts.get(ngram, 0) + 1

alphabet = set(''.join(counts.keys()))

## gen()
#. u'socusitale low.prne'

main()
#. diand
#. gieno
#. eadvet
#. mygmx
#. whabs
#. digge
#. terit
#. endeo
#. ndnzi
#. linostr
#. hedignica
#. foterco
#. myellc
#. brick
#. lagiend
#. pcare
#. clata
#. listia
#. nolia
#. talab
#. 
