"""
Find a high-probability sequence of words whose lengths express a
sequence of digits. (0-digits appear as words of length 10.)
Inspired by the pi mnemonic "How I wish I could enumerate pi easily..."
I think I messed up the Viterbi algorithm here, besides all the
usual current suckage for this package.
"""

import heapq
from math import log10

from pdist import Pdist, datafile, memo, Memo

def forbid_unknowns(key, N):
    "Estimate the probability of an unknown word as 0."
    return 1e-9

def cPw(word, prev):
    "Conditional probability of word, given previous word."
    try:
        return Pw2[prev + ' ' + word] / float(Pw[prev])
    except KeyError:
        return 1e-9              # No unknown combos either

def cPww(word, prev1, prev2):
    "Conditional probability of word, given twe previous words."
    prev = prev1 + ' ' + prev2
    try:
        return Pw3[prev + ' ' + word] / float(Pw2[prev])
    except KeyError:
        return 1e-9              # No unknown combos either

# About 7% of 5gram counts missing
#NT = 1024908267229 ## Number of tokens
#Pw  = Pdist(datafile('vocab_canon_cs_3'), NT, forbid_unknowns)
#Pw2 = Pdist(datafile('2gm-common6'), NT)

#NT = 641241
#Pw  = Pdist(datafile('vocab_austen'), NT, forbid_unknowns)
#Pw2 = Pdist(datafile('2gm-austen'), NT)

#NT = 475637
#Pw  = Pdist(datafile('vocab_tolkien'), NT, forbid_unknowns)
#Pw2 = Pdist(datafile('2gm-tolkien'), NT)
#Pw3 = Pdist(datafile('3gm-tolkien'), NT)

NT = 821133
Pw  = Pdist(datafile('vocab_bible'), NT, forbid_unknowns)
Pw2 = Pdist(datafile('2gm-bible'), NT)
Pw3 = Pdist(datafile('3gm-bible'), NT)

def main(argv):
    write_mnemonic(argv[0])

def write_mnemonic(s):
    import formatter
    f = formatter.DumbWriter()
    f.send_flowing_data(format(mnemonify3(s)))
    f.send_line_break()
    f.flush()

def format(tokens):
    out = ''
    for t in tokens:
        if not out and t == '<S>':
            pass
        elif not out:
            out = t.capitalize()
        elif t == '<S>':
            out = out + '.'
        elif out[-1] == '.':
            out = out + ' ' + t.capitalize()
        else:
            if t == 'i': t = 'I'
            out = out + ' ' + t
    return out

def mnemonify1(digits):
    for digit in digits:
        yield max(candidates(digit), key=Pw)


words2 = {}
for words, count in Pw2.iteritems():
    word = words.split()[1]
    if 1 <= len(word) <= 10 and word != '<S>' and word != '<s>': # XXX wtf
        if len(word) != 1 or word in ('a', 'i', 'o'):
            words2[word] = words2.get(word, 0) + count
length = [[] for i in range(10)]
for word in words2.iterkeys():
    L = len(word) % 10
    length[L].append(word)
for i in range(10):
    length[i] = heapq.nlargest(60, length[i], words2.get)

def candidates(digit):
    return length[int(digit) % 10]

def splits(s):
    return ((s[:i], s[i:]) for i in range(max(0, len(s) - sentence_limit),
                                          len(s)))

sentence_limit = 30

def dump():
    for k, v in sorted(mnemonifying.memo.items(),
                       key=lambda (k,v): len(k[0])):
        print k[0]
        for k1, v1 in sorted(v):
            print '  ', k1, v1


########################################

def mnemonify3(digits):
    return m3(digits)[1]

@memo
def m3(digits):
    if len(digits) < 3: return m2(digits)
    return max(extend3(combine3(m3(L), '<S>'), R)
               for L, R in splits(digits))

@memo
def extend3(before, digits):
    if not digits: return before
    if len(digits) == 1:
        return max(combine3(before, c) for c in candidates(digits[-1]))
    if len(digits) == 2:        # XXX um
        return max(combine3(combine3(before, c2), c1)
                   for c2 in candidates(digits[-2])
                   for c1 in candidates(digits[-1]))
    prevresult = extend3(before, digits[:-3])
    # XXX this is stupid
    return max(combine3(combine3(combine3(prevresult, c3), c2), c1)
               for c3 in candidates(digits[-3])
               for c2 in candidates(digits[-2])
               for c1 in candidates(digits[-1]))

def combine3((logprob, words), word):
    if len(words) < 2:
        return combine2((logprob, words), word)
    return (logprob + log10(cPww(word, words[-2], words[-1])),
            words + (word,))


########################################

def mnemonify2(digits):
    return m2(digits)[1]

@memo
def m2(digits):
    if not digits: return (0.0, ())
    return max(extend2(combine2(m2(L), '<S>'), R)
               for L, R in splits(digits))

@memo
def extend2(before, digits):
    if not digits: return before
    if len(digits) == 1:
        return max(combine2(before, c) for c in candidates(digits[-1]))
    prevresult = extend2(before, digits[:-2])
    return max(combine2(combine2(prevresult, c2), c1)
               for c2 in candidates(digits[-2])
               for c1 in candidates(digits[-1]))

def combine2((logprob, words), word):
    if words:
        prevword = words[-1]
    else:
        if word == '<S>':
            return (logprob, (word,))
        prevword = '<S>'
    return (logprob + log10(cPw(word, prevword)),
            words + (word,))


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
