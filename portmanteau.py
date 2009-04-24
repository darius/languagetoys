"""
Let's find pairs of words that blend nicely, like
book + hookup --> bookup

Usage:
$ python portmanteau.py >output
Takes around 40 seconds on a 2008-vintage laptop.
Alternatively:
$ python portmanteau.py my-dictionary-filename >output

Strategy: given a wordlist, first remove generative affixes like un-
and -ly. Find all reasonably-long substrings of every word. Match
suffixes of candidate first words with midparts of candidate second
words.

TODO: get better at stripping affixes
  (though that's not always a win: e.g.:
  contendresse                   contendress + tendresse)
  (also: bunchawed from bunch and unchawed)
Solution: don't strip affixes from the dictionary. Instead,
filter out portmanteaus with unshared parts that are merely
sequences of affixes. (This ought to help us to be more relaxed
in our affix-matching, too -- not as big a deal when we're 
too aggressive?)
Note however that this would produce multiple affix-variants of a
portmanteau, that need to be cut down for presentation.
Also: the last check in is_root_word,
    if p in raw_words and s in raw_words:
is overeager.

TODO: currently we're matching suffixes against prefixes instead
of midparts, so the motivating example above doesn't even appear...

TODO: the pronunciations should blend, not just the spelling.
"""

import math
import re
import sys

import pdist

if len(sys.argv) == 2:
    dictionary_filename = sys.argv[1]
else:
    dictionary_filename = '/usr/share/dict/words'

def print_all_portmanteaus():
    for score, (s, p, affix) in sorted(all_portmanteaus()):
        combo = s + p[len(affix):]
        print '  %6.2f %-30s %s + %s' % (score, combo, s, p)

def all_portmanteaus():
    words = [w for w in raw_words if is_root_word(w) and 3 < len(w)]
    suffixes = group(all_suffixes(words))
    for affix, p in all_prefixes(words):
        if affix in suffixes:
            suffix_words = suffixes[affix]
            for s in suffix_words:
                if is_portmanteau(s, p, affix):
                    yield score(s, p, affix), (s, p, affix)

def group(pairs):
    table = {}
    for k, v in pairs:
        table.setdefault(k, []).append(v)
    return table

def is_portmanteau(s, p, affix):
    return (not p.startswith(s) and not s.endswith(p)
            and (s + p[len(affix):]) not in raw_words)

def score(s, p, affix):
    L = len(s) + len(p) - len(affix)
    return -math.log10(pdist.Pw(s) * pdist.Pw(p) * 16**(-float(L)/len(affix)))

def all_prefixes(words):
    return ((w[:i], w) for w in words for i in range(3, len(w)+1))

def all_suffixes(words):
    return ((w[i:], w) for w in words for i in range(len(w)-3))

left_noise = """
  be bi em en di duo im iso non oct octo out pre quad quadra quadri re
  sub tri un uni
""".split()
right_noise = """
  ability able adian age an ation d ed en ent er es escent ful ian ic
  ies ily iness ing ish ite ize less let log like liness ly ness og
  ogy proof r ress ry s ship tion y
""".split()

def is_root_word(w):
    "Return true iff w has no affixes."
    for ln in left_noise:
        if w.startswith(ln) and w[len(ln):] in raw_words:
            return False
    for rn in right_noise:
        if w.endswith(rn) and w[:-len(rn)] in raw_words:
            return False
    for i in range(2, len(w)-1):
        p, s = w[:i], w[i:]
        if p in raw_words and s in raw_words:
            return False
    return True

raw_words = set(unicode(line.rstrip('\n'), 'utf8').lower()
                for line in open(dictionary_filename))


print_all_portmanteaus()
