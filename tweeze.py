"""
Try to produce manglings like "Tweeze denied beef worker isthmus".
"""
from memo import memo
from pdist import Pw
from math import log10

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
## pronounce_all(('darius',))
#. ('d', 'er0', 'ay1', 'ah0', 's')
## annotated_pronounce_all(('darius','is','great'))
#. (('d', 'er0', 'ay1', 'ah0', 's', 'ih1', 'z', 'g', 'r', 'ey1', 't'), ('darius', None, None, None, None, 'is', None, 'great', None, None, None))

## transcribe(*annotated_pronounce_all(tuple("stirring not even a mouse".split())))
#. (21.741929954664087, ('staying', 'note', 'ave', 'mass'))
## transcribe(*annotated_pronounce_all(tuple("snug in their beds with visions".split())))
#. (43.36161186892771, ('snag', "'n", 'there', 'bids', 'wythe', 'versions'))
## transcribe(*annotated_pronounce_all(tuple("syne".split())))
#. (56.71069362546324, ('syne',))

longest = 20
match_cost = 25
fit_cost = 4
rarity_cost = 1
roughened_cost = 1

## transcribe(*annotated_pronounce_all(tuple("the light".split())))
#. (56.50999260901199, ('the', 'let'))

## pronounce_all(tuple("the light".split()))
#. ('dh', 'ah0', 'l', 'ay1', 't')

def compute_best(phones, bounds, costs, seqs, i):
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
        for word in rough_words.get(roughen(phones[i-L:i]), ()):
            if word not in exacts:
                add(word, subcost + roughened_cost)
    return min(attempts) if attempts else (1e6, ('XXX',))

def transcribe(phones, bounds):
    """Return (cost,words) where pronounce_all(words) matches
    `phones`. `cost` is lower the better the match. Try to find the
    lowest cost."""
    assert len(phones) == len(bounds)
    costs, seqs = [0], [()]
    for i in range(1, len(phones) + 1):
        cost, seq = compute_best(phones, bounds, costs, seqs, i)
        costs.append(cost)
        seqs.append(seq)
    return costs[-1], seqs[-1]


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
#    print text
#    print phones
#    print len(phones)
    cost, words = transcribe(phones, bounds)
    print cost
    print textwrap.fill(' '.join(words).lower(), 60)

if __name__ == '__main__':
    main()
