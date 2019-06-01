"""
Sketch of https://explainshell.com/ like output, in plain text

 $ python explain.py

git diff-tree -M -r --name-status <commit>
    └───┬───┘ ┣┛ ├┘ ┗━━━━━┳━━━━━┛ └──┬───┘
┌───────┘     ┃  │        ┃          │
│┏━━━━━━━━━━━━┛  │        ┃          │
│┃┌──────────────┘        ┃          │
│┃│┏━━━━━━━━━━━━━━━━━━━━━━┛          │
│┃│┃┌────────────────────────────────┘
└╂┼╂┼─ Compares the content and mode of
 ┃│┃│  blobs found via two tree objects
 ┗┿╋┿━ Detect renames
  └╂┼─ recurse into subtrees
   ┗┿━ Show only names and status of
    │  changed files
    │           for example:
    │              M   foo.py
    └─ show differences between this
       commit and preceding one
"""

import itertools
import math
from itertools import (accumulate, chain, repeat, cycle)
from functools import reduce
from textwrap import wrap
from operator import itemgetter

def tokens(descs):
    def norm(desc):
        return desc if type(desc) is tuple else (desc, None)

    ts = [{'token': t,
           'comment': c,
           'length': len(t)}
          for (t,c)
          in [norm(desc) for desc in descs]]
    return ts

def withOffsets(ts):
    def offset(a, b):
        o = a['offset'] + a['length']
        po = o + math.ceil(b['length'] / 2)
        return {**b,
                'offset': o,
                'pathOffset': po}

    init = {'offset': 0,
            'pathOffset': 0,
            'length': 0,
            'comment': None}

    withOffset = list(filter(itemgetter('comment'),
                             accumulate([init] + ts, offset)))

    withDelta = [{**t,
                  'indent': t['offset'] - p['offset'] - p['length'],
                  'pathDelta': t['pathOffset'] - p['pathOffset']}
                 for (t,p)
                 in zip(withOffset, [init] + withOffset)]

    withPens = [{**t, **p}
                for (t,p)
                in zip(withDelta,
                       cycle([{'pen': False}, {'pen': True}]))]
    return withPens


boxes = {
        'ew': '─',
        'EW': '━',
        'ns': '│',
        'NS': '┃',
        'se': '┌',
        'sE': '┍',
        'Se': '┎',
        'SE': '┏',
        'sw': '┐',
        'sW': '┑',
        'Sw': '┒',
        'SW': '┓',
        'ne': '└',
        'nE': '┕',
        'Ne': '┖',
        'NE': '┗',
        'nw': '┘',
        'nW': '┙',
        'Nw': '┚',
        'NW': '┛',
        'nse': '├',
        'nsE': '┝',
        'Nse': '┞',
        'nSe': '┟',
        'NSe': '┠',
        'NsE': '┡',
        'nSE': '┢',
        'NSE': '┣',
        'nsw': '┤',
        'nsW': '┥',
        'Nsw': '┦',
        'nSw': '┧',
        'NSw': '┨',
        'NsW': '┩',
        'nSW': '┪',
        'NSW': '┫',
        'sew': '┬',
        'seW': '┭',
        'sEw': '┮',
        'sEW': '┯',
        'Sew': '┰',
        'SeW': '┱',
        'SEw': '┲',
        'SEW': '┳',
        'new': '┴',
        'neW': '┵',
        'nEw': '┶',
        'nEW': '┷',
        'New': '┸',
        'NeW': '┹',
        'NEw': '┺',
        'NEW': '┻',
        'nsew': '┼',
        'nseW': '┽',
        'nsEw': '┾',
        'nsEW': '┿',
        'Nsew': '╀',
        'nSew': '╁',
        'NSew': '╂',
        'NseW': '╃',
        'NsEw': '╄',
        'nSeW': '╅',
        'nSEw': '╆',
        'NsEW': '╇',
        'nSEW': '╈',
        'NSeW': '╉',
        'NSEw': '╊',
        'NSEW': '╋',
        'w': '╴',
        'n': '╵',
        'e': '╶',
        's': '╷',
        'W': '╸',
        'N': '╹',
        'E': '╺',
        'S': '╻',
        'Ew': '╼',
        'nS': '╽',
        'eW': '╾',
        'Ns': '╿'}

def box(*items):
    def norm(item):
        if type(item) is tuple:
            (dirs, case) = item
            return dirs.upper() if case else dirs.lower()
        else:
            return item

    dirs = ''.join([norm(item) for item in items])

    def aux(a,b):
        return {**a,
                b.lower(): b}

    rose = reduce(aux, dirs, {})

    dir = ''.join([rose.get(d, '')
                   for d in 'nsew'])
    return boxes.get(dir, ' ')

def boxer(pen):
    return lambda item: box((item, pen))

def header(ts):
    print(''.join([t['token'] for t in ts]))

def markers(ts):
    def indent(t):
        return ' ' * t['indent']

    def line(t):
        _ = boxer(t['pen'])
        l = t['length']
        if l == 1:
            return _('ns')
        elif l == 2:
            return _('nse') + _('nw')
        else:
            left  = math.floor((l-3) / 2)
            right = math.ceil((l-3) / 2)
            return ''.join([
                _('ne'),
                left * _('ew'),
                _('sew'),
                right * _('ew'),
                _('nw')])
    def draw(t):
        return indent(t) + line(t)

    print(''.join([draw(t) for t in ts]))

def converge(ts):
    def aux(left, right):
        (r,*rs) = right
        span = r['pathOffset'] - len(left)

        heads = [box(('ns', l['pen']))
                 for l in left]

        _ = boxer(right[0]['pen'])
        curve = _('ns') if span == 1 else _('se') + (_('ew') * (span-2)) + _('nw')

        tails = [' ' * (r['pathDelta']-1) + box(('ns', r['pen']))
                 for r in rs]

        return ''.join([*heads,
                       curve,
                       *tails])

    for x in range(0,len(ts)):
        print(aux(ts[:x], ts[x:]))

def reflow(text, width):
    return sum([wrap(para, width)
                for para
                in text.split("\n")],
               [])

def definitions(ts, width):
    l = len(ts)
    for x in range(0,len(ts)):
        current = ts[x]
        pen = current['pen']
        rest = ts[x+1:]
        first = ''.join([' ' * x,
                         box(('ne', pen)),
                         *([box(('ew', pen), ('ns', t['pen']))
                            for t in rest]),
                         box(('ew', pen)),
                         ' '])
        then = ''.join([' ' * (x+1),
                        *([box(('ns', t['pen']))
                           for t in rest]),
                        '  '])
        text = reflow(ts[x]['comment'], width - (l+2))
        print("\n".join(
            [h+t
             for (h,t)
             in zip(chain([first], repeat(then)),
                    text)]))

def explain(descs, width=80):
    ts = tokens(descs)
    header(ts)

    ts = list(withOffsets(ts))
    markers(ts)
    converge(ts)
    definitions(ts, width)


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

