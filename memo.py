def memo(f):
    memos = {}
    def memoized(*args):
        try: return memos[args]
        except KeyError:
            result = memos[args] = f(*args)
            return result
    return memoized
