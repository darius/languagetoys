import itertools
import operator
import random
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

bad_words = frozenset(string.ascii_lowercase) - frozenset('aio')
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

def start():
    return babble.start(start_state)
    
def print_verse(verse):
    print
    for line in verse:
        print format_line(line)
    print
    print 'Unknown:', ' '.join(set(word for line in verse for word in line if word in guesses))

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

slack, stressed, rhymed = range(3)
iamb = (slack, stressed)
dactyl = (stressed, slack, slack)
anapest = (slack, stressed, slack) # XXX wrong
iambic_tetrameter = iamb * 4
iambic_pentameter = iamb * 5

def gen_blank_verse(n_lines=6, state=None):
    # XXX we seem to be getting extra beats at the end sometimes now
    #  (as if we were ending with a 'rhymed' constituent)
    meters = [iambic_pentameter] * n_lines
    rhymes = [[]] * n_lines
    antis  = [[]] * n_lines
    return gen_verse(rhymes, antis, meters, state)

def gen_sonnet(state=None):
    # rhyme_scheme = 'ababcdcdefefgg'
    m = iambic_pentameter[:-1] + (rhymed,)
    meters = [m] * 14
    #         1  2   3   4   5  6  7   8   9 10 11  12   13 14
    #         a  b   a   b   c  d  c   d   e  f  e   f    g  g
    rhymes = [[],[], [1],[2],[],[],[5],[6],[],[],[9],[10],[],    [13]]
    antis  = [[],[1],[], [], [],[5],[],[], [],[9],[],[],  [9,10],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_couplet(state=None):
    # rhyme_scheme = 'aa'
    m = iambic_pentameter[:-1] + (rhymed,)
    rhymes = [[],[1]]
    antis  = [[],[]]
    return gen_verse(rhymes, antis, [m] * 2, state)

def gen_incantation(state=None):
    m = (stressed, slack, stressed, slack, stressed, slack, rhymed)
    # rhyme_scheme = 'aa'
    rhymes = [[],[1]]
    antis  = [[],[]]
    return gen_verse(rhymes, antis, [m] * 2, state)

def gen_quatrain(state=None):
    # rhyme_scheme = 'abab'
    m = iambic_tetrameter[:-1] + (rhymed,)
    meters = [m] * 4
    rhymes = [[],[],[1],[2]]
    antis  = [[],[1],[],[]]
    return gen_verse(rhymes, antis, meters, state)

def gen_neolithic(state=None):
    'in the neolithic age'
    'de de dah de de de dah'
    'de dah de dah de dah de dah de dah'
    #semi = (1,0,2,0,1,0,2)  # -.*.-.*
    # TODO: a 1-beat-only 'rhymed' constituent
    m = iambic_pentameter[:-1] + (rhymed,)
    semi = (stressed, slack, stressed, slack, stressed, slack, rhymed)
    meters = [semi,
              semi,
              m,
              semi,
              semi,
              m]
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
              (stressed, slack, slack, rhymed),
              dactyl * 2,
              dactyl * 2,
              dactyl * 2,
              (stressed, slack, slack, rhymed)]
    # rhyme_scheme = '--a---a'
    #                 1234567
    rhymes = [[],[],[],[],[],[],[3]]
    # XXX we need gen_line() to return the rhyme even on a non-rhyming
    #  line (for the sake of antirhyme checks)
    # antis  = [[],[],[2],[3],[],[3],[]]
    antis  = [[],[],[],[],[],[],[]]
    return [['higgledy', 'piggledy']] + gen_verse(rhymes, antis, meters, state)

def gen_limerick(state=None):
    #end1 = anapest if random.randint(0, 1) else iamb
    if random.randint(0, 1):
        end1 = anapest if False else (slack, rhymed)
        end2 = anapest if False else (slack, rhymed)
        meters = [anapest * 2 + end1,
                  anapest * 2 + end1,
                  anapest + end2,
                  anapest + end2,
                  anapest * 2 + end1]
    else:
        anapest1 = (slack, slack, stressed)
        end = (slack, slack, rhymed)
        meters = [anapest1 * 2 + end,
                  anapest1 * 2 + end,
                  anapest1 + end,
                  anapest1 + end,
                  anapest1 * 2 + end]
    # rhyme_scheme = 'aabba'
    rhymes = [[],[1],[],[3],[2,1]]
    antis  = [[],[],[1],[],[]]
    return gen_verse(rhymes, antis, meters, state)

class Exhausted(Exception):
    pass

def tick(counter):
    counter[0] -= 1
    if counter[0] < 0:
        raise Exhausted()

