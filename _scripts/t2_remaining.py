"""T2 剩余选题的真实搜索量核对（只统计含 dryer/diffuser 词根的词）。"""
import io
import pandas as pd

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower()
DRY = r'(dryer|drier|blow dry|blowdry|hair dry)'

TOPICS = {
    '/hair-types/quiet-hair-dryer/':        r'quiet|silent|low noise',
    '/hair-types/lightweight-hair-dryer/':  r'lightweight|light weight|light-weight',
    '/best-hair-dryers/fast-drying/':       r'fast dry|quick dry|powerful|high speed|high-speed',
    '/best-hair-dryers/premium/':           r'premium|expensive|best hair dryer\b|luxury|high end',
    '/best-hair-dryers/under-150/':         r'under \$?1[05]0|budget|cheap|affordable|best budget',
    '/guides/how-many-watts/':              r'watt|2000w|1875w|1600w',
    '/guides/hair-dryer-care/':             r'clean hair dryer|hair dryer filter|maintenance|hair dryer care|fix hair dryer|repair',
    '/guides/dual-voltage/':                r'dual voltage|voltage converter|travel adapter',
    '/best-hair-dryers/best-travel-hair-dryer/': r'travel|portable|compact|folding',
    '/hair-types/damaged-hair/':            r'damaged hair|heat damage|color treated|colour treated|bleached',
}

out = []
def P(*a):
    out.append(' '.join(str(x) for x in a))

P('=' * 112)
P('T2 剩余选题（仅统计含 dryer 词根的词）')
P('=' * 112)
P(f"{'拟建页面':<46}{'词数':>6}{'月搜索量':>10}{'中位KD':>8}   头部词")
P('-' * 112)
rows = []
for path, pat in TOPICS.items():
    s = m[m['kw'].str.contains(pat, regex=True, na=False)
          & m['kw'].str.contains(DRY, regex=True, na=False)
          & (m['Volume'] > 0)]
    kd = s['KD'].notna()
    med = s[kd]['KD'].median() if kd.any() else 0
    top = s.nlargest(3, 'Volume')
    tl = ' | '.join(f"{r['Keyword']} ({int(r['Volume']):,})" for _, r in top.iterrows())
    rows.append((path, len(s), int(s['Volume'].sum()), med))
    P(f"{path:<46}{len(s):>6}{int(s['Volume'].sum()):>10,}{med:>8.0f}   {tl}")

P('')
P('按搜索量排序：')
for path, n, v, med in sorted(rows, key=lambda x: -x[2]):
    P(f'  {v:>8,}/月   词数 {n:<5} KD中位 {med:<5.0f} {path}')

io.open('analysis/_t2_remaining.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_t2_remaining.txt')
