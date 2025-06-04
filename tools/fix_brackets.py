import glob, os, re
pairs = [
    ('(', ')'),
    ('（', '）'),
    ('【', '】'),
    ('『', '』'),
]
root = os.path.dirname(os.path.dirname(__file__)) if __file__.startswith('/') else os.path.join(os.getcwd(), 'tools')
files = sorted(glob.glob(os.path.join(root, 'src', '*.txt')))
for path in files:
    updated_lines = []
    changed = False
    with open(path, encoding='utf-8') as f:
        for line in f:
            orig = line
            line = line.rstrip('\n')
            if not line.strip():
                updated_lines.append(orig)
                continue
            cols = line.split('\t')
            if len(cols) < 2:
                updated_lines.append(orig)
                continue
            text = cols[1]
            for o, c in pairs:
                cnt_o = text.count(o)
                cnt_c = text.count(c)
                if cnt_o == cnt_c:
                    continue
                diff = cnt_o - cnt_c
                if diff > 0:
                    text += c * diff
                    changed = True
                elif diff < 0:
                    # remove extra closing brackets from the end
                    for _ in range(-diff):
                        idx = text.rfind(c)
                        if idx != -1:
                            text = text[:idx] + text[idx+1:]
                            changed = True
            cols[1] = text
            updated_lines.append('\t'.join(cols) + '\n')
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print('fixed', os.path.basename(path))
