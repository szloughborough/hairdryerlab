"""列出 a/an/the about 残留的实际上下文，判断哪些是真错。"""
import glob
import io
import re

D = 'site/dist'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

PATS = [r'\ba about\b', r'\ban about\b', r'\bthe about\b']
P('=' * 96)
P('上下文明细')
P('=' * 96)
for p in glob.glob(f'{D}/**/*.html', recursive=True):
    h = io.open(p, encoding='utf-8').read()
    txt = re.sub(r'<[^>]+>', ' ', h)
    txt = re.sub(r'\s+', ' ', txt)
    rel = p.replace(D + '\\', '').replace(D + '/', '')
    for pat in PATS:
        for m in re.finditer(pat, txt, re.I):
            s = max(0, m.start() - 70)
            e = min(len(txt), m.end() + 70)
            P(f'{rel}')
            P(f'    ...{txt[s:e].strip()}...')
            P('')

io.open('analysis/_planb_contexts.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_planb_contexts.txt')
