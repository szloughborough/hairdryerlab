"""Extract product main-image URLs + key facts from the BSR export for the 5 recommended products."""
import zipfile, re, io
import pandas as pd

BSR = r"C:\Users\Mloong\Downloads\BSR(Hair-Dryers(Current))-50-CA-20261002.xlsx"
z = zipfile.ZipFile(BSR)
S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)).replace('&amp;', '&').replace('&apos;', "'")
     for s in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8'), re.S)]
df = pd.read_excel(BSR, sheet_name='CA', header=0); df.columns = S[:71]

WANT = ['B0GWHF4SHD', 'B0FPMBBG2J', 'B0F8QH8XHV', 'B0C3M9WBQF', 'B09JZ18GLJ']
out = []
out.append("ASIN        | 品牌      | 价格    | 评分 | 评分数 | 主图URL")
out.append("-" * 140)
for a in WANT:
    r = df[df['ASIN'] == a]
    if len(r) == 0:
        out.append(f"{a}  NOT FOUND"); continue
    r = r.iloc[0]
    out.append(f"{a} | {r['品牌']:<9} | {r['价格(C$)']:<7} | {r['评分']:<4} | "
               f"{int(r['评分数']):<6} | {r['商品主图']}")

# also dump all image urls to a json-ready list
imgs = df[df['ASIN'].isin(WANT)][['ASIN', '品牌', '商品主图', '商品标题']]
out.append("")
out.append("=== 完整标题（用于 alt 文本参考）===")
for _, r in imgs.iterrows():
    out.append(f"{r['ASIN']} | {str(r['商品标题'])[:120]}")

io.open('analysis/_images.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_images.txt')
