import collections, cPickle, re

class BigramModel:
    def __init__(self):
        # _counts[w1] counts unigrams we've trained on.
        # _succs[w1][w2] counts bigrams we've trained on.
        self._counts = collections.defaultdict(int)
        self._n = self._p0 = 0
        self._succs = {}
    def train(self, text):
        previous = '#'
        for pos, word in words(text):
            self._note_ngram(previous, word)
            previous = word
        self._note_ngram(previous, '#')
    def _note_ngram(self, prev, word):
        # XXX doesn't update _p0
        self._counts[prev] += 1
        self._n += 1
        if prev not in self._succs:
            self._succs[prev] = collections.defaultdict(int)
        self._succs[prev][word] += 1
    def save(self, file):
        cPickle.dump(self._succs, file)
    def load(self, file):
        self._succs = cPickle.load(file)
        self._counts = dict((word, len(succs))
                            for word, succs in self._succs.items())
        self._n = sum(self._counts.values())
        self._p0 = 1.0 / self._n
    def p(self, context, word):
        counts = self._counts
        s = 0.01 * self._p0 + counts.get(word, 0) / self._n
        if context in self._succs:
            return s + 0.89 * (self._succs[context].get(word, 0)
                               / float(counts[context]))
        return s
    def p_untuned(self, context, word):
        # XXX ad-hoc
        return (0.89 * self._p2(context, word)
                + 0.10 * self._p1(word)
                + 0.01 * self._p0)
    def _p1(self, word):
        return self._counts.get(word, 0) / self._n
    def _p2(self, context, word):
        if context in self._succs:
            return (self._succs[context].get(word, 0)
                    / float(self._counts[context]))
        return 0

def words(text):
    return ((m.start(), m.group(0))
            for m in re.finditer(r'[A-Za-z]+', text))

if __name__ == '__main__':
    m = BigramModel()
    m.train(open('big.txt').read().lower())
    m.save(open('bigdict', 'w'))