def gen_verse(rhymescheme, antirhymescheme, meters, state=None):
    if state is None: state = start_state
    order = babble.the_order()
    lines = [list(state)]
    linerhymes = [None]
    i = 1
    length = len(rhymescheme)
    rhymescheme = [[]] + rhymescheme
    antirhymescheme = [[]] + antirhymescheme
    meters = [None] + meters
    while i <= length:
        state_i = tuple(reduce(operator.add, lines, [])[-order:])
        rhymes     = [linerhymes[j] for j in rhymescheme[i]]
        antirhymes = [linerhymes[j] for j in antirhymescheme[i]]
        if i == 1:  # XXX hacky
            state_i = babble.start(state_i)
            m = match_words(tuple(t for t in state_i if t != '<S>'),
                            meters[i])
            if m is None:
                continue
            line, rhyme = gen_line(meter=m,
                                   rhymes=rhymes,
                                   antirhymes=antirhymes,
                                   state=state_i,
                                   cutoff=10000)
            if line: line = list(state_i) + line
        else:
            line, rhyme = gen_line(meter=meters[i],
                                   rhymes=rhymes,
                                   antirhymes=antirhymes,
                                   state=state_i,
                                   cutoff=60000)
        if line is None:
            # XXX hacky:
            i = max(1, max(rhymescheme[i]) if rhymescheme[i] else i-1)
            lines = lines[:i]
            linerhymes = linerhymes[:i]
            print >>sys.stderr, 'Backing up to %d' % i
        else:
            print >>sys.stderr, '%4d' % i, format_line(line)
            lines.append(line)
            linerhymes.append(rhyme)
            i += 1
    return lines[1:]

def gen_line(meter, rhymes, antirhymes, state, cutoff):
    counter = [cutoff]
    while True:
        try:
            line, rhyme = gen(meter, rhymes, antirhymes, state, counter)
        except Exhausted:
            return None, None
        if line:
            return line, rhyme

def gen(meter, rhymes, antirhymes, state, counter):
    tick(counter)
    for i in range(10):
        try:
            word = babble.pick_word2(state)
        except KeyError:
            continue
        after, rhyme = match_word(word, meter)
        if () == after:
            if (all(rhyme_matches(rhyme, r) for r in rhymes)
                and not any(rime(rhyme) == rime(r) for r in antirhymes)):
                return [word], rhyme
            continue
        if after is not None:
            rest, rhyme = gen(after, rhymes, antirhymes, 
                              babble.update(state, word),
                              counter)
            if rest is not None:
                return [word] + rest, rhyme
    return None, None

def match_words(words, meter):
    for word in words:
        if meter is None: break
        meter, rhyme = match_word(word, meter)
    return meter

def match_word(word, meter):
    if meter and meter[0] and word in unstressables:
        return None, None
    if True:
        if word == '<S>':
            return meter, None
    try:
        phones = pronounce.pronounce(word)
    except KeyError:
        return try_guess(word, meter)
    else:
        return match_phones(phones, meter)

import guessbeats
guesses = guessbeats.load()

def try_guess(word, meter):
    print 'YO! TRYING', word
    try:
        beats = guesses[word]
    except KeyError:
        return None, None
    lobeat, hibeat = argh(beats)
    nvowels = len(beats)
    for j, m in enumerate(meter):
        if nvowels <= j:
            return meter[j:], None
        if m == rhymed:
            return None, None
        if not match_beat(beats[j], m, lobeat, hibeat):
            # XXX let's try a special case improvement until we can
            #   better it:
            if beats == (1, 0, 0,) and meter[:3] == (1, 0, 1):
                return meter[3:], None
            return None, None
    return None, None

def match_phones(phones, meter):
    beats = segment_beats(phones)
    lobeat, hibeat = argh(beats)
    v, nvowels = 0, len(beats)
    p, nphones = 0, len(phones)
    for j, m in enumerate(meter):
        if nphones <= p:
            return meter[j+1:], None
        if m == rhymed:
            # NB we assume a rhymed may only appear once, at the end of meter
            # XXX I think this is not quite right: e.g. 'intelligible'
            #  against meter (0,1,0,rhymed) produces rhyme 'gible' here,
            #  but it should fail:
            return match_as_rhyme(phones[p:], lobeat, hibeat)
        while not pronounce.is_vowel(phones[p]):
            p += 1
            if nphones <= p:
                return None, None
        if not match_beat(int(phones[p][-1]), m, lobeat, hibeat):
            # XXX let's try a special case improvement until we can
            #   better it:
            if beats == [1, 0, 0] and meter[:3] == (1, 0, 1):
                return meter[3:], None
            return None, None
        p += 1
        v += 1
        if v == nvowels:
            return meter[j+1:], None
    return (), None             # XXX shouldn't this be None, None?

sheeshtable = [0, 2, 1]
def argh(beats):
    sheesh = [sheeshtable[b] for b in beats]
    return min(sheesh), max(sheesh)

def match_as_rhyme(phones, lobeat, hibeat):
    beats = segment_beats(phones)
    assert beats
    if beats[0] == 1 or lobeat == hibeat:
        return (), phones
    return None, None

def match_beat(beat, meter_beat, lobeat, hibeat):
    # TODO: use 1/2 distinction in meter
    if meter_beat == 0:
        rv = (sheeshtable[beat] == lobeat)
    else:
        rv = (lobeat < sheeshtable[beat] or lobeat == hibeat)
    return rv

def memo(f):
    "Memoize function f."
    table = {}
    def fm(*x):
        if x not in table:
            table[x] = f(*x)
        return table[x]
    fm.memo = table
    return fm

@memo
def segment_beats(phones):
    return [int(phone[-1]) for phone in phones if pronounce.is_vowel(phone)]


def rhyme_matches(phones1, phones2):
    return onset(phones1) != onset(phones2) and rime(phones1) == rime(phones2)

def onset(phones): return phones[:find_rime(phones)]
def rime(phones):  return phones[find_rime(phones):]

def find_rime(phones):
    assert isinstance(phones, tuple), "phones: %r" % phones
    for i, ph in enumerate(phones):
        if pronounce.is_vowel(ph):
            return i
    assert False


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
