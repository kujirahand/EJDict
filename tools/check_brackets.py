import csv
import glob
import os
import re

pairs = [
    ('(', ')'),
    ('（', '）'),
    ('【', '】'),
    ('『', '』'),
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
            text = cols[1]
            # remove enumeration patterns like "a)" or "1)" which are not
            # part of bracket pairs
            cleaned = re.sub(r"\b[a-zA-Z0-9]\)", "", text)
            for o, c in pairs:
                if cleaned.count(o) != cleaned.count(c):
                    errors.append((os.path.basename(path), lineno, o, c, text))
                    break

if errors:
    for fname, lineno, o, c, text in errors:
        print(f"{fname}:{lineno}: mismatched {o}{c}: {text}")
else:
    print("No mismatches found.")
