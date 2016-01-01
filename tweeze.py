"""
Try to produce manglings like "Tweeze denied beef worker isthmus".
"""
import sys; sys.setrecursionlimit(8000)

from memo import memo
from pdist import Pw
from math import log10

def roughen(phones):
    return tuple(p[-1] if p[-1].isdigit() else p
                 for p in phones)

phones_of_word = {}
words_of_phones = {}
rough_words = {}
for line in open('cmudict.0.7a'):
    if ';;' in line: continue
    s = line.lower().split()
    if not s: continue
    word, phones = s[0], tuple(s[1:])
    if word.endswith(')'): continue
    phones_of_word[word] = phones
    words_of_phones.setdefault(phones, []).append(word)
    rough_words.setdefault(roughen(phones), []).append(word)

def pronounce(word):
    if word not in phones_of_word:
        phones_of_word[word] = (word,)
        words_of_phones[word,] = word
    return phones_of_word[word]

def pronounce_all(words):
    return sum(map(pronounce, words), ())

def annotated_pronounce_all(words):
    phones, bounds = (), ()
    for word in words:
        i = len(phones)
        p = pronounce(word)
        phones += p
        bounds += (word,) + (None,)*(len(p)-1)
    return phones, bounds

## pronounce('yay')
#. ('y', 'ey1')

## pronounce('darius')
#. ('d', 'er0', 'ay1', 'ah0', 's')
## pronounce_all(('darius',))
#. ('d', 'er0', 'ay1', 'ah0', 's')
## annotated_pronounce_all(('darius','is','great'))
#. (('d', 'er0', 'ay1', 'ah0', 's', 'ih1', 'z', 'g', 'r', 'ey1', 't'), ('darius', None, None, None, None, 'is', None, 'great', None, None, None))

## transcribe(*annotated_pronounce_all(tuple("stirring not even a mouse".split())))
#. (20.543223182754616, ('staying', 'not', 'ave', 'mass'))
## transcribe(*annotated_pronounce_all(tuple("snug in their beds with visions".split())))
#. (28.03218602490996, ('snug', 'in', 'there', 'bids', 'with', 'versions'))
## transcribe(*annotated_pronounce_all(tuple("the light".split())))
#. (7.509992609011988, ('the', 'let'))

longest = 20

match_cost = 10

@memo
def transcribe(phones, bounds):
    """Return (cost,words) where pronounce_all(words) matches
    `phones`. `cost` is lower the better the match. Try to find the
    lowest cost."""
    if not phones: return 0, ()
    attempts = []
    for L in range(1, min(len(phones), longest) + 1):
#        print 'phones', phones
#        print bounds, L, bounds[-L]
        assert len(phones[:-L]) < len(phones)
        subcost,subwords = transcribe(phones[:-L], bounds[:-L])
        cost = 4*(None is bounds[-L])
        def add(word, common_cost):
#            print 'try', word, cost, -log10(Pw(word)), match_cost*(word == bounds[-L])
            attempts.append((common_cost - log10(Pw(word)) + match_cost*(word == bounds[-L]),
                             subwords + (word,)))
        exacts = words_of_phones.get(phones[-L:], ())
        for word in exacts:
            add(word, subcost + cost)
        for word in rough_words.get(roughen(phones[-L:]), ()):
            if word not in exacts:
                add(word, subcost + cost + 1)
    return min(attempts) if attempts else (1e6, ('XXX',))

## -log10(Pw('the'))
#. 1.6506163745527287
## -log10(Pw('felonious'))
#. 7.04004028985589
## -log10(Pw('dar'))
#. 5.644601987828583

def main():
    import re, sys, textwrap
    text = re.findall(r"['\w]+", sys.stdin.read().lower())
    phones, bounds = annotated_pronounce_all(text)
    print text
    print phones
    print len(phones)
    cost, words = transcribe(phones, bounds)
    print cost
    print textwrap.fill(' '.join(words).lower())

if __name__ == '__main__':
    main()
