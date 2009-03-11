"""
Analyze the Gutenberg Project's Bible text into sentences and words.
We consider a verse to be a sentence: starting at a verse number like
1:23 and ending at the next verse or blank line.

Output an n-gram table.
"""

import itertools
import re
import sys

def main():
    # print_tokens()
    # count_bigrams()
    count_ngrams(4)

def print_tokens():
    for token in enum_bible_tokens(sys.stdin):
        print token

def count_ngrams(n):
    d = {}
    state = ()
    for token in enum_bible_tokens(sys.stdin):
        word = token if token == '<S>' else token.lower()
        if n-1 == len(state):
            key = state + (word,)
            d[key] = d.get(key, 0) + 1
            state = state[1:] + (word,)
        else:
            state = state + (word,)
    for words, count in d.iteritems():
        sys.stdout.write('%s\t%d\n' % (' '.join(words), count))

def enum_bible_tokens(lines):
    for para in enum_paragraphs(lines):
        for verse in enum_verses(para):
            yield '<S>'
            for token in verse:
                yield token

def enum_paragraphs(lines):
    para = []
    for line in lines:
        line = line.strip()
        if line:
            para.append(line)
        elif para:
            yield '\n'.join(para)
            para = []
    if para:
        yield '\n'.join(para)

def enum_verses(paragraph):
    versenum = r'\d+:\d+'
    tokens = re.findall(versenum + r"|['\w]+", paragraph)
    groups = itertools.groupby(tokens, re.compile(versenum).match)
    first_group = True
    for is_versenum, verse_tokens in groups:
        if not first_group:
            if not is_versenum:
                yield [t.strip("'") for t in verse_tokens]
        first_group = False

if __name__ == '__main__':
    main()
