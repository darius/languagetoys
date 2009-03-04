import itertools
import operator
import re
import sys

import babble
import pronounce

def main():
    print_new_sonnet()

def print_new_sonnet():
    for line in gen_sonnet():
        print ' '.join(line).capitalize()

def check_sonnet123():
    for line in open('sonnet123'):
        if not scans(line):
            words = re.findall(r"['\w]+", line)
            print match_words(words, iambic_pentameter)
            print line

def scans(line):
    words = re.findall(r"['\w]+", line)
    return match_words(words, iambic_pentameter) == ()

def rhymes(line1, line2):
    return (line1[-1] != line2[-1] # such rhymes are almost always weak
            and rhyme_matches(rhyme_phones(line1),
                              rhyme_phones(line2)))

def rhyme_matches(phones1, phones2):
    return phones1[0] != phones2[0] and phones1[1:] == phones2[1:]

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

iamb = (0, 2)
iambic_pentameter = iamb * 5

def gen_sonnet():
    lines = [['<S>']]
    # rhyme_scheme = 'ababcdcdefefgg'
    rhyme_scheme = ['xxx',None,None,1,2,None,None,5,6,None,None,9,10,None,13]
    i = 1
    while i <= 14:
        r = rhyme_scheme[i]
        line = gen_line(state=lines[i-1][-1],
                        rhyme=(r is not None and lines[r]))
        # TODO: reject lines with accidental rhymes ('aaaa' vs 'abab')
        if line is None:
            # Throw away the current 'stanza' and try over
            print >>sys.stderr, 'Backing up from %d to %d' % (i, 1 + 4 * ((i - 1) // 4))
            i = 1 + 4 * ((i - 1) // 4)
            lines = lines[:i]
        else:
            lines.append(line)
            i += 1
    return lines[1:]

def gen_line(meter=iambic_pentameter, state='<S>', rhyme=None):
    print 'state', state
    for i in range(10000):
        line = gen(meter, state)
        if line is not None:
            if not rhyme or rhymes(line, rhyme):
                return line
    return None

def gen(meter, state):
    if meter == ():
        return []
    for i in range(10):
        try:
            word = babble.pick_word2(state)
            if word and len(word) == 1 and word not in ('a', 'i'):
                continue
            after = match_word(word, meter)
        except KeyError:
            continue
        if after is not None:
            rest = gen(after, word)
            if rest is not None:
                return [word] + rest
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
    if meter and meter[0] and word in 'a an of the'.split():
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
