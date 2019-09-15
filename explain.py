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
from textwrap import (wrap, dedent)
from operator import itemgetter
import string
import re

'''
Take a list of descriptions, which are either a literal string or a tuple of
string + description, and return a list of tuples of
(string, desc, length, offset)

e.g.
    ["ls ",
     ("*.py", "wildcard search for files that end with `.py`")]

would become:
    [("ls ", None, 3, 0),
     ("*.py", "wildcard search for files that end with `.py`", 4, 3)]
'''
def normalise_tokens(tokens):
    def norm(token):
        (t,c) = token if type(token) is tuple else (token, None)
        l = len(t)
        # return tuple of token, comment, length, and a dummy offset of 0
        return (t,c,l,0)

    def offset(a, b):
        (_, _, alength, aoffset) = a
        return (*b[0:3], aoffset + alength)

    hasComment = itemgetter(1)

    ntokens = [norm(desc) for desc in descs]
    header = ''.join([ntoken[0] for ntoken in ntokens])

    lanes = list(filter(hasComment,
                        accumulate(ntokens, offset)))

    return (header, lanes)

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

def resolve(existing, instructions, width=65):

    fst = itemgetter(0)
    snd = itemgetter(1)

    n = drawverticals('n', existing)

    pens = {pos: pen for (pos,pen,*_) in existing}
    texts = {pos: text for (pos,_,text,*_) in existing}

    ew = overlay([drawhorizontal(i['pos'], i['to'], pens[i['pos']])
                  for i
                  in instructions
                  if 'to' in i])

    explicit = {i['pos'] for i in instructions}
    implicit = [(pos, *rest)
                for (pos, *rest)
                in existing
                if not pos in explicit]

    def cont(i):
        f = i['pos']
        t = i['to']
        return (t, pens[f], texts[f])
    continuation = [cont(i)
                    for i in instructions
                    if not 'go' in i]\
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

    gone = next(filter(lambda i: 'go' in i, instructions), None)
    if gone:
        l = len(lines)
        text = reflow(texts[gone['pos']], width - l - 1)
        (then, _) = resolve(nextState, [])
        first = lines + ' '
        then = then + ' ' * (len(first) - len(then))
        lines = ("\n".join(
                    [h+t
                     for (h,t)
                     in zip(chain([first], repeat(then)),
                            text)]))

    return (lines, nextState)

def move(f, t):
    return {'pos': f, 'to': t}

def go(f, t):
    return {'pos': f, 'to': t, 'go': True}

def nmarkers(ts):
    usePens = True # TODO pass in
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

    instructions = flatten([[move(start, mean),
                             move(end, mean)]
                            for (start, mean, end, comment, _)
                            in ps])

    return resolve(pre, instructions)

def toleft_instructions(lanes):
    def aux(lanes, idx):
        pos = lanes[idx][0]
        return move(pos, idx)

    return [[aux(lanes, idx)] for idx in range(0, len(lanes))]

def define_instructions(lanes):
    l = len(lanes) + 1
    def aux(lane):
        pos = lane[0]
        return go(pos, l)

    return [[aux(lane)] for lane in lanes]

def toleft(lanes):
    return resolve_list(lanes, toleft_instructions(lanes))

def define(lanes):
    return resolve_list(lanes, define_instructions(lanes))

def resolve_list(lanes, instructions):
    def aux(output_lanes, i):
        (o, lanes) = output_lanes
        (o2, lanes2) = resolve(lanes, i)
        return (o + [o2], lanes2)

    (output, lanes) = reduce(aux, instructions, ([], lanes))
    return ('\n'.join(output), lanes)

def unit(data):
    return ("", data)

def bind(t, f):
    (o, x) = t
    (o2, x2) = f(x)
    return (o + o2 + "\n", x2)

def sequence(t, fs):
    return reduce(bind, fs, t)

def run(t, fs):
    (output, _) = sequence(unit(t), fs)
    print(output)

def explain(tokens):
    run(tokens,
        [normalise_tokens,
         nmarkers,
         toleft,
         define ])

def parse1(string):
    (command, markers, *data) = string.split("\n")
    
    groups = groupby(zip(command, markers), key=itemgetter(1))

    def aux(g):
        group = g[0]
        command = ''.join(list(map(itemgetter(0), g[1])))
        return (group, command)

    print([aux(g) for g in groups])

explain(descs)

def parseres(string, rxs):
    def aux(acc, token):
        last = acc[-1][-1]
        rx = re.escape(token)
        match = re.compile(rx).search(string, last)
        if match:
            return acc + [(token, match.start(), match.end())]
        else:
            raise Exception("BAD PROGRAMMER")

    slices = reduce(aux, rxs, [(0,)])[1:]

    t = len(string)
    def fill(i, ss):
        if i == t:
            return []
        if not ss:
            return [(string[i:t], i,t)]
        [(token, s,e),*rest] = ss
        if i == s:
            return [(token, s,e)] + fill(e, rest)
        else:
            return [(string[i:s], i,s), (token, s,e)] + fill(e, rest)

    return fill(0, slices)

def parse(string):
    ...

parse("""\
      git log -m thingy
      # git
      version control ting

      # log
      do some logging innit""")

# print(parseres("git log -m thingy", ["git", "log", "-m"]))
