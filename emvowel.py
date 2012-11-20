from math import log10
import re
import sys

# pdist.Pw is the unigram model, and pdist.cPw the bigram.
import pdist
from pdist import Pw, cPw

# A special token our models take to signify the start of a sentence.
sentence_token = '<s>'

y_is_a_vowel = False
vowels = r'[aeiouyAEIOUY]' if y_is_a_vowel else r'[aeiouAEIOU]'

def disemvowel(t):
    return re.sub(vowels, '', t)

emvowel_dict = {}
for token in Pw.iterkeys():
    emvowel_dict.setdefault(disemvowel(token), []).append(token)

def all_emvowelings(token):
    # XXX case actually matters. E.g. Russia vs. RSS.
    t = token.lower()
    return emvowel_dict.get(t) or [t]

def emvowel_unigram(tokens):
    return tuple(max(all_emvowelings(token), key=Pw)
                 for token in tokens)

@pdist.memo
def emvowel1(tokens, prev=sentence_token):
    if not tokens: return ()
    first, rest = tokens[0], tokens[1:]
    return max(((word,) + emvowel1(rest, word)
                for word in all_emvowelings(first)),
               key=lambda words: pdist.product(cPw(v, u)
                                               for u, v in bigrams((prev,) + words)))

def bigrams(words):
    for i in range(len(words)-1):
        yield words[i:i+2]

def emvowel(tokens, prev=sentence_token):
    @pdist.memo
    def ev(tokens, prev):
        if not tokens: return 0, ()
        first_token, rest_tokens = tokens[0], tokens[1:]
        return max((log10(cPw(word, prev)) + logp_rest,
                    (word,) + rest)
                   for word in all_emvowelings(first_token)
                   for logp_rest, rest in [ev(rest_tokens, word)])
    logp, words = ev(tokens, prev)
    return words

def try_on(sample):
    tokens = tuple(re.findall(r"['\w]+", sample))
    print 'unigram:'
    print indent(' '.join(emvowel_unigram(tokens)))
    print 'emvowel:'
    print indent(' '.join(emvowel(tokens)))

def indent(s):
    return '    ' + s.replace('\n', '\n    ')

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
"""My father's family name being Pirrip, and my Christian name Philip, my
infant tongue could make of both names nothing longer or more explicit
than Pip. So, I called myself Pip, and came to be called Pip.""",
 """A simple project for an NLP class would be to make a decent corpus-based re-emvoweler. This one really isn't very good, and could easily be improved by considering bigram frequencies."""]

def main():
    for sample in samples:
        print '---------------------------------------------'
        print sample
        try_on(disemvowel(sample))
        print

main()
