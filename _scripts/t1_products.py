"""从 BSR 导出提取这 5 篇文章会用到的全部产品数据，生成 products.ts。"""
import zipfile, re, io
import pandas as pd

BSR = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
z = zipfile.ZipFile(BSR)
S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)).replace('&amp;', '&').replace('&apos;', "'")
     for s in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8'), re.S)]
df = pd.read_excel(BSR, sheet_name='CA', header=0); df.columns = S[:71]
for c in ['价格(C$)', '评分', '评分数', '月销量', '小类BSR', '上架天数', '卖家数', '月销量增长率']:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# 需要的 ASIN（按品牌分组）
WANT = {
    'Laifen':  ['B0GWHF4SHD', 'B0FKBFZNHK', 'B0GWHGTBDY', 'B0FPMBBG2J', 'B0D141Q8ZF', 'B0D13MYLJC'],
    'Dyson':   ['B0GHZMFY9W', 'B0FHJFTZ57'],
    'Shark':   ['B0DFDQ3THF'],
    'dreame':  ['B0F8QH8XHV'],
    'slopehill': ['B0C3M9WBQF', 'B08HRQG2M6', 'B0CY4QMMBH'],
    'wavytalk': ['B09JZ18GLJ'],
    'Conair':  ['B0852913V2', 'B0CFQ3R4CQ', 'B0B15P7SDS'],
    'REVLON':  ['B07NF1CLMQ'],
    'Aina':    ['B0DMWNFZRH'],
    'Remington': ['B0BN2F767S', 'B08DLGCKGK'],
}

log = []
def P(*a): log.append(' '.join(str(x) for x in a))

P('=' * 130)
P('产品数据提取（来源：SellerSprite BSR 导出，Amazon.ca，2026-10-02）')
P('=' * 130)
P(f"{'ASIN':<12}{'品牌':<11}{'价格':>8}{'评分':>6}{'评分数':>9}{'月销量':>8}{'BSR':>6}{'天数':>6}{'卖家':>5}{'增长':>8}")
P('-' * 130)

rows = []
for brand, asins in WANT.items():
    for a in asins:
        r = df[df['ASIN'] == a]
        if len(r) == 0:
            P(f"{a:<12}{brand:<11}  ** 不在 Top50 中 **"); continue
        r = r.iloc[0]
        g = r['月销量增长率']
        rows.append({
            'asin': a, 'brand': brand, 'title': str(r['商品标题']),
            'price': float(r['价格(C$)']), 'rating': float(r['评分']),
            'ratings': int(r['评分数']), 'units': int(r['月销量']) if pd.notna(r['月销量']) else 0,
            'bsr': int(r['小类BSR']) if pd.notna(r['小类BSR']) else None,
            'days': int(r['上架天数']) if pd.notna(r['上架天数']) else None,
            'sellers': int(r['卖家数']) if pd.notna(r['卖家数']) else None,
            'growth': float(g) if pd.notna(g) else None,
            'buybox': str(r['Buybox卖家']), 'image': str(r['商品主图']),
        })
        P(f"{a:<12}{brand:<11}{r['价格(C$)']:>8.2f}{r['评分']:>6.1f}{r['评分数']:>9,.0f}"
          f"{(r['月销量'] if pd.notna(r['月销量']) else 0):>8,.0f}"
          f"{(r['小类BSR'] if pd.notna(r['小类BSR']) else 0):>6,.0f}"
          f"{(r['上架天数'] if pd.notna(r['上架天数']) else 0):>6,.0f}"
          f"{(r['卖家数'] if pd.notna(r['卖家数']) else 0):>5,.0f}"
          f"{(g if pd.notna(g) else 0):>8.2f}")

P('')
P('--- 主图 URL ---')
for r in rows:
    P(f"{r['asin']}  {r['image']}")

io.open('analysis/_t1_products.txt', 'w', encoding='utf-8').write('\n'.join(log))
pd.DataFrame(rows).to_pickle('analysis/t1_products.pkl')
print('written analysis/_t1_products.txt')
