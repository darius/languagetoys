import itertools
import random

#import pdist

## babble(10)
#. 'india next pics level at the and directly on the'

## babble2(10)
#. 'watching the trap of the site to go to eat'

def main():
    # print babble(100)
    print babble2(100)

def babble2(n):
    return ' '.join(itertools.islice(babbling(), n))

def babbling(state='<S>'):
    while True:
        word = pick_word2(state)
        yield word
        state = word

def pick_word2(prev):
    total, d = bigrams[prev]
    return pick_word(d, total)

def babble(n):
    return ' '.join(pick_word(vocab, vocab_total) for i in range(n))

def pick_word(d, total):
    k = random.randint(0, total-1)
    for word, count in d.iteritems():
        k -= count
        if k <= 0:
            return word
    raise Exception("Can't happen")

vocab = {}
for line in open('vocab_canon_cs_3'):
    word, countstr = line.split('\t')
    vocab[word] = int(countstr)
vocab_total = sum(vocab.itervalues())

bigrams = {}
for line in open('2gm-common6'):
    words, countstr = line.split('\t')
    word1, word2 = words.split()
    bigrams.setdefault(word1, {})[word2] = int(countstr)
bigrams = dict((word1, (sum(d.itervalues()), d))
               for word1, d in bigrams.iteritems())

if __name__ == '__main__':
    main()
