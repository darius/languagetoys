"""
Text summarization scheme

For each block of text, induce a 'local' language model. Also, get a
global language model -- either for the particular corpus, or for
English, etc. For each block, find the query (small bag of words) that
best picks out that block's language model (as in Ch. 12 of _Intro to
Info Retrieval_). 

(Original plan: then arrange those words in a plausible order, like
I've done for anagrams. This last step probably won't go so well since
there won't be enough 'noise' words (grammatical support thingies). So
this code sticks with the obvious sort by importance.

Plus ad-hoc hacks to process The Lord of the Rings in particular.
"""

import collections
import glob
import heapq
import re

smoothing = 100
lotr_is_global = True

def words(text):
    return (word
            for word in re.findall('[A-Za-z]+', text)
            if 1 < len(word) or word.lower() in ('a', 'i'))

def train(features):
    model = collections.defaultdict(lambda: smoothing)
    for f in features:
        model[f] += 1
    return model

if lotr_is_global:
    gcounts = train(words(open('tolkien0.txt').read().lower()))
    gn = float(sum(gcounts.values()))
else:
    def datafile(name, sep='\t'):
        "Read key,value pairs from file."
        for line in file(name):
            yield line.split(sep)
    gcounts = collections.defaultdict(lambda: smoothing)
    for key, count in datafile('../vocab_canon_cs_3'):
        gcounts[key] += int(count)
    gn = float(sum(gcounts.values()))

capcounts = train(words(open('tolkien0.txt').read()))

def maybe_capitalize(word):
    wl = word.lower()
    wc = word.capitalize()
    if wl in gcounts or wc in gcounts:
        return max([wl, wc], key=capcounts.get)
    return word

def do_all():
#    print gsummarize()
    for filename in glob.glob('chapters/*'):
        text = open(filename).read().lower()
        print chunk_name(filename), summarize(text)

def gsummarize():
    def datafile(name, sep='\t'):
        "Read key,value pairs from file."
        for line in file(name):
            yield line.split(sep)
    hcounts = collections.defaultdict(lambda: smoothing)
    for key, count in datafile('../vocab_canon_cs_3'):
        hcounts[key] += int(count)
    hn = float(sum(hcounts.values()))
    def candidates():
        for word in gcounts:
            gp = gcounts[word] / gn
            hp = hcounts[word] / hn
            if 100 + smoothing < gcounts[word]:
                yield gp/hp, word
    return ' '.join(maybe_capitalize(word)
                    for m, word in heapq.nlargest(8, candidates()))

def summarize(text):
    lcounts = train(words(text))
    ln = float(sum(lcounts.values()))
    cs = candidates(lcounts, ln)
    return ' '.join(maybe_capitalize(word)
                    for m, word in heapq.nlargest(8, cs))

def chunk_name(filename):
    dir, rest = filename.split('/')
    return rest.split()[0]

import math

def candidates(lcounts, ln):
    for word in lcounts:
        if lcounts[word] - smoothing < 3:
            continue
        lp = lcounts[word] / ln
        # Here we use a global model consisting of all the text
        # EXCEPT the local-modeled text, plus a smoothing term:
        if lotr_is_global:
            gp = (gcounts[word] - lcounts[word] + smoothing) / (gn - lcounts[word])
        else:
            gp = gcounts[word] / gn
        m = lp/gp * (lp)  # the *lp is totally ad-hoc, sigh
#        print lp/gp, math.log(lp), lp/gp * math.log(lp), word
        yield m, word
#        if gp < gcounts['said'] / gn:
#            yield lp, word

def the_list():
    for m, word in sorted(candidates(), reverse=True):
        print '%.6f %3d %s' % (m, lcounts[word], word)

def main():
    print ' '.join(word for m, word in heapq.nlargest(9, candidates()))

if __name__ == '__main__':
#    main()
    do_all()
