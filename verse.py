import itertools
import operator
import random
import re
import string
import sys

import babble
import pronounce

#start_state = 'and'
start_state = '<S>'

# TODO: Can we just penalize unstressables (to varying degrees)
#  instead of banning them, and then include more words in this set?
unstressables = 'a an of the'.split()
unstressables += 'am and for in is on or that to with'.split()
unstressables += 'are as be by he him his her my she them us we'.split()
unstressables += 'its they their were you your'.split()
unstressables += 'at do did from i it me'.split()
unstressables += 'but had has have our shall was will'.split()
unstressables += 'dost hast hath shalt thee thou thy wilt ye'.split()
unstressables += 'if how what when where who why'.split()
unstressables += 'can so this though which'.split()
unstressables += 'could should would'.split()
unstressables += 'all like nor out too yet'.split()
unstressables += 'near through while whose'.split()
unstressables += 'these those'.split()
unstressables += 'came come'.split()
unstressables += 'none one two three four five six eight nine ten'.split()
unstressables += 'en et la may non off per re than un'.split()
unstressables = frozenset(unstressables)

def main():
    print_verse(gen_blank_verse())
    print_verse(gen_couplet())
    print_verse(gen_quatrain())
    print_verse(gen_limerick())
    print_verse(gen_neolithic())
    print_verse(gen_sonnet())
    
def print_verse(verse):
    for line in verse:
        print format_line(line)

def check_sonnet123():
    for line in open('sonnet123'):
        if not scans(line):
            words = re.findall(r"['\w]+", line)
            print match_words(words, iambic_pentameter)
            print line

def scans(line):
    words = re.findall(r"['\w]+", line)
    return match_words(words, iambic_pentameter) == ()

def lines_rhyme(line1, line2):
    return (line1[-1] != line2[-1]  # such rhymes are almost always weak
            and rhyme_matches(rhyme_phones(line1),
                              rhyme_phones(line2)))

def rhyme_matches(phones1, phones2):
    # XXX check that the onsets are different
    return onset(phones1) != onset(phones2) and rime(phones1) == rime(phones2)

def onset(phones):
    return '' if pronounce.is_vowel(phones[0]) else phones[0]

def rime(phones):
    return phones if pronounce.is_vowel(phones[0]) else phones[1:]

# M       A     D      L       A      D      EE
# //m   m/a/  m/a/d  m/a/dl  l/a/   l/a/d   d/ee/

def rhyme_phones(line):
    before = []
    vowels = []
    after  = []
    state = 'consonant'
    # XXX This only works for 'masculine' rhymes. And man the code sucks.
    for phone in pronounce_line(line):
        if pronounce.is_vowel(phone):
            if state == 'vowel':
                # v->v
                vowels.append(phone)
            else:
                # c->v
                before = [after[-1]] if after else []
                vowels = [phone]
                after  = []
        else:
            if state == 'vowel':
                # v->c
                after = [phone]
            else:
                # c->c
                after.append(phone)
    return before + vowels + after

def pronounce_line(line):
    return reduce(operator.add, map(pronounce.pronounce, line), ())

# TODO: allow extra unstressed syllables at end, for 'feminine' rhymes
iamb = (0, 2)
anapest = (0, 2, 0)
iambic_tetrameter = iamb * 4
iambic_pentameter = iamb * 5

def format_line(line):
    return ' '.join(line).capitalize()

def gen_blank_verse(n_lines=6, state=start_state):
    meters = [iambic_pentameter] * n_lines
    rhymes = [[]] * n_lines
    antis  = [[]] * n_lines
    return gen_verse(rhymes, antis, meters, state)

