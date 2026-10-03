"""Extract literal questions from reviews -> FAQ material."""
import re, io
import pandas as pd, numpy as np

R = pd.read_pickle('analysis/reviews.pkl')
R['rating'] = pd.to_numeric(R['rating'], errors='coerce')
R = R.dropna(subset=['rating']).copy()

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

# split into sentences, keep question-form ones
sents = []
for _, r in R.iterrows():
    t = re.sub(r'\s+', ' ', str(r['text']))
    for s in re.split(r'(?<=[.!?])\s+', t):
        s = s.strip()
        if 15 <= len(s) <= 220 and s.endswith('?'):
            sents.append((s, int(r['rating']), int(r['helpful']) if pd.notna(r['helpful']) else 0))
Q = pd.DataFrame(sents, columns=['question', 'rating', 'helpful']).drop_duplicates('question')
P("=" * 112)
P(f"评论中的字面提问（用户自己问的问题）—— 共 {len(Q)} 条")
P("=" * 112)
P(f"其中来自差评(1-3星): {(Q['rating']<=3).sum()} 条 ({100*(Q['rating']<=3).mean():.0f}%)")
P("\n--- 按有用数排序的 top 40 ---")
for _, r in Q.sort_values('helpful', ascending=False).head(40).iterrows():
    P(f"  [{r['rating']}★] {r['question'][:180]}")

# topic buckets of questions
P("\n" + "=" * 112)
P("提问主题归类（用于设计 FAQ 结构）")
P("=" * 112)
BUCKETS = {
    '耐用性/寿命': r'\blast|long|durab|break|broke|reliable|how many years|worth.*(money|buy)',
    '温度/安全':   r'\bhot|heat|burn|safe|fire|smoke|melt|scalp',
    '噪音':       r'\bnois|quiet|loud|silent',
    '重量/便携':   r'\bheavy|weight|light|portable|travel|compact|fold',
    '电压/旅行':   r'\bvoltage|\bvolt|220|europe|travel|adapter|convert',
    '配件':       r'\bdiffus|nozzle|attach|comb|concentrator',
    '护发/发质':   r'\bfrizz|curl|fine hair|thick hair|damage|shiny|straight',
    '功率/速度':   r'\bpower|fast|watt|speed|dry.*(time|fast)|airflow',
    '价格/性价比': r'\bprice|cost|worth|cheap|expensive|value|deal|sale',
    '保修/售后':   r'\bwarrant|guarantee|return|refund|repair|customer',
    'Dyson对比':  r'\bdyson|supersonic',
    '滤网/清洁':   r'\bfilter|clean|maintenance',
}
for name, pat in BUCKETS.items():
    s = Q[Q['question'].str.lower().str.contains(pat, regex=True, na=False)]
    P(f"  {name:<14} {len(s):>4} 条")
    for q, rt in s.sort_values('helpful', ascending=False).head(3)[['question', 'rating']].values:
        P(f"       [{rt}★] {q[:150]}")

with io.open('analysis/_rev_questions.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
Q.to_pickle('analysis/rev_questions.pkl')
print("written analysis/_rev_questions.txt")
