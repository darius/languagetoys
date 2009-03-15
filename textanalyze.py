"""
Analyze a text into sentences and words. Our crude notion of a
sentence: text up to a period (except for Mr./Mrs./Dr.) or blank line.

Output an n-gram table.
"""

import itertools
import re
import sys

def main(argv):
    #print_tokens()
    # count_bigrams()
    count_ngrams(int(argv[0]))

def print_tokens():
    for token in squeeze(enum_tokens(sys.stdin)):
        print token

def count_ngrams(n):
    d = {}
    state = ()
    for token in squeeze(enum_tokens(sys.stdin)):
        word = token if token == '<S>' else token.lower()
        state += (word,)
        if n == len(state):
            d[state] = d.get(state, 0) + 1
            state = state[1:]
    for words, count in d.iteritems():
        sys.stdout.write('%s\t%d\n' % (' '.join(words), count))

def squeeze(tokens):
    prev = None
    for t in tokens:
        if not t:
            continue
        if t == '<S>' and prev == '<S>':
            continue
        yield t
        prev = t

def enum_tokens(lines):
    yield '<S>'
    for line in lines:
        if not line.strip('\n'):
            yield '<S>'
        else:
            for t in re.findall(r"Mrs?[.]|Dr[.]|[.?!]|['a-zA-Z0-9]+", line):
                if t in '.?!':
                    # XXX inaccurate
                    yield '<S>'
                else:
                    yield t.rstrip('.').strip("'")

if __name__ == '__main__':
    main(sys.argv[1:])
