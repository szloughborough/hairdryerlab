"""
Consumer concern / pain-point mining from Amazon.ca hair dryer reviews.
Outputs theme frequencies + sentiment split + representative quotes,
then maps them to article section structure.
"""
import re, io, glob, os, zipfile
import pandas as pd, numpy as np

R = pd.read_pickle('analysis/reviews.pkl')
R['rating'] = pd.to_numeric(R['rating'], errors='coerce')
R = R.dropna(subset=['rating'])
R['text_l'] = R['text'].str.lower()

# ---- attach brand / price from BSR
BSR = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
try:
    z = zipfile.ZipFile(BSR)
    S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)).replace('&amp;', '&').replace('&apos;', "'")
         for s in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8'), re.S)]
    b = pd.read_excel(BSR, sheet_name='CA', header=0); b.columns = S[:71]
    b = b[['ASIN', '品牌', '价格(C$)']].rename(columns={'品牌': 'brand', '价格(C$)': 'price'})
    b['price'] = pd.to_numeric(b['price'], errors='coerce')
except Exception as e:
    print("BSR join failed:", e); b = pd.DataFrame(columns=['ASIN', 'brand', 'price'])

R = R.merge(b, on='ASIN', how='left')
R['brand'] = R['brand'].fillna('(未在Top50)')

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

NEG = R['rating'] <= 3      # 1-3星 = 不满/有保留
POS = R['rating'] >= 4

# ================================================================
THEMES = {
    '噪音 Noise':            r'\bnois|\bloud|too loud|quiet|silent|silenc|humming|whine|hearing|deafening',
    '重量 Weight':           r'\bheavy|heavier|weight|lightweight|light weight|light-?weight|bulky|weighs|too heavy',
    '温度/过热 Heat':        r'\btoo hot|overheat|over heat|burn|scorch|melt|heat setting|temperature|hot air|scald|heat control|gets hot',
    '风力/干发速度 Power':    r'\bpowerful|not powerful|weak|strong|fast dry|dries fast|drying time|takes forever|slow to dry|airflow|air flow|blows',
    '耐用性/故障 Durability': r'\bbroke|broken|stopped working|stop working|stopped after|died|dead|quit working|no longer works|lasted|durab|fell apart|defect',
    '性价比 Value':          r'\bworth it|not worth|overpriced|expensive|good value|great value|cheap price|price|money well|bang for|affordable|cost',
    '配件/风嘴 Attachments':  r'\bdiffus|nozzle|concentrator|attach|comb attachment|accessor',
    '电源线 Cord':           r'\bcord|power cord|wire length|cable|swivel cord|short cord|cordless',
    '电压/旅行 Voltage':      r'\bvoltage|\bvolt|\b220\b|\b110\b|dual voltage|travel|adapter|plug|europe|overseas',
    '操作/握持 Usability':    r'\bbutton|setting|hard to use|easy to use|ergonomic|comfortable to hold|handle|grip|cumbersome|confusing|dial|switch',
    '客服/保修 Service':      r'\bcustomer service|warranty|guarantee|return|refund|replaced|customer support|contacted',
    '护发效果 Results':       r'\bfrizz|shiny|shine|smooth|silky|volume|curl|straight|damage|healthy|soft|salon-?quality|glossy',
    '异味/烧焦味 Smell':      r'\bburning smell|burning|smell|odor|smells like|plastic smell|smoke',
    '尺寸/收纳 Size':         r'\bcompact|small|large|big|storage|storage bag|fold|foldable|fits in|portable|size',
    '做工/材质 Build':        r'\bplastic|flimsy|cheaply made|sturdy|well made|well-?built|build quality|feels cheap|solid',
    '离子/技术 Tech':         r'\bionic|ceramic|tourmaline|infrared|negative ion|nano|brushless|high-?speed|digital motor',
    '冷风 Cold Shot':         r'\bcold shot|cool shot|cool air|cool button|cold air',
    '滤网/清洁 Filter':       r'\bfilter|lint|clean the|cleaning|dust|clog',
    '安全/自动断电 Safety':    r'\bauto.?shut|shut off|safety|overheat protection|fuse|circuit|breaker|sparks',
    '发质 Fine/Thick':        r'\bfine hair|thin hair|thick hair|coarse|my hair type|curly hair|wavy hair',
    '礼物 Gift':              r'\bgift|present for|bought (it )?for my (wife|daughter|mom|mother|girlfriend|husband)',
    '专业/沙龙 Salon':         r'\bsalon|professional use|stylist|barber|at work',
}

rows = []
for name, pat in THEMES.items():
    m = R['text_l'].str.contains(pat, regex=True, na=False)
    n_all = int(m.sum())
    n_neg = int((m & NEG).sum())
    n_pos = int((m & POS).sum())
    rows.append({'主题': name, '提及总数': n_all,
                 '提及率%': round(100 * n_all / len(R), 1),
                 '差评(1-3星)提及': n_neg, '好评(4-5星)提及': n_pos,
                 '负面占比%': round(100 * n_neg / n_all, 1) if n_all else 0,
                 '净情绪(好-差)': n_pos - n_neg})
T = pd.DataFrame(rows).sort_values('提及总数', ascending=False)

P("=" * 118)
P("消费者关注点主题榜（全量 8,261 条评论）")
P("=" * 118)
P('"负面占比%"高 = 该主题是用户的槽点/痛点；低 = 用户普遍满意')
P("")
P(f"{'主题':<26}{'提及数':>7}{'提及率':>7}{'差评提及':>9}{'好评提及':>9}{'负面占比':>9}{'净情绪':>8}")
P("-" * 118)
for _, r in T.iterrows():
    bar = '#' * int(r['负面占比%'] / 2)
    P(f"{r['主题']:<26}{r['提及总数']:>7,}{r['提及率%']:>6.1f}%{r['差评(1-3星)提及']:>9,}"
      f"{r['好评(4-5星)提及']:>9,}{r['负面占比%']:>8.1f}%{r['净情绪(好-差)']:>8,}  {bar}")

P("\n" + "=" * 118)
P("★ 痛点排序（按差评提及数）—— 这些就是文章必须回答的问题")
P("=" * 118)
PAIN = T.sort_values('差评(1-3星)提及', ascending=False)
for i, (_, r) in enumerate(PAIN.head(14).iterrows(), 1):
    P(f"{i:>2}. {r['主题']:<26} 差评提及 {r['差评(1-3星)提及']:>4,} 条  (负面占比 {r['负面占比%']:.0f}%)")

P("\n" + "=" * 118)
P("★ 满意点排序（按净情绪）—— 这些是卖点，要写进推荐理由")
P("=" * 118)
SAT = T.sort_values('净情绪(好-差)', ascending=False)
for i, (_, r) in enumerate(SAT.head(10).iterrows(), 1):
    P(f"{i:>2}. {r['主题']:<26} 净情绪 {r['净情绪(好-差)']:>+5,}  (好评 {r['好评(4-5星)提及']:,} / 差评 {r['差评(1-3星)提及']:,})")

with io.open('analysis/_rev_themes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
T.to_pickle('analysis/rev_themes.pkl')
print("\nwritten analysis/_rev_themes.txt")
