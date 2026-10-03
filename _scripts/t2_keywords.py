"""为 T2 选题核对关键词量与难度（Semrush CA 实测）。"""
import io, re
import pandas as pd, numpy as np

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower().str.strip()

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

TOPICS = {
    '/guides/how-long-does-a-hair-dryer-last/': r'how long.*hair dryer|hair dryer lifespan|hair dryer last|long lasting hair dryer|durable hair dryer|hair dryer life',
    '/hair-types/curly-hair/':            r'curly hair|curls|wavy hair|hair dryer for curls|diffuser for curly',
    '/hair-types/fine-hair/':             r'fine hair|thin hair|thinning hair',
    '/hair-types/thick-hair/':            r'thick hair|coarse hair',
    '/hair-types/frizzy-hair/':           r'frizzy hair|anti frizz|frizz control',
    '/hair-types/travel-hair-dryer/':     r'travel hair dryer|dual voltage|portable hair dryer|compact hair dryer|hair dryer for travel',
    '/hair-types/quiet-hair-dryer/':      r'quiet hair dryer|silent hair dryer|low noise hair dryer',
    '/guides/diffuser/':                  r'diffuser',
    '/reviews/dreame/':                   r'dreame',
    '/reviews/slopehill/':                r'slopehill',
    '/reviews/wavytalk/':                 r'wavytalk',
    '/reviews/conair/':                   r'conair',
    '/best-hair-dryers/best-hair-dryer-with-diffuser/': r'best .*diffus|best hair dryer with diffus',
    '/comparisons/laifen-vs-shark/':      r'laifen vs shark|shark vs laifen',
}

P('=' * 116)
P('T2 选题关键词核对（Semrush CA）')
P('=' * 116)
P(f"{'拟建页面':<52}{'相关词数':>9}{'月搜索量':>10}{'中位KD':>8}{'最大单词量':>11}")
P('-' * 116)
rows = []
for path, pat in TOPICS.items():
    s = m[m['kw'].str.contains(pat, regex=True, na=False) & (m['Volume'] > 0)]
    nz = s[s['KD'].notna()]['KD']
    top = s.nlargest(1, 'Volume')
    rows.append({'page': path, 'kws': len(s), 'vol': int(s['Volume'].sum()),
                 'kd': (round(nz.median(), 1) if len(nz) else np.nan),
                 'maxvol': int(s['Volume'].max()) if len(s) else 0,
                 'topkw': (top['Keyword'].iloc[0] if len(top) else '')})
    P(f"{path:<52}{len(s):>9,}{int(s['Volume'].sum()):>10,}"
      f"{(round(nz.median(),1) if len(nz) else 0):>8}{int(s['Volume'].max()) if len(s) else 0:>11,}")

P('')
P('=' * 116)
P('各选题的头部关键词（前 8）')
P('=' * 116)
for r in rows:
    s = m[m['kw'].str.contains(TOPICS[r['page']], regex=True, na=False) & (m['Volume'] > 0)]
    P(f"\n### {r['page']}   （{r['vol']:,}/月）")
    for _, x in s.nlargest(8, 'Volume').iterrows():
        P(f"   {int(x['Volume']):>6,}  KD={str(x['KD'] if pd.notna(x['KD']) else '-'):>4}  {x['Keyword']}")

io.open('analysis/_t2_keywords.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_t2_keywords.txt')
