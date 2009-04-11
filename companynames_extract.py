import re
import sys

for line in sys.stdin:
    if re.search(r'<li><a href=', line):
        m = re.search(r'title="([^"]+)"', line)
        if not m:
            print 'MISS ON LINE', line
            continue
        print m.group(1)
