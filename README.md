Sketch of https://explainshell.com/ like output, in plain text

```
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
```

*NB:* if you're using a good font like `Menlo` with support for Unicode box-drawing
characters, you can pass `usePens=True` to alternate each line bold/normal to
make it easier to read.

(With many fonts, the bold characters default to variable width.)
