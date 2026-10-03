"""细查 T3 两个疑问：Revlon 是否是品类错配；dual-voltage 与已有旅行页的重叠度。"""
import io
import pandas as pd

m = pd.read_pickle('analysis/master.pkl')
m['kw'] = m['Keyword'].astype(str).str.lower()
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P('=' * 110)
P('疑问一：Revlon 的搜索量到底是吹风机还是热风梳？')
P('=' * 110)
rv = m[m['kw'].str.contains('revlon', na=False) & (m['Volume'] > 0)]
BRUSH = r'brush|one.?step|volumiz|styl|round|blow.?dry brush|hot air|airbrush'
DRYER = r'hair dryer|blow dryer|blowdryer'
b = rv[rv['kw'].str.contains(BRUSH, regex=True, na=False)]
d = rv[~rv['kw'].str.contains(BRUSH, regex=True, na=False)]
P(f'  Revlon 总词数 {len(rv)} / {int(rv["Volume"].sum()):,}月')
P(f'  ├ 含 brush/styler 词根（热风梳类）: {len(b)} 词 / {int(b["Volume"].sum()):,}月')
P(f'  └ 不含（可能是真吹风机）        : {len(d)} 词 / {int(d["Volume"].sum()):,}月')
P('')
P('  「不含 brush」那部分的头部词（即真正的吹风机需求）:')
for _, r in d.nlargest(12, 'Volume').iterrows():
    P(f'     {int(r["Volume"]):>6,}  KD={str(r["KD"] if pd.notna(r["KD"]) else "-"):>4}  {r["Keyword"]}')
P('')
P('  含 brush 那部分的头部词（我们没数据的产品类型）:')
for _, r in b.nlargest(5, 'Volume').iterrows():
    P(f'     {int(r["Volume"]):>6,}  {r["Keyword"]}')

P('')
P('=' * 110)
P('疑问二：dual-voltage 与已有 /hair-types/travel-hair-dryer/ 的重叠')
P('=' * 110)
dv = m[m['kw'].str.contains(r'dual voltage|voltage converter|110.?240|220v', regex=True, na=False) & (m['Volume'] > 0)]
HAIR = r'hair|blow ?dry|blowdry|styl|diffus'
dv_h = dv[dv['kw'].str.contains(HAIR, regex=True, na=False)]
P(f'  纯 voltage 相关（全部）: {len(dv)} 词 / {int(dv["Volume"].sum()):,}月')
P(f'  其中含 hair 词根        : {len(dv_h)} 词 / {int(dv_h["Volume"].sum()):,}月')
BRUSHP = r'brush'
P(f'  再排除 brush（热风梳）  : {len(dv_h[~dv_h["kw"].str.contains(BRUSHP, na=False)])} 词 / '
  f'{int(dv_h[~dv_h["kw"].str.contains(BRUSHP, na=False)]["Volume"].sum()):,}月  ← 真实可争的量')
P('')
P('  头部词:')
for _, r in dv_h.nlargest(10, 'Volume').iterrows():
    P(f'     {int(r["Volume"]):>6,}  KD={str(r["KD"] if pd.notna(r["KD"]) else "-"):>4}  {r["Keyword"]}')

P('')
P('=' * 110)
P('疑问三：型号级词的意图（能否与品牌枢纽页区分开）')
P('=' * 110)
for label, pat in [('laifen 型号', r'laifen (swift|se|air|se2|se lite)'),
                   ('dreame 型号', r'dreame (pocket|hair)'),
                   ('shark 型号', r'shark (speedstyle|flexstyle|hyperair)')]:
    s = m[m['kw'].str.contains(pat, regex=True, na=False) & (m['Volume'] > 0)]
    P(f'  {label}: {int(s["Volume"].sum()):,}月')
    for _, r in s.nlargest(6, 'Volume').iterrows():
        P(f'     {int(r["Volume"]):>6,}  KD={str(r["KD"] if pd.notna(r["KD"]) else "-"):>4}  {r["Keyword"]}')

io.open('analysis/_t3_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_t3_verify.txt')
