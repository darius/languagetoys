"""
Given a disemvoweled text, try to guess the original text (i.e.,
"re-emvowel" it). Here are three corpus-based strategies: use a
unigram model, or a bigram model greedily, or a bigram model with the
Viterbi algorithm.
"""

import math
import re

# pdist.Pw is the unigram model, and pdist.cPw the bigram.
import pdist

# A special token our models take to signify the start of a sentence.
sentence_token = '<' + 'S' + '>'

y_is_a_vowel = False

def disemvowel(t):
    if y_is_a_vowel:
        return re.sub(r'[aeiouyAEIOUY]', '', t)
    return re.sub(r'[aeiouAEIOU]', '', t)

emvowel_dict = {}
for token in pdist.Pw.iterkeys():
    emvowel_dict.setdefault(disemvowel(token), []).append(token)

def all_emvowelings(token):
    if token == sentence_token: return [sentence_token]
    # XXX case actually matters. E.g. Russia vs. RSS.
    t = token.lower()
    return emvowel_dict.get(t) or [t]

def emvowel_one_token(token):
    return max(all_emvowelings(token), key=pdist.Pw.get)

def emvowel1(tokens):
    return map(emvowel_one_token, tokens)

def greedy_emvowel2(tokens):
    rv = []
    prev = sentence_token
    for t in tokens:
        prev = max(all_emvowelings(t),
                   key=lambda candidate: pdist.cPw(candidate, prev))
        rv.append(prev)
    return rv

def viterbi_emvowel2(tokens):
    logprob, words = max(emvoweling(tuple(tokens)))
    return words[1:]

@pdist.memo
def emvoweling(tokens):
    if not tokens:
        return [(0.0, [sentence_token])]
    def extend((logprob, words), word):
        return (logprob + math.log10(pdist.cPw(word, words[-1])),
                words + [word])
    def extend2(prevresult, tween, word):
        return extend(extend(prevresult, tween) if tween else prevresult,
                      word)
    prevresults = emvoweling(tokens[:-1])
    return [max(extend(prevresult, candidate) for prevresult in prevresults)
# This is to try inserting missing 'a' and 'I' words; but it never 
# seems to judge them worth inserting, in practice:
#                for tween in ['a', 'i', None])
            for candidate in all_emvowelings(tokens[-1])]

def try_on(sample):
    print sample
    tokens = re.findall(r"['\w]+", sample)
    print 
    print ' '.join(emvowel1(tokens))
    print 
    print ' '.join(greedy_emvowel2(tokens))
    print 
    print ' '.join(viterbi_emvowel2(tokens))
    # Let's look into why Viterbi over bigrams is so slow here:
    options = [len(all_emvowelings(t)) for t in tokens]
    print options
    print sum(options), 'steps for greedy_emvowel2'
    print sum(prev * next for prev, next in zip([1] + options, options)), \
        'steps for viterbi_emvowel2'
    # So it turns out to be common in our corpus for very short words
    # to have 100-200 emvowelings. This is expensive since we're
    # quadratic in that number (while of course linear in the length
    # of the input). This suggests trimming very-uncommon words from
    # emvowel_dict.

samples = \
["""f t's tr tht r spcs s ln n th nvrs, thn 'd hv t sy tht th nvrs md rthr lw nd sttld fr vry lttl.

Grg Crln""",
 """Th nxt lgcl dvlpmnt f ths prtclr Bttr Mstrp s DV-Rdstrbtr, whch wll xprt th hrvstd vwls t ths lngge, mny n rpdly dvlpng st rpn cntrs, tht hv lng bn ndrsppld thrwth. (Th fct tht mny f ths ppltns hv hstr f xtrml clrfl nvctv m nt b nrltd.)

f cn rd ths cn gt gd jb s frlnc rvwltr.""",
 """Mk, tht'd b lk "Clntn rlfts vwls t Bsn?" """,
 """Sct Fr Crtv nchrnsm Szs Cntrl f Rss""",
 """y r th mn (nlss y r th wmn).""",
 """s ths th plc fr   lnk t th t-shrt, bmpr stckr, tc "ll yr vwl r blng t s"?""",
 """T b fr, n cld *sly* crt smlr vd tsd n bm rlly:
"Grg Bsh *prsnlly* crshd *bth* rplns nt th Wrld Trd Cntr! Bt nly ftr rlsng mnd-cntrl chmtrls nd rgn-hrnssng stllts vr NYC!"
Slctv dtng s th prpgndst's frnd.""",
 """Mnfst plnnss,

mbrc smplcty,

Rdc slfshnss,

Hv fw dsrs.

L-tz""",
 """Bttr t rmn slnt nd b thght fl thn t spk t nd rmv ll dbt.

brhm Lncln""",
 """ghty prcnt f sccss s shwng p.

Wdy lln""",
 """d nt wnt ppl t b grbl, s t svs m th trbl f lkng thm.

Jn stn""",
 """n rl lf, ssr y, thr s n sch thng s lgbr.

Frn Lbwtz""",
 """Sbd yr pptts, my drs, nd y'v cnqrd hmn ntr.

Chrls Dckns""",
 """A simple project for an NLP class would be to make a decent corpus-based re-emvoweler. This one really isn't very good, and could easily be improved by considering bigram frequencies."""]

for sample in samples:
    print '---------------------------------------------'
    try_on(disemvowel(sample))
    print