def gen_sonnet(state=start_state):
    # rhyme_scheme = 'ababcdcdefefgg'
    meters = [iambic_pentameter] * 14
    #         1  2   3   4   5  6  7   8   9 10 11  12   13 14
    #         a  b   a   b   c  d  c   d   e  f  e   f    g  g
    rhymes = [[],[], [1],[2],[],[],[5],[6],[],[],[9],[10],[],    [13]]
    antis  = [[],[1],[], [], [],[5],[],[], [],[9],[],[],  [9,10],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_couplet(state=start_state):
    # rhyme_scheme = 'aa'
    rhymes = [[],[1]]
    antis  = [[],[]]
    return gen_verse(rhymes, antis, [iambic_pentameter] * 2, state)

def gen_quatrain(state=start_state):
    # rhyme_scheme = 'abab'
    meters = [iambic_tetrameter] * 4
    rhymes = [[],[],[1],[2]]
    antis  = [[],[1],[],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_neolithic(state=start_state):
    'in the neolithic age'
    'de de dah de de de dah'
    'de dah de dah de dah de dah de dah'
    semi = (2, 0, 2, 0, 2, 0, 2)  # -.*.-.*
    meters = [semi,
              semi,
              iambic_pentameter,
              semi,
              semi,
              iambic_pentameter]
    # rhyme_scheme = 'aabccb'
    #                 123456
    rhymes = [[],[1],[],[],[4],[3]]
    antis  = [[],[],[2],[3],[],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_limerick(state=start_state):
    #end1 = anapest if random.randint(0, 1) else iamb
    end1 = anapest if False else iamb
    end2 = anapest if False else iamb
    meters = [anapest * 2 + end1,
              anapest * 2 + end1,
              anapest + end2,
              anapest + end2,
              anapest * 2 + end1]
    # rhyme_scheme = 'aabba'
    rhymes = [[],[1],[],[3],[2,1]]
    antis  = [[],[],[1],[],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_verse(rhymes, antirhymes, meters, state=start_state):
    lines = [[state]]
    i = 1
    #print len(rhymes), len(antirhymes), len(meters)
    length = len(rhymes)
    rhymes = [[]] + rhymes
    antirhymes = [[]] + antirhymes
    meters = [None] + meters
    while i <= length:
        r = rhymes[i]
        line = gen_line(meter=meters[i],
                        state=lines[i-1][-1],
                        rhyme=(r and lines[r[0]]))
        if line is None:
            # Throw away the current 'stanza' and try over
            i = max(1, (r and r[0]) or i - 2)  # XXX hacky
            lines = lines[:i]
            print >>sys.stderr, 'Backing up to %d' % i
        elif (all(lines_rhyme(line, lines[rr]) for rr in r[1:])
              and not any(lines_rhyme(line, lines[rr])
                          for rr in antirhymes[i])):
            print >>sys.stderr, '%4d' % i, format_line(line)
            lines.append(line)
            i += 1
        else:
            print >>sys.stderr, '****', format_line(line)
    return lines[1:]

def gen_line(meter=iambic_pentameter, state=start_state, rhyme=None):
    #print >>sys.stderr, '. . .', state
    for i in range(90000):
        line = gen(meter, state)
        if line is not None:
            if not rhyme or lines_rhyme(line, rhyme):
                return line
    return None

bad_words = frozenset(string.ascii_lowercase) - frozenset('ai')
bad_words |= frozenset('co il th'.split())

def gen(meter, state):
    if meter == ():
        return []
    for i in range(10):
        try:
            word = babble.pick_word2(state)
            if word in bad_words:
                continue
            after = match_word(word, meter)
        except KeyError:
            continue
        if after is not None:
            rest = gen(after, word)
            if rest is not None:
                return [word] + rest
    #print >>sys.stderr, "Nothing for %s, %s" % (state, meter)
    return None

## gen_line()

## match_words('hello my dear'.split(), iambic_pentameter)
## match_words('No Time thou shalt not boast that I do change'.split(), iambic_pentameter)

## match_word('hello', iambic_pentameter)

def match_words(words, meter):
    for word in words:
        if meter is None: break
        meter = match_word(word, meter)
    return meter

def match_word(word, meter):
    if meter and meter[0] and word in unstressables:
        return None
    return match_phones(pronounce.pronounce(word), meter)
    
def match_phones(phones, meter):
    return match_beats(segment_beats(phones), meter)

def segment_beats(phones):
    return [int(phone[-1]) for phone in phones if pronounce.is_vowel(phone)]

def match_beats(beats, meter):
    if len(meter) < len(beats):
        return None
    if len(set(beats)) == 1:
        return meter[len(beats):]
    if all(match_beat(beat, m) for beat, m in zip(beats, meter)):
        return meter[len(beats):]
    return None

def match_beat(beat, meter_beat):
    # TODO: use 1/2 distinction
    if meter_beat == 0: return beat == 0
    return beat != 0

## segment_beats(('HH', 'AH0', 'L', 'OW1'))

if __name__ == '__main__':
    main()
