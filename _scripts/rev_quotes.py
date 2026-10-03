"""Extract representative quotes per pain point, price-tier split, French detection."""
import re, io, zipfile
import pandas as pd, numpy as np

R = pd.read_pickle('analysis/reviews.pkl')
R['rating'] = pd.to_numeric(R['rating'], errors='coerce')
R = R.dropna(subset=['rating']).copy()
R['text_l'] = R['text'].str.lower()

# ---- attach brand / price from BSR (needed for price-tier split)
if 'price' not in R.columns:
    BSR = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
    z = zipfile.ZipFile(BSR)
    S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)).replace('&amp;', '&').replace('&apos;', "'")
         for s in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8'), re.S)]
    b = pd.read_excel(BSR, sheet_name='CA', header=0); b.columns = S[:71]
    b = b[['ASIN', '品牌', '价格(C$)']].rename(columns={'品牌': 'brand', '价格(C$)': 'price'})
    b['price'] = pd.to_numeric(b['price'], errors='coerce')
    R = R.merge(b, on='ASIN', how='left')
    R['brand'] = R['brand'].fillna('(未在Top50)')

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

def quotes(pat, neg=True, n=5, minlen=60, maxlen=420):
    m = R['text_l'].str.contains(pat, regex=True, na=False)
    m &= (R['rating'] <= 2) if neg else (R['rating'] >= 4)
    sub = R[m & (R['text'].str.len().between(minlen, maxlen))]
    sub = sub.sort_values('helpful', ascending=False) if 'helpful' in sub else sub
    res = []
    for _, r in sub.head(n).iterrows():
        t = re.sub(r'\s+', ' ', str(r['text'])).strip()
        res.append(f"   [{int(r['rating'])}★] {t[:300]}")
    return res

P("=" * 118)
P("痛点原声（1-2星，按有用数排序）—— 直接回答「用户到底在抱怨什么」")
P("=" * 118)

PAINS = {
    '耐用性/故障 (946条差评, 负面占比84%)':
        r'\bbroke|broken|stopped working|stop working|stopped after|died|dead|quit working|no longer works|lasted|fell apart',
    '客服/保修 (610条, 81%)':
        r'\bcustomer service|warranty|guarantee|return|refund|replaced|customer support',
    '温度/过热 (590条, 54%)':
        r'\btoo hot|overheat|over heat|burn|scorch|melt|heat setting|scald|gets hot',
    '异味/烧焦味 (180条, 84%)':
        r'\bburning smell|burning|smell|odor|smells like|plastic smell|smoke',
    '风力/干发速度 (556条, 35%)':
        r'\bnot powerful|weak|takes forever|slow to dry|airflow|air flow|blows',
    '操作/握持 (617条, 39%)':
        r'\bbutton|hard to use|cumbersome|confusing|dial|switch|awkward',
    '配件/风嘴 (417条, 36%)':
        r'\bdiffus|nozzle|concentrator|attach|accessor',
    '安全/自动断电 (341条, 47%)':
        r'\bauto.?shut|shut off|safety|sparks|fuse|circuit|breaker',
    '冷风 (150条, 52%)':
        r'\bcold shot|cool shot|cool air|cool button',
    '滤网/清洁 (76条, 53%)':
        r'\bfilter|lint|clog|dust',
    '做工/材质 (183条, 45%)':
        r'\bplastic|flimsy|cheaply made|feels cheap',
}
for name, pat in PAINS.items():
    P(f"\n### {name}")
    qs = quotes(pat, neg=True, n=5)
    P('\n'.join(qs) if qs else "   (无符合长度的引用)")

