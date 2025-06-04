"""対応しない括弧のチェックツール"""

import glob
import os

pairs = [
    ('(', ')'),
    ('[', ']'),
    ('{', '}'),
    ('（', '）'),
    ('【', '】'),
    ('『', '』'),
    ('《', '》'),
    ('「', '」'),
    ('『', '』'),
    ('〔', '〕'),
    ('〖', '〗'),
    ('〈', '〉'),
    ('〔', '〕'),
    ('｛', '｝'),
]

root = os.path.dirname(os.path.dirname(__file__))
files = sorted(glob.glob(os.path.join(root, 'src', '*.txt')))

errors = []

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if not line:
                continue
            cols = line.split('\t')
            if len(cols) < 2:
                continue
            word = cols[0]
            text = cols[1]
            for o, c in pairs:
                num_open = text.count(o)
                num_close = text.count(c)
                if num_open != num_close:
                    base_name = os.path.basename(path)
                    errors.append((
                        base_name,
                        lineno,
                        o,
                        c,
                        word,
                        text,
                        num_open,
                        num_close
                    ))

if errors:
    for fname, lineno, o, c, word, text, no, oc in errors:
        print(f"src/{fname}:{lineno:<4d}: mismatched {o}…{c}: {word}:{text}: {no} open, {oc} close")
    print(f"Total mismatches: {len(errors)}")
else:
    print("No mismatches found.")
