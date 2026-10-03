"""Failure-mode breakdown (durability is #1 concern) + new article opportunities from review language."""
import re, io, zipfile
import pandas as pd, numpy as np

R = pd.read_pickle('analysis/reviews.pkl')
R['rating'] = pd.to_numeric(R['rating'], errors='coerce')
R = R.dropna(subset=['rating']).copy()
R['text_l'] = R['text'].str.lower()
NEG = R['rating'] <= 3

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

# ---------- failure modes ----------
P("=" * 112)
P("★ 故障模式拆解（耐用性是第一痛点，946条差评）")
P("=" * 112)
MODES = {
    '完全停转/彻底坏':      r'stopped working|stop working|no longer works|quit working|\bdied|completely dead|stopped after',
    '电源线/接头故障':      r'\bcord|wire|where it connects|plug.*(broke|spark|loose)',
    '开关/按钮失灵':        r'switch|button.*(broke|loose|stuck|not work)|on and off',
    '加热丝/发热件烧毁':     r'heating coil|heating element|burned out|coil.*(burn|fail)',
    '电机/风量衰减':        r'\bmotor|airflow.*(reduc|weak|stop)|no air',
    '塑料熔化/变形':        r'melt|bulge|deform|warp',
    '冒烟/起火':            r'\bsmoke|caught fire|spark|flame',
    '温度开关(冷热)失效':     r'heat.*(switch|control).*(broke|fail)|only cool air|cold.*switch.*(grill|broke)',
}
rows = []
for name, pat in MODES.items():
    m = R['text_l'].str.contains(pat, regex=True, na=False)
    rows.append({'故障模式': name, '提及数': int(m.sum()),
                 '其中差评': int((m & NEG).sum()),
                 '占比%': round(100 * m.sum() / len(R), 2)})
F = pd.DataFrame(rows).sort_values('提及数', ascending=False)
P(F.to_string(index=False))

P("\n--- 用户报告的「寿命」时长（月） ---")
life = R['text_l'].str.extract(r'(\d+)\s*(?:month|months|mo\b)')[0].astype(float)
life_y = R['text_l'].str.extract(r'(\d+(?:\.\d+)?)\s*(?:year|years|yr)')[0].astype(float)
P(f"  提到「N 个月就坏」的评论: {life.notna().sum()} 条, 中位 {life.median()} 个月, 均值 {life.mean():.1f} 个月")
P(f"  提到「N 年」的评论:      {life_y.notna().sum()} 条, 中位 {life_y.median()} 年")
P("\n  用户抱怨寿命的典型时长:")
for v, c in life.value_counts().head(8).items():
    P(f"    {int(v)} 个月 → {c} 条")

P("\n--- 「用久了才坏」vs「开箱就坏」(DOA) ---")
doa = R['text_l'].str.contains(r'right out of the box|out of the box|arrived broken|doa|didn.t work.*first|broken upon|first use', regex=True, na=False)
early = R['text_l'].str.contains(r'after (\d+ )?(week|month)', regex=True, na=False)
P(f"  开箱即坏(DOA): {doa.sum()} 条 ({100*doa.mean():.1f}%)  平均星 {R[doa]['rating'].mean():.2f}")
P(f"  数周/数月后坏:  {early.sum()} 条 ({100*early.mean():.1f}%)")

# ---------- Canada-specific ----------
P("\n" + "=" * 112)
P("★ 加拿大特有议题")
P("=" * 112)
CA = {
    'ALCI 安全插头/合规': r'\balci|non-compliant|compliance|csa|ul certif|recalled|recall|mandatory safety',
    '电压/欧洲旅行':      r'\bvoltage|\b220\b|europe|dual voltage|adapter',
    '关税/清关/寄送':      r'\bcustoms|duty|duties|shipping.*(slow|long)|took.*weeks to arrive',
    '魁北克/法语':        r'sèche|seche|cheveux|très|puissant|chaud|bruit|léger',
    '加价/美元换算':       r'\busd|exchange|duty|overpriced in canada|cheaper in the us',
}
for name, pat in CA.items():
    m = R['text_l'].str.contains(pat, regex=True, na=False)
    P(f"  {name:<22} {int(m.sum()):>4} 条 ({100*m.mean():>4.1f}%)")

# ---------- new article opportunities from review language ----------
P("\n" + "=" * 112)
P("★ 评论数据衍生的新选题机会（用户用自己的话提出了问题）")
P("=" * 112)
OPP = {
    '为什么吹风机有烧焦味/冒烟': r'burning smell|smell.*burn|smoke|odor',
    '吹风机能用多久/寿命':      r'how long|lasted|last.*(year|month)|lifespan',
    '吹风机坏了怎么办/保修':    r'warranty|guarantee|repair|replace.*(broke|faulty)',
    '风嘴/扩散器老是掉':        r'nozzle.*(fall|stay|loose)|diffuser.*(fall|stay)|attachment.*(fall|stay)',
    '冷风按钮不管用':          r'cold shot|cool shot|cool button|only cool air',
    '滤网能不能拆洗':          r'filter|removable|clean the',
    '吹风机太烫/烫头皮':        r'too hot|burn.*scalp|scalp.*burn|scorch',
    '旅行能不能用(电压)':       r'travel|voltage|dual voltage|220',
    '吹风机吵不吵':            r'quiet|noise|loud|silent',
    '哪款适合细软/粗硬发':      r'fine hair|thin hair|thick hair|coarse',
    '安全吗(插头/认证)':        r'\balci|safety|compliant|certif',
    '和Dyson比怎么样':         r'dyson|supersonic',
}
rows = []
for name, pat in OPP.items():
    m = R['text_l'].str.contains(pat, regex=True, na=False)
    rows.append({'潜在选题': name, '评论提及数': int(m.sum()),
                 '提及率%': round(100 * m.mean(), 1),
                 '其中差评': int((m & NEG).sum()),
                 '差评占比%': round(100 * (m & NEG).sum() / m.sum(), 0) if m.sum() else 0})
O = pd.DataFrame(rows).sort_values('评论提及数', ascending=False)
P(O.to_string(index=False))

P("\n--- 提到 Dyson 的评论：用户在拿什么对比/为什么转投 ---")
d = R[R['text_l'].str.contains(r'\bdyson', na=False)]
P(f"  提到 Dyson: {len(d)} 条 (占 {100*len(d)/len(R):.1f}%)  平均星 {d['rating'].mean():.2f}")
P(f"  其中差评占: {100*(d['rating']<=3).mean():.1f}%")
P("\n  样例:")
for _, r in d[d['rating'] <= 2].head(6).iterrows():
    P(f"   [{int(r['rating'])}★] {re.sub(chr(10),' ',str(r['text']))[:220]}")

with io.open('analysis/_rev_failure.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
F.to_pickle('analysis/rev_failure.pkl')
O.to_pickle('analysis/rev_opps.pkl')
print("written analysis/_rev_failure.txt")
