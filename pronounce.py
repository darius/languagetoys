import itertools
import re

phone_dict = {}
for line in open('cmudict.0.7a'):
    if ';;' in line: continue
    s = line.split()
    if not s: continue
    word, phones = s[0], s[1:]
    phone_dict[word] = tuple(phones)

vowels = frozenset('AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW'.split())

def is_vowel(phone):
    return phone[-1] in '012'

def pronounce(word):
    return phone_dict[word.upper()]

def phonetic(word):
    return ' '.join(pronounce(word))

def known_words():
    return phone_dict.iterkeys()

def main():
    import sys
    for line in sys.stdin:
        for word in re.findall(r"['\w]+", line):
            print phonetic(word)

if __name__ == '__main__':
    main()
