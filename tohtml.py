"""
Given plain text on stdin, write out HTML that highlights
words with increasing intensity the more unlikely they are
according to a language model.
"""

# NB: this sort of thing seems helpful for proofreading.
# The 'automatic copyeditor' doesn't have to be right as often..

from math import log10
import re
import sys

import pdist

highest_prob = pdist.Pw('the')

def colored(word, prev):
    if word.isspace(): return word
    return wrapcolor(word, color(score(word, prev)))

def score(word, prev):
    if word[0].isalpha():
        v = -log10(pdist.cPw(word.lower(), prev.lower()))
        #return (0.5 * v) / len(word)
        return (0.5 * v + 0.0) / (2.0 + len(word))
    return 0.3

def color(v):
    c = int(v * 256)
    c = max(0, min(c, 255))
    return rgb(c, c, c)

def rgb(r, g, b):
    return '%02x%02x%02x' % (r, g, b)

def wrapcolor(text, c):
    return '<font color="%s">%s</font>' % (c, text)

input = [line.strip('\\\n') for line in sys.stdin.readlines()]

#print len(max((t for t in '\n'.join(input).split() if t.isalpha()), key=len))
#sys.exit(0)

print """<body bgcolor=black text=white>"""

clitics = "('d|n't|'re|'ve|'s)?"
contractions = "can't|d'you|doesn't|don't|he'll|i'd|i've|isn't|isn't|it's|let's|mustn't|needn't|she'd|she's|you're|you've"

# TODO: fix rtf character escapes
# TODO: handle clitics generatively
# TODO: turn _foo_ into <i>foo</i>
# TODO: bigram probabilities with sentence-break tokens
# TODO: 1/2-character words are overemphasized. fix.
#   How about: normalize to the ave. prob. for words of the same length
#   Another idea: try visualizing surprisingness in bits/syllable instead of bits/char.
# TODO: adaptive model
prev = '<S>'
for line, next in zip([''] + input, input):
    L = len(line)
    m = len(next.split()[0])
    words = re.findall(r"[a-zA-Z]+|.", line)
    coloredwords = [] 
    for word in words:
        coloredwords.append(colored(word, prev))
        prev = word
    out = ''.join(coloredwords)
    if L+m < 72: out += '<P>'
    print out

print """</body>"""



