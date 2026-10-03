import io, zipfile, re
import pandas as pd

BSR = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
z = zipfile.ZipFile(BSR)
S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)).replace('&amp;', '&').replace('&apos;', "'")
     for s in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8'), re.S)]
df = pd.read_excel(BSR, sheet_name='CA', header=0); df.columns = S[:71]
for c in ['月销量', '月销售额(C$)', '价格(C$)', '卖家数']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P("=" * 104)
P("Buy Box 与卖家结构 —— 三个自定义佣金品牌")
P("=" * 104)
t = df[df['品牌'].isin(['Laifen', 'slopehill', 'dreame'])].copy()
t = t[['品牌', 'ASIN', '月销量', '价格(C$)', '卖家数', 'Buybox卖家', '卖家所属地', '配送方式', 'LQS']]
t = t.sort_values(['品牌', '月销量'], ascending=[True, False])
P(t.to_string(index=False))

P("\n" + "=" * 104)
P("⚠ 风险检查：Buy Box 是否由品牌自己掌控？")
P("=" * 104)
for b in ['Laifen', 'slopehill', 'dreame']:
    s = df[df['品牌'] == b]
    P(f"\n--- {b} ---")
    for _, r in s.iterrows():
        own = '自身' if b.lower() in str(r['Buybox卖家']).lower() else '第三方'
        P(f"   {r['ASIN']}  卖家数={r['卖家数']:.0f}  BuyBox={r['Buybox卖家']}  [{own}]  "
          f"发货地={r['卖家所属地']}  配送={r['配送方式']}  月销={r['月销量']:.0f}")

P("\n" + "=" * 104)
P("结论")
P("=" * 104)
sl = df[df['品牌'] == 'slopehill']
P(f"slopehill {len(sl)} 个 ASIN 中，Buy Box 归属：")
P("  " + str(sl['Buybox卖家'].value_counts().to_dict()))
P(f"  卖家数分布: {sl['卖家数'].value_counts().sort_index().to_dict()}")
P(f"  发货地: {sl['卖家所属地'].value_counts().to_dict()}")
P("")
P("→ slopehill 全部 ASIN 的 Buy Box 由 Stellartech 掌控（第三方卖家，非品牌方）。")
P("  这意味着：slopehill 的 20% 佣金必须是「卖家直连」协议，"
  "而 Amazon Associates 站内链接只能拿类目标准 4%。")
P("  同时 3 个 ASIN 都有 2-5 个跟卖，存在 Buy Box 易主导致佣金流失的风险。")

with io.open('analysis/_buybox.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("written")
