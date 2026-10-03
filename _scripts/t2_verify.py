"""复核有疑问的选题：排除 clothes dryer 污染，检查与已有页面的关键词重叠（自噬风险）。"""
import io
import pandas as pd

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower()

HAIR = r'hair|blow ?dry|blowdry|styl|salon|diffus|ionic'
NOT_CLOTHES = r'clothes|garment|laundry|vent|general electric|\bge\b|whirlpool|maytag|samsung dryer|lg dryer|stack'

out = []
def P(*a):
    out.append(' '.join(str(x) for x in a))

def show(label, pat, extra_exclude=None):
    s = m[m['kw'].str.contains(pat, regex=True, na=False) & (m['Volume'] > 0)]
    s_hair = s[s['kw'].str.contains(HAIR, regex=True, na=False)]
    s_clean = s_hair[~s_hair['kw'].str.contains(NOT_CLOTHES, regex=True, na=False)]
    P(f'### {label}')
    P(f'  原始 {len(s)} 词 / {int(s["Volume"].sum()):,}月')
    P(f'  含 hair 词根: {len(s_hair)} 词 / {int(s_hair["Volume"].sum()):,}月')
    P(f'  再去掉衣服烘干机: {len(s_clean)} 词 / {int(s_clean["Volume"].sum()):,}月  ← 真实机会')
    if len(s_clean):
        kd = s_clean['KD'].notna()
        P(f'  KD 中位: {s_clean[kd]["KD"].median():.0f}')
        for _, r in s_clean.nlargest(6, 'Volume').iterrows():
            P(f'     {int(r["Volume"]):>6,}  KD={str(r["KD"] if pd.notna(r["KD"]) else "-"):>4}  {r["Keyword"]}')
    P('')

P('=' * 100)
P('复核：排除 clothes dryer 污染')
P('=' * 100)
show('hair dryer care / maintenance / repair',
     r'clean hair dryer|hair dryer filter|hair dryer maintenance|hair dryer care|fix hair dryer|hair dryer repair|hair dryer not working|hair dryer stopped')
show('quiet hair dryer', r'quiet|silent|low noise|noise')
show('wattage', r'watt|\bw\b hair dryer|2000w|1875w|1600w')
show('under budget', r'bunder|budget|cheap|affordable|inexpensive')
show('fast drying', r'fast dry|quick dry|powerful|high speed|high-speed|fastest')

P('=' * 100)
P('自噬检查：这些词是否已被现有页面覆盖')
P('=' * 100)
for label, pat in [
    ('/best-hair-dryers/ (支柱页 已有)', r'best hair dryer|top hair dryer'),
    ('/hair-types/travel-hair-dryer/ (已有)', r'travel hair dryer|dual voltage|portable|compact|folding'),
    ('/best-hair-dryers/dyson-alternatives/ (已有)', r'dyson alternative|dupe|cheaper than dyson'),
]:
    s = m[m['kw'].str.contains(pat, regex=True, na=False) & (m['Volume'] > 0)]
    s = s[s['kw'].str.contains(HAIR, regex=True, na=False)]
    P(f'  {label}: {len(s)} 词 / {int(s["Volume"].sum()):,}月')

io.open('analysis/_t2_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_t2_verify.txt')
