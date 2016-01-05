"""
Try to produce manglings like "Tweeze denied beef worker isthmus".
"""
import re, sys, textwrap
from math import log10

from memo import memo
from pdist import Pw
from simpleverse import find_rime

roughener = {
    'd': 't', 'dh': 't', 'th': 't',
    'l': 'r',
    'sh': 's', 'z': 's', 'zh': 's',
}

def roughen(phones):
    return tuple(p[-1] if p[-1].isdigit() else roughener.get(p, p)
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
        words_of_phones[word,] = [word]
    return phones_of_word[word]

def pronounce_all(words):
    return sum(map(pronounce, words), ())

def pronounce_line(words):
    phones, bounds = (), ()
    for word in words:
        p = pronounce(word)
        phones += p
        bounds += (word,) + (None,)*(len(p)-1)
    return phones, bounds

def roughen_line(phones, rhyming):
    "Roughen phones, except maybe preserving the rime at the end."
    i = find_rime(phones) if rhyming else len(phones)
    return roughen(phones[:i]) + phones[i:]

## pronounce('yay')
#. ('y', 'ey1')
## pronounce_all(('darius',))
#. ('d', 'er0', 'ay1', 'ah0', 's')

longest = 20
match_cost = 25
fit_cost = 5
rarity_cost = 5
roughened_cost = 5

## pronounce_all(tuple("the light".split()))
#. ('dh', 'ah0', 'l', 'ay1', 't')

def compute_best(phones, rough_phones, bounds, costs, seqs, i):
    attempts = []
    for L in range(1, min(i, longest) + 1):
        assert len(phones[:i-L]) < len(phones)
        subcost, subwords = costs[i-L], seqs[i-L]
        subcost += fit_cost*(None is not bounds[i-L])
        def add(word, common_cost):
            attempts.append((common_cost - rarity_cost*log10(Pw(word)) + match_cost*(word == bounds[i-L]),
                             subwords + (word,)))
        exacts = words_of_phones.get(phones[i-L:i], ())
        for word in exacts:
            add(word, subcost)
        for word in rough_words.get(rough_phones[i-L:i], ()):
            if word not in exacts:
                add(word, subcost + roughened_cost)
    return min(attempts) if attempts else (1e6, ('XXX',))

def transcribe(phones, rough_phones, bounds):
    """Return (cost,words) where pronounce_all(words) matches
    `phones`. `cost` is lower the better the match. Try to find the
    lowest cost."""
    assert len(phones) == len(bounds)
    costs, seqs = [0], [()]
    for i in range(1, len(phones) + 1):
        cost, seq = compute_best(phones, rough_phones, bounds, costs, seqs, i)
        costs.append(cost)
        seqs.append(seq)
    return costs[-1], seqs[-1]


## -log10(Pw('the'))
#. 1.6506163745527287
## -log10(Pw('felonious'))
#. 7.04004028985589
## -log10(Pw('dar'))
#. 5.644601987828583

def pronounce_lines(lines, rhyming):
    phones, rough_phones, bounds = (), (), ()
    for line in lines:
        p, b = pronounce_line(re.findall(r"['\w]+", line.lower()))
        phones += p
        rough_phones += roughen_line(p, rhyming)
        bounds += b
    return phones, rough_phones, bounds

def main(argv):
    rhyming = (argv[1:] == ['--rhyme'])
    phones, rough_phones, bounds = pronounce_lines(sys.stdin, rhyming)
#    print text
#    print phones
#    print rough_phones
#    print len(phones)
    cost, words = transcribe(phones, rough_phones, bounds)
    print cost
    print textwrap.fill(' '.join(words).lower(), 60)

if __name__ == '__main__':
    main(sys.argv)
