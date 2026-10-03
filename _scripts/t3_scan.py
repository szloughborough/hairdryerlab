"""T3 长尾选题盘点：未建页的产品 + 型号级/品牌级关键词真实搜索量。"""
import io
import re
import pandas as pd

# ---------- 1. 已有数据但未建独立页的产品 ----------
t = io.open('site/src/data/products.ts', encoding='utf-8').read()
prods = []
for m in re.finditer(r'\{([^{}]*)\}', t, re.S):
    b = m.group(1)
    a = re.search(r"asin:\s*'([A-Z0-9]{10})'", b)
    if not a:
        continue
    def g(k):
        x = re.search(k + r":\s*(?:'([^']*)'|\"([^\"]*)\"|([^,\n]+))", b)
        return ((x.group(1) or x.group(2) or x.group(3)) if x else '-').strip()
    prods.append(dict(asin=a.group(1), brand=g('brand'), line=g('line'),
                      price=g('priceCAD'), rating=g('rating'), n=g('ratingCount'),
                      units=g('unitsMonth'), bsr=g('bsr')))

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P('=' * 118)
P('已有数据但尚未建独立页的产品（T3 候选）')
P('=' * 118)
P(f"{'品牌':<12}{'型号':<38}{'价格':>8}{'评分':>6}{'评论数':>9}{'月销量':>8}{'BSR':>5}")
P('-' * 118)
for p in sorted(prods, key=lambda x: -int(x['units'] or 0)):
    P(f"{p['brand']:<12}{p['line']:<38}{p['price']:>8}{p['rating']:>6}{p['n']:>9}{p['units']:>8}{p['bsr']:>5}")

# ---------- 2. 关键词量 ----------
m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower()
DRY = r'(dryer|drier|blow dry|blowdry|hair dry)'

TOPICS = {
    'revlon 品牌':      r'revlon',
    'remington 品牌':   r'remington',
    'aina 品牌':        r'aina',
    'laifen 型号级':    r'laifen (air|se|swift|se2|se lite)',
    'dreame 型号级':    r'dreame (pocket|hair|ultra)',
    'slopehill 型号级': r'slopehill',
    'shark 型号级':     r'shark (speedstyle|flexstyle|hyperair)',
    'conair 型号级':    r'conair (infiniti|318|330|flomotion|pro)',
    'wavytalk 型号级':  r'wavytalk',
    'laifen vs shark':  r'laifen vs shark|shark vs laifen',
    'dreame vs laifen': r'dreame vs laifen|laifen vs dreame',
    'damaged/bleached': r'damaged hair|bleached hair|color treated|colour treated',
    'dual voltage':     r'dual voltage|voltage converter',
}

P('')
P('=' * 118)
P('T3 关键词真实搜索量（仅含 dryer 词根）')
P('=' * 118)
P(f"{'主题':<22}{'词数':>6}{'月搜索量':>10}{'中位KD':>8}   头部词")
P('-' * 118)
rows = []
for label, pat in TOPICS.items():
    s = m[m['kw'].str.contains(pat, regex=True, na=False)
          & m['kw'].str.contains(DRY, regex=True, na=False) & (m['Volume'] > 0)]
    kd = s['KD'].notna()
    med = s[kd]['KD'].median() if kd.any() else 0
    tl = ' | '.join(f"{r['Keyword']} ({int(r['Volume']):,})"
                    for _, r in s.nlargest(3, 'Volume').iterrows())
    rows.append((label, len(s), int(s['Volume'].sum()), med))
    P(f"{label:<22}{len(s):>6}{int(s['Volume'].sum()):>10,}{med:>8.0f}   {tl}")

P('')
P('按搜索量排序：')
for label, n, v, med in sorted(rows, key=lambda x: -x[2]):
    P(f'  {v:>7,}/月   词数 {n:<4} KD中位 {med:<5.0f} {label}')

io.open('analysis/_t3_scan.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_t3_scan.txt')
