import zipfile, re, io
import pandas as pd, numpy as np

F = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"

# ---- decode sharedStrings to real header names
z = zipfile.ZipFile(F)
raw = z.read('xl/sharedStrings.xml').decode('utf-8')
strs = re.findall(r'<si>(.*?)</si>', raw, re.S)
S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S))
     .replace('&amp;', '&').replace('&apos;', "'") for s in strs]
HDR = S[:71]

# ---- read sheet data by index (avoid mangled headers)
df = pd.read_excel(F, sheet_name='CA', header=0)
df.columns = HDR

num = ['月销量', '月销售额(C$)', '价格(C$)', '评分数', '月新增评分数', '评分',
       '留评率', '大类BSR', '小类BSR', '变体数', '上架天数', 'Q&A数']
for c in num:
    df[c] = pd.to_numeric(df[c], errors='coerce')

out = []
def P(*a):
    out.append(' '.join(str(x) for x in a))

P("=" * 100)
P("Amazon.ca 吹风机类目 BSR Top50  (SellerSprite 导出, 2026-10-02)")
P("=" * 100)
P(f"产品数: {len(df)}   列数: {len(df.columns)}")
P(f"\n类目合计 月销量: {df['月销量'].sum():,.0f} 台")
P(f"类目合计 月销售额: C${df['月销售额(C$)'].sum():,.0f}")
P(f"类目均价 (加权): C${(df['月销售额(C$)'].sum()/df['月销量'].sum()):.2f}")
P(f"价格区间: C${df['价格(C$)'].min():.2f} - C${df['价格(C$)'].max():.2f}  中位 C${df['价格(C$)'].median():.2f}")

# ---- find Laifen
la = df[df['品牌'].astype(str).str.contains('laifen', case=False, na=False) |
        df['商品标题'].astype(str).str.contains('laifen', case=False, na=False)]
P("\n" + "=" * 100)
P("★★★ LAIFEN 在 Amazon.ca 的实际表现 ★★★")
P("=" * 100)
P(f"Laifen ASIN 数: {len(la)}")
cols = ['ASIN', '品牌', '商品标题', '小类BSR', '月销量', '月销量增长率', '月销售额(C$)',
        '价格(C$)', '评分数', '月新增评分数', '评分', '变体数', '上架天数', '卖家数', 'Buybox卖家']
P(la[cols].to_string(index=False))

P("\n--- Laifen 品牌维度汇总 (Brands 表口径) ---")
try:
    bd = pd.read_excel(F, sheet_name='Brands')
    bd.columns = [S[i] for i in range(bd.shape[1])]
    for c in bd.columns[1:]:
        bd[c] = pd.to_numeric(bd[c], errors='coerce')
    P(bd.to_string(index=False))
except Exception as e:
    P("Brands read err:", e)

P("\n--- Sellers 表 ---")
try:
    sd = pd.read_excel(F, sheet_name='Sellers')
    sd.columns = [S[i] for i in range(sd.shape[1])]
    for c in sd.columns[1:]:
        sd[c] = pd.to_numeric(sd[c], errors='coerce')
    P(sd.to_string(index=False))
except Exception as e:
    P("Sellers read err:", e)

# ---- full top 50
P("\n" + "=" * 100)
P("Top 50 全表 (按小类BSR)")
P("=" * 100)
show = ['小类BSR', '品牌', 'ASIN', '月销量', '月销售额(C$)', '价格(C$)', '评分数', '评分',
        '月新增评分数', '上架天数', '变体数', '卖家数']
show = [c for c in show if c in df.columns]
P(df.sort_values('小类BSR')[show].to_string(index=False))

# ---- brand aggregation
P("\n" + "=" * 100)
P("品牌集中度 (Top50 内, 按月销量)")
P("=" * 100)
bg = df.groupby('品牌').agg(ASIN数=('ASIN', 'size'), 月销量=('月销量', 'sum'),
                            月销售额=('月销售额(C$)', 'sum'),
                            均价=('价格(C$)', 'mean')).sort_values('月销量', ascending=False)
bg['销量占比%'] = (100 * bg['月销量'] / df['月销量'].sum()).round(1)
P(bg.to_string())

# ---- price band analysis
P("\n" + "=" * 100)
P("价格带分析 (Top50)")
P("=" * 100)
df['价格带'] = pd.cut(df['价格(C$)'], [0, 30, 50, 80, 120, 200, 1000],
                     labels=['<$30', '$30-50', '$50-80', '$80-120', '$120-200', '$200+'])
pb = df.groupby('价格带', observed=True).agg(ASIN数=('ASIN', 'size'), 月销量=('月销量', 'sum'),
                                              月销售额=('月销售额(C$)', 'sum')).sort_index()
pb['销量占比%'] = (100 * pb['月销量'] / df['月销量'].sum()).round(1)
pb['销售额占比%'] = (100 * pb['月销售额'] / df['月销售额(C$)'].sum()).round(1)
P(pb.to_string())

with io.open('analysis/_bsr_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("written analysis/_bsr_report.txt")
