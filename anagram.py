"""
Generate multi-word anagrams.

$ python anagram.py a dam
dam/mad a
Adam
am ad
"""

import re
import string

# Configure me by editing these constants:
dict_filename = 'wordlist.txt'
write_in_expanded_form = True

def main(argv):
    input = ' '.join(argv[1:]).lower()
    global dictionary, dictionary_prefixes
    dictionary, dictionary_prefixes = load(dict_filename, input)
    write_anagrams(input)

# We check fewer possibilities overall if we consider the most-
# constraining letters first: the letters that appear in the
# fewest words. These transcribe strings to and from an alphabet
# sorted most-constraining first:
alphabet      = 'qjxzwkvfybhmpgudclotnrsaie'
untranscriber = string.maketrans(string.ascii_lowercase, alphabet)
transcriber   = string.maketrans(alphabet, string.ascii_lowercase)
def transcribe(s):   return s.translate(transcriber)
def untranscribe(s): return s.translate(untranscriber)

## transcribe('etaonrish')
#. 'ztxsuvywk'
## transcribe('quux a xanthic jove')
#. 'aooc x cxutkyq bsgz'

def pigeonhole(word):
    "Two words have the same pigeonhole iff they're anagrams of each other."
    return ''.join(sorted(word))

def load(filename, subject=None):
    "Read in a word-list, one word per line. Prune it wrt subject."
    pigeonholes = {}
    prefixes = set()
    identity = ''.join(map(chr, range(256)))
    nonalpha = ''.join(set(identity) - set(string.ascii_lowercase))
    usable = usable_pattern(subject)
    def add(word):
        if not usable(word): return
        canon = word.lower().translate(identity, nonalpha)
        hole = pigeonhole(transcribe(canon))
        pigeonholes.setdefault(hole, []).append(word)
        for i in range(1, len(hole)+1):
            prefixes.add(hole[:i])
    for line in open(filename):
        add(line.rstrip('\n'))
    # 'a' and 'I' happen not to be in my wordlist file:
    if transcribe('a') not in pigeonholes: add('a')
    if transcribe('i') not in pigeonholes: add('I')
    return pigeonholes, prefixes

def usable_pattern(subject):
    """Return a predicate that accepts words that could be part of an
    anagram of subject. (But a None subject could be anything.) This
    is to prune the dictionary to speed things up a bit."""
    if subject is None:
        return lambda word: True
    alphabet = set(extract_letters(subject))
    pattern = re.compile('([%s]|\W)+$' % ''.join(alphabet), re.I)
    return pattern.match

dictionary, dictionary_prefixes = None, None
#dictionary, dictionary_prefixes = load(dict_filename)

## pt = lambda word: pigeonhole(transcribe(word))
## pt('hel') in dictionary_prefixes, pt('hel') in dictionary
#. (True, False)
## pt('hello') in dictionary_prefixes, pt('hello') in dictionary
#. (True, True)

### write_anagrams('aworld')

def write_anagrams(s):
    for pigeonholes in gen_anagrams(s):
        if write_in_expanded_form:
            for words in cross_product(map(dictionary.get, pigeonholes)):
                print ' '.join(words)
        else:
            print ' '.join('/'.join(dictionary[p]) for p in pigeonholes)

def cross_product(lists):
    if not lists:
        yield []
    else:
        for xs in cross_product(lists[1:]):
            for x in lists[0]:
                yield [x] + xs

def gen_anagrams(s):
    """Generate the anagrams of s in sorted order, each anagram itself
    sorted, and each such anagram appearing exactly once. An anagram
    is represented as a tuple of pigeonhole names."""
    bag = extract_letters(transcribe(s))
    return extend((), '', bag, '') if bag else ()

def extend(acc, wp, rest, bound):
    """Generate all the anagrams of the nonempty bag 'rest' that
    extend acc with a word starting with wp, the remainder of wp
    being lexicographically >= bound. As with gen_anagrams(), each
    anagram is sorted and they appear in sorted order."""
    for letter, others in each_distinct_letter(rest):
        if bound[0:1] <= letter:
            wp1 = wp + letter
            if wp1 in dictionary_prefixes:
                bound1 = bound[1:] if bound[0:1] == letter else ''
                if not bound1 and wp1 in dictionary:
                    acc1 = acc + (wp1,)
                    if others:
                        for result in extend(acc1, '', others, wp1):
                            yield result
                    else:
                        yield acc1
                if others:
                    for result in extend(acc, wp1, others, bound1):
                        yield result

def extract_letters(s):
    return make_bag(c for c in s.lower() if c.isalpha())

def make_bag(letters):
    return ''.join(sorted(letters))

def each_distinct_letter(bag):
    """Generate (letter, bag-minus-one-of-that-letter) for each
    different letter in the bag."""
    prefix = ''
    for i, letter in enumerate(bag):
        if 0 == i or letter != bag[i-1]:
            yield letter, bag[:i] + bag[i+1:]

## list(each_distinct_letter('eehlloo'))
#. [('e', 'ehlloo'), ('h', 'eelloo'), ('l', 'eehloo'), ('o', 'eehllo')]

if __name__ == '__main__':
    import sys
    main(sys.argv)
