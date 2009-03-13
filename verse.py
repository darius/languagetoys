import itertools
import operator
import random
import re
import string
import sys

import babble
import pronounce

default_ngram_filename = '2gm-common6'

start_state = ('<S>',)

# TODO: Can we just penalize unstressables (to varying degrees)
#  instead of banning them, and then include more words in this set?
unstressables = 'a an of the'.split()
if True:
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
    unstressables += 'ah en et la may non off per re than un'.split()
unstressables = frozenset(unstressables)

bad_words = frozenset(string.ascii_lowercase) - frozenset('ai') #-'o'
bad_words |= frozenset('co il th'.split())

def main(argv):
    pronounceables = set(word.lower() for word in pronounce.known_words())
    ngram_filename = default_ngram_filename
    if 2 <= len(argv) and argv[0] == '-f':
        ngram_filename = argv[1]
        argv = argv[2:]
    babble.load(open(ngram_filename),
                (pronounceables - bad_words) | set(['<S>']))
    if not argv:
        versers = [gen_blank_verse,
                   gen_incantation,
                   gen_couplet,
                   gen_quatrain,
                   gen_limerick,
                   gen_neolithic,
                   gen_double_dactyl,
                   gen_sonnet]
    else:
        versers = [globals()['gen_' + arg] for arg in argv]
    for verser in versers:
        print_verse(verser())

def print_double_dactyl_words():
    for word in words_that_match(dactyl * 2):
        print word

def words_that_match(meter):
    for word in pronounce.known_words():
        word = word.lower()
        if () == match_word(word, meter):
            yield word

def start():
    return babble.start(start_state)
    
def print_verse(verse):
    print
    for line in verse:
        print format_line(line)
    print

def check_sonnet123():
    for line in open('sonnet123'):
        if not scans(line):
            words = re.findall(r"['\w]+", line)
            print match_words(words, iambic_pentameter)
            print line

def scans(line):
    words = re.findall(r"['\w]+", line)
    return match_words(words, iambic_pentameter) == ()

def lines_echo(line1, line2):
    return rime(rhyme_phones(line1)) == rime(rhyme_phones(line2))

def lines_rhyme(line1, line2):
    # N.B. we assume line1, line2 don't end in <S>
    return (line1[-1] != line2[-1]  # such rhymes are almost always weak
            and rhyme_matches(rhyme_phones(line1),
                              rhyme_phones(line2)))

def rhyme_matches(phones1, phones2):
    return onset(phones1) != onset(phones2) and rime(phones1) == rime(phones2)

def onset(phones):
    return '' if pronounce.is_vowel(phones[0]) else phones[0]

def rime(phones):
    return phones if pronounce.is_vowel(phones[0]) else phones[1:]

# M       A     D      L       A      D      EE
# //m   m/a/  m/a/d  m/a/dl  l/a/   l/a/d   d/ee/

def rhyme_phones(line):
    line = [t for t in line if t != '<S>']
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

slack, stressed, rhymed = range(3)
iamb = (slack, stressed)
dactyl = (stressed, slack, slack)
anapest = (slack, stressed, slack) # XXX wrong
iambic_tetrameter = iamb * 4
iambic_pentameter = iamb * 5

def format_line(line):
    out = ''
    for t in line:
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

def gen_blank_verse(n_lines=6, state=None):
    meters = [iambic_pentameter] * n_lines
    rhymes = [[]] * n_lines
    antis  = [[]] * n_lines
    return gen_verse(rhymes, antis, meters, state)

