import itertools
import random

def main():
    #load(open('2gm-common6'))
    #load(open('3gm-bible'))
    load(open('4gm-bible'))
    print babble(100)

def start(tokens=('<S>',)):
    n = the_order()
    tokens = tokens[-n:]
    lt = len(tokens)
    if lt == n:
        return tokens
    candidates = [state
                  for state in ngrams.iterkeys()
                  if state[:lt] == tokens]
    assert candidates
    return random.choice(candidates)
    
def the_order():
    for state in ngrams.iterkeys():
        return len(state)
    assert False

def babble(nwords, state=None):
    if not state: state = start()
    return ' '.join(state + tuple(itertools.islice(babbling(state), nwords)))

def babbling(state):
    while True:
        word = pick_word2(state)
        yield word
        state = update(state, word)

def update(state, word):
    return state[1:] + (word,)

def all_successors(state):
    total, d = ngrams[state]
    return d.iterkeys()

def pick_word2(state):
    total, d = ngrams[state]
    return pick_word(d, total)

def pick_word(d, total):
    k = random.randint(0, total-1)
    for word, count in d.iteritems():
        k -= count
        if k <= 0:
            return word
    raise Exception("Can't happen")

ngrams = {}
                        
def load(file, good_words=None):
    ng = {}
    for line in file:
        wordstr, countstr = line.split('\t')
        words = tuple(wordstr.split())
        if good_words and not all(word in good_words for word in words):
            continue
        ng.setdefault(words[:-1], {})[words[-1]] = int(countstr)
    global ngrams
    ngrams = dict((state, (sum(d.itervalues()), d))
                  for state, d in ng.iteritems())

if __name__ == '__main__':
    main()
