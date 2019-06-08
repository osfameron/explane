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

NB: if you're using a good font like `Menlo` with support for Unicode box-drawing
characters, you can pass `usePens=True` to alternate each line bold/normal to
make it easier to read.

(With many fonts, the bold characters default to variable width.)
"""

import itertools
import math
from itertools import (accumulate, chain, repeat, cycle, groupby, zip_longest)
from functools import reduce
from textwrap import wrap
from operator import itemgetter
import string

def ntokens(descs):
    def norm(desc):
        (t,c) = desc if type(desc) is tuple else (desc, None)
        return (t, c, len(t))

    raw = [norm(desc) for desc in descs]
    header = ''.join([item[0] for item in raw])

    def offset(a, b):
        return (*b, a[3] + a[2])

    ri = [(*raw[0], 0)] + raw[1:]
    withOffsets = list(accumulate(ri, offset))

    comment = itemgetter(1)

    return (header, list(filter(comment, withOffsets)))

boxes = {
        'ew': '─', 'EW': '━', 'ns': '│', 'NS': '┃', 'se': '┌',
        'sE': '┍', 'Se': '┎', 'SE': '┏', 'sw': '┐', 'sW': '┑',
        'Sw': '┒', 'SW': '┓', 'ne': '└', 'nE': '┕', 'Ne': '┖',
        'NE': '┗', 'nw': '┘', 'nW': '┙', 'Nw': '┚', 'NW': '┛',
        'nse': '├', 'nsE': '┝', 'Nse': '┞', 'nSe': '┟', 'NSe': '┠',
        'NsE': '┡', 'nSE': '┢', 'NSE': '┣', 'nsw': '┤', 'nsW': '┥',
        'Nsw': '┦', 'nSw': '┧', 'NSw': '┨', 'NsW': '┩', 'nSW': '┪',
        'NSW': '┫', 'sew': '┬', 'seW': '┭', 'sEw': '┮', 'sEW': '┯',
        'Sew': '┰', 'SeW': '┱', 'SEw': '┲', 'SEW': '┳', 'new': '┴',
        'neW': '┵', 'nEw': '┶', 'nEW': '┷', 'New': '┸', 'NeW': '┹',
        'NEw': '┺', 'NEW': '┻', 'nsew': '┼', 'nseW': '┽', 'nsEw': '┾',
        'nsEW': '┿', 'Nsew': '╀', 'nSew': '╁', 'NSew': '╂', 'NseW': '╃',
        'NsEw': '╄', 'nSeW': '╅', 'nSEw': '╆', 'NsEW': '╇', 'nSEW': '╈',
        'NSeW': '╉', 'NSEw': '╊', 'NSEW': '╋', 'w': '╴', 'n': '╵',
        'e': '╶', 's': '╷', 'W': '╸', 'N': '╹', 'E': '╺',
        'S': '╻', 'Ew': '╼', 'nS': '╽', 'eW': '╾', 'Ns': '╿'}

box2recipe = {v: k for (k,v) in boxes.items() }

def overlayc(a,b):
    # anything beats a space
    if a == ' ':
        return b
    elif b == ' ':
        return a

    # anything that isn't a box character wins
    ar = box2recipe.get(a, None)
    br = box2recipe.get(b, None)
    if not ar:
        return a
    elif not br:
        return b

    # otherwise we have two box recipes! Compose them
    return box(ar, br)

def overlay2(aa,bb):
    return ''.join([overlayc(a, b)
                    for (a,b)
                    in zip_longest(aa,bb, fillvalue=' ')])

def overlay(items):
    return reduce(overlay2, items, '')

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

def flatten(lol):
    return sum(lol, [])

def reflow(text, width):
    return flatten([wrap(para, width)
                    for para
                    in text.split("\n")])


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

def drawat(pos, string):
    return (' ' * pos) + string

def drawhorizontal(a,b,pen):
    (a,b) = sorted((a,b))
    l = b-a
    if l:
        line = ''.join([box(('e',pen)),
                        box(('ew',pen)) * (l-1),
                        box(('w',pen))])
        return drawat(a, line)
    else:
        return ''

def drawverticals(point, items):
    return overlay([drawat(pos, box((point, pen))) for (pos,pen,*_) in items])

def resolve(existing, instructions, width=80):

    fst = itemgetter(0)
    snd = itemgetter(1)

    n = drawverticals('n', existing)

    exp = {pos: pen for (pos,pen,*_) in existing}
    ext = {pos: text for (pos,_,text,*_) in existing}

    def dest(i):
        return list(filter(lambda a: type(a) is int, i))[-1]
    def pen(i):
        return next(filter(lambda a: type(a) is bool, i), False)
    def go(i):
        return next(filter(lambda a: a is Ellipsis, i), None)

    def normalise(instruction):
        f = fst(instruction)
        t = dest(instruction)
        p = exp.get(f, pen(instruction))
        tx = ext.get(f, None)
        g = go(instruction)
        return (f,t,p,tx,g)

    normalised = [normalise(i) for i in instructions]

    ew = overlay([drawhorizontal(a,b,pen)
                  for (a,b,pen,*_)
                  in normalised
                  if a is not None and b is not None])

    explicit = {fst(i) for i in normalised}
    implicit = [(pos, *rest)
                for (pos, *rest)
                in existing
                if not pos in explicit]

    continuation = [(t,pen,comment)
                    for (f,t,pen,comment,go) in normalised
                    if not go]\
                   + implicit

    # sorted and merged paths
    def aux(k,v):
        v = list(v)
        pen = any(map(snd, v))
        [(_,_,comment), *_] = v
        return (k, pen, comment)

    nextState = [aux(k,v)
                 for (k, v)
                 in groupby(sorted(continuation, key=fst), fst)]

    s = drawverticals('s', nextState)
    lines = overlay([n, ew, s])

    gone = next(filter(go, normalised), None)
    if gone:
        l = len(lines)
        text = reflow(gone[3], width - l - 1)
        (then, _) = resolve(nextState, [])
        lines = ("\n".join(
                    [h+t
                     for (h,t)
                     in zip(chain([lines + ' '], repeat(then + '   ')),
                            text)]))

    return (lines, nextState)

def nmarkers(ts, usePens=False):
    def aux(t):
        (_,c,l,o) = t
        end = o + l - 1
        mean = o + int(l/2)
        return (o, mean, end, c, None)

    ps = list(map(aux, ts))
    pens = cycle([False, True]) if usePens else repeat(False)
    pre = flatten([[(start, pen, comment, None),
                    (end, pen, comment, None)]
                    for ((start, _, end, comment, _), pen)
                    in zip(ps, pens)])

    instructions = flatten([[(start, mean, comment, None),
                             (end, mean, comment, None)]
                            for (start, mean, end, comment, _)
                            in ps])

    return resolve(pre, instructions)

def toleft_instructions(lanes):
    def aux(lanes, idx):
        pos = lanes[idx][0]
        return (pos, idx)

    return [[aux(lanes, idx)] for idx in range(0, len(lanes))]

def define_instructions(lanes):
    l = len(lanes) + 1
    def aux(lane):
        pos = lane[0]
        return (pos, l, ...)

    return [[aux(lane)] for lane in lanes]

def resolve_list(lanes, instructions):
    def aux(output_lanes, i):
        (o, lanes) = output_lanes
        (o2, lanes2) = resolve(lanes, i)
        return (o + [o2], lanes2)

    (output, lanes) = reduce(aux, instructions, ([], lanes))
    return ('\n'.join(output), lanes)

def explain(descs):
    (header, ts) = ntokens(descs)
    print(header)
    (markers, lanes) = nmarkers(ts, usePens=True)
    print(markers)
    (left, lanes) = resolve_list(lanes, toleft_instructions(lanes))
    print(left)
    (define, lanes) = resolve_list(lanes, define_instructions(lanes))
    print(define)


explain(descs)
