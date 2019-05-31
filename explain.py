"""
Sketch of https://explainshell.com/ like output, in plain text

 $ python explain.py

git diff-tree -M -r --name-status <commit>
    └───┬───┘ ├┘ ├┘ └─────┬─────┘ └──┬───┘
┌───────┘     │  │        │          │
│┌────────────┘  │        │          │
││┌──────────────┘        │          │
│││┌──────────────────────┘          │
││││┌────────────────────────────────┘
└┼┼┼┼─ Compares the content and mode of blobs found via two tree objects
 └┼┼┼─ Detect renames
  └┼┼─ recurse into subtrees
   └┼─ Show only names and status of changed files
    │           for example:
    │              M   foo.py
    └─ show differences between this commit and preceding one
"""

import itertools
import math
from itertools import (accumulate, chain, repeat)
from textwrap import wrap

def tokens(descs):
    def norm(desc):
        return desc if type(desc) is tuple else (desc, None)

    ts = [{'token': t,
           'comment': c,
           'length': len(t)} for (t,c) in [norm(desc) for desc in descs]]
    return ts

def withOffsets(ts):
    def offset(a, b):
        o = a['offset'] + a['length']
        po = o + math.ceil(b['length'] / 2)
        return {**b,
                'offset': o,
                'pathOffset': po}
    init = {'offset': 0, 'length': 0, 'comment': None}

    pred = lambda t: t['comment']

    return filter(pred,
                  accumulate([init] + ts, offset))

def line1(ts):
    print(''.join([t['token'] for t in ts]))

def line2(ts):
    def draw(t):
        if t['comment']:
            l = t['length']
            if l == 1:
                return '│'
            elif l == 2:
                return '├┘'
            else:
                left  = math.floor((l-3) / 2)
                right = math.ceil((l-3) / 2)
                return ''.join([
                    '└',
                    left * '─',
                    '┬',
                    right * '─',
                    '┘'])
        else:
            return ' ' * t['length']
    print(''.join([draw(t) for t in ts]))

def line3(left, right):
    l = len(left)
    rpos = [r['pathOffset'] for r in right]
    span = rpos[0] - l

    curve = '│' if span == 1 else '┌%s┘' % ('─' * (span-2))

    offsets = [b-a for (a,b) in zip(rpos, rpos[1:])]
    tails = [('%' + str(o) + 's') % '│' for o in offsets]

    print(''.join(['│' * l,
                  curve,
                  *tails]))

def line3s(ts):
    for x in range(0,len(ts)):
        line3(ts[:x], ts[x:])

def reflow(text, width):
    return sum([wrap(para, width) for para in text.split("\n")], [])

def line4s(ts):
    l = len(ts)
    for x in range(0,len(ts)):
        first = ''.join([' ' * x,
                         '└',
                         '┼' * (l-x-1),
                         '─ '])
        then = ''.join([' ' * (x+1),
                        '│' * (l-x-1),
                        '  '])
        width = 80 - (l + 2)
        text = reflow(ts[x]['comment'], width)
        print("\n".join(
            [h+t for (h,t) in zip(chain([first], repeat(then)), text)]))

def explain(descs):
    ts = tokens(descs)
    line1(ts)
    line2(ts)

    ts = list(withOffsets(ts))
    line3s(ts)
    line4s(ts)

descs = ['git',
         ' ',
         ('diff-tree', 'Compares the content and mode of blobs found via two tree objects'),
         ' ',
         ('-M', 'Detect renames'),
         ' ',
         ('-r', 'recurse into subtrees'),
         ' ',
         ('--name-status',
         """Show only names and status of changed files

         for example:
            M   foo.py"""),
         ' ',
         ('<commit>', 'show differences between this commit and preceding one')]

explain(descs)