P("\n\n" + "=" * 118)
P("满意点原声（4-5星）—— 这些是推荐理由的素材")
P("=" * 118)
GAINS = {
    '风力/干发速度': r'\bpowerful|fast dry|dries fast|drying time',
    '重量': r'\blightweight|light weight|light-?weight',
    '尺寸/收纳': r'\bcompact|small|fold|portable',
    '护发效果': r'\bfrizz|shiny|smooth|silky|soft',
    '性价比': r'\bworth it|good value|great value|bang for',
}
for name, pat in GAINS.items():
    P(f"\n### {name}")
    qs = quotes(pat, neg=False, n=3)
    P('\n'.join(qs) if qs else "   (无)")

# ---------------- price tier ----------------
P("\n\n" + "=" * 118)
P("★ 按价格带拆分 —— 不同价位段的用户关心什么不同？")
P("=" * 118)
R['tier'] = pd.cut(R['price'], [0, 50, 120, 10000], labels=['预算 <C$50', '中端 C$50-120', '高端 >C$120'])
THEMES = {
    '耐用性/故障': r'\bbroke|broken|stopped working|died|lasted|durab|defect',
    '温度/过热': r'\btoo hot|overheat|burn|heat setting|temperature|gets hot',
    '风力/速度': r'\bpowerful|weak|fast dry|drying time|airflow|blows',
    '操作/握持': r'\bbutton|setting|easy to use|handle|dial|switch',
    '配件/风嘴': r'\bdiffus|nozzle|attach|accessor',
    '重量': r'\bheavy|weight|lightweight|light weight',
    '噪音': r'\bnois|\bloud|quiet|silent',
    '客服/保修': r'\bcustomer service|warranty|return|refund',
    '性价比': r'\bworth it|overpriced|value|price',
}
P(f"{'主题':<16}{'预算<C$50':>12}{'中端50-120':>13}{'高端>120':>12}   (占该价位段评论的%)")
P("-" * 78)
for name, pat in THEMES.items():
    line = f"{name:<16}"
    for tier in ['预算 <C$50', '中端 C$50-120', '高端 >C$120']:
        sub = R[R['tier'] == tier]
        if len(sub) == 0:
            line += f"{'—':>12}"; continue
        pct = 100 * sub['text_l'].str.contains(pat, regex=True, na=False).mean()
        line += f"{pct:>11.1f}%"
    P(line)
P("")
for tier in ['预算 <C$50', '中端 C$50-120', '高端 >C$120']:
    sub = R[R['tier'] == tier]
    if len(sub):
        P(f"  {tier}: {len(sub):,} 条评论, 平均 {sub['rating'].mean():.2f} 星, "
          f"差评率 {100*(sub['rating']<=2).mean():.1f}%")

# ---------------- French ----------------
P("\n" + "=" * 118)
P("★ 法语评论（魁北克机会）")
P("=" * 118)
FR = r'\bsèche|seche|cheveux|très|tres bien|puissant|chaud|bruit|léger|leger|fonctionne|acheté|jai |je suis|pour ma|avec |mais |bonne|excellent|vite'
R['is_fr'] = R['text_l'].str.contains(FR, regex=True, na=False)
P(f"疑似法语评论: {R['is_fr'].sum():,} 条 ({100*R['is_fr'].mean():.1f}%)")
P(f"法语平均星级: {R[R['is_fr']]['rating'].mean():.2f}")
P("\n法语评论样例:")
for _, r in R[R['is_fr']].head(8).iterrows():
    P(f"   [{int(r['rating'])}★] {re.sub(chr(10),' ',str(r['text']))[:180]}")

# ---------------- review length & helpful ----------------
P("\n" + "=" * 118)
P("辅助指标")
P("=" * 118)
P(f"平均评论长度: {R['text'].str.len().mean():.0f} 字符")
P(f"长评论(>300字符)占比: {100*(R['text'].str.len()>300).mean():.1f}%")
P(f"含图评论均星: {R[R['n_images'].notna()]['rating'].mean():.2f}  vs  无图: {R[R['n_images'].isna()]['rating'].mean():.2f}")

with io.open('analysis/_rev_quotes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("written analysis/_rev_quotes.txt")