def gen_sonnet(state=None):
    # rhyme_scheme = 'ababcdcdefefgg'
    meters = [iambic_pentameter] * 14
    #         1  2   3   4   5  6  7   8   9 10 11  12   13 14
    #         a  b   a   b   c  d  c   d   e  f  e   f    g  g
    rhymes = [[],[], [1],[2],[],[],[5],[6],[],[],[9],[10],[],    [13]]
    antis  = [[],[1],[], [], [],[5],[],[], [],[9],[],[],  [9,10],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_couplet(state=None):
    # rhyme_scheme = 'aa'
    rhymes = [[],[1]]
    antis  = [[],[]]
    return gen_verse(rhymes, antis, [iambic_pentameter] * 2, state)

def gen_incantation(state=None):
    # rhyme_scheme = 'aa'
    rhymes = [[],[1]]
    antis  = [[],[]]
    return gen_verse(rhymes, antis, [(2,0,1,0,2,0,1)] * 2, state)

def gen_quatrain(state=None):
    # rhyme_scheme = 'abab'
    meters = [iambic_tetrameter] * 4
    rhymes = [[],[],[1],[2]]
    antis  = [[],[1],[],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_neolithic(state=None):
    'in the neolithic age'
    'de de dah de de de dah'
    'de dah de dah de dah de dah de dah'
    semi = (1,0,2,0,1,0,2)  # -.*.-.*
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

def gen_double_dactyl(state=None):
    # TODO: make the first line a name
    # TODO: fit in a whole-line double-dactyl word in the 2nd verse
    meters = [dactyl * 2,
              dactyl * 2,
              (2,0,0,2),
              dactyl * 2,
              dactyl * 2,
              dactyl * 2,
              (2,0,0,2)]
    # rhyme_scheme = '--a---a'
    #                 1234567
    rhymes = [[],[],[],[],[],[],[3]]
    antis  = [[],[],[2],[3],[],[3],[]]
    return [['higgledy', 'piggledy']] + gen_verse(rhymes, antis, meters, state)

def gen_limerick(state=None):
    #end1 = anapest if random.randint(0, 1) else iamb
    end1 = anapest if False else iamb
    end2 = anapest if False else iamb
    meters = [anapest * 2 + end1,
              anapest * 2 + end1,
              anapest + end2,
              anapest + end2,
              anapest * 2 + end1]
    anapest1 = (slack, slack, stressed)
    meters = [anapest1 * 3,
              anapest1 * 3,
              anapest1 * 2,
              anapest1 * 2,
              anapest1 * 3]
    # rhyme_scheme = 'aabba'
    rhymes = [[],[1],[],[3],[2,1]]
    antis  = [[],[],[1],[],[]]
    return gen_verse(rhymes, antis, meters, state)

class Exhausted(Exception):
    pass

def gen_verse(rhymescheme, antirhymescheme, meters, state=None):
    if state is None: state = start_state
    order = babble.the_order()
    lines = [list(state)]
    i = 1
    length = len(rhymescheme)
    rhymescheme = [[]] + rhymescheme
    antirhymescheme = [[]] + antirhymescheme
    meters = [None] + meters
    while i <= length:
        state_i = tuple(reduce(operator.add, lines, [])[-order:])
        rhymes = [rhyme_phones(lines[j]) for j in rhymescheme[i]]
        antirhymes = [rhyme_phones(lines[j]) for j in antirhymescheme[i]]
        if i == 1:  # XXX hacky
            state_i = babble.start(state_i)
            m = match_words(tuple(t for t in state_i if t != '<S>'),
                            meters[i])
            if m is None:
                continue
            line = gen_line(meter=m,
                            rhymes=rhymes,
                            antirhymes=antirhymes,
                            state=state_i,
                            cutoff=10000)
            if line: line = list(state_i) + line
        else:
            line = gen_line(meter=meters[i],
                            rhymes=rhymes,
                            antirhymes=antirhymes,
                            state=state_i,
                            cutoff=60000)
        if line is None:
            # # XXX hacky:
            i = max(1, max(rhymescheme[i]) if rhymescheme[i] else i-1)
            lines = lines[:i]
            print >>sys.stderr, 'Backing up to %d' % i
        else:
            print >>sys.stderr, '%4d' % i, format_line(line)
            lines.append(line)
            i += 1
    return lines[1:]

def gen_line(meter, rhymes, antirhymes, state, cutoff):
    counter = [cutoff]
    while True:
        try:
            line = gen(meter, rhymes, antirhymes, state, counter)
        except Exhausted:
            return None
        if line:
            return line

def gen(meter, rhymes, antirhymes, state, counter):
    tick(counter)
    for i in range(10):
        try:
            word = babble.pick_word2(state)
        except KeyError:
            continue
        after = match_word(word, meter)
        if () == after:
            rhyme = rhyme_phones([word])
            if (all(rhyme_matches(rhyme, r) for r in rhymes)
                and not any(rime(rhyme) == rime(r) for r in antirhymes)):
                return [word]
            continue
        if after is not None:
            rest = gen(after, rhymes, antirhymes, 
                       babble.update(state, word),
                       counter)
            if rest is not None:
                return [word] + rest
    return None

def tick(counter):
    counter[0] -= 1
    if counter[0] < 0:
        raise Exhausted()

def match_words(words, meter):
    for word in words:
        if meter is None: break
        meter = match_word(word, meter)
    return meter

def match_word(word, meter):
    if meter and meter[0] and word in unstressables:
        return None
    if True:
        if word == '<S>':
            return meter
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

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
