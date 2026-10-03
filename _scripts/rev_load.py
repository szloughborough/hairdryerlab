"""
Amazon.ca hair dryer review analysis.
Decode headers from sharedStrings, load all ASIN review files,
extract consumer concerns/themes to guide article layout.
"""
import glob, os, re, io, zipfile
import pandas as pd, numpy as np

SRC = 'asin数据'
files = sorted(glob.glob(os.path.join(SRC, '*-CA-Reviews-*.xlsx')))
print(f"review files: {len(files)}")

# ---------- decode header names ----------
hdr = None
with zipfile.ZipFile(files[0]) as z:
    raw = z.read('xl/sharedStrings.xml').decode('utf-8')
    S = [''.join(re.findall(r'<t[^>]*>(.*?)</t>', s, re.S)).replace('&amp;', '&').replace('&apos;', "'")
         for s in re.findall(r'<si>(.*?)</si>', raw, re.S)]
    # first 19 shared strings are the header
    hdr = S[:19]
print("\n=== 评论表头 (19列) ===")
for i, h in enumerate(hdr, 1):
    print(f"  {i:>2} | {h}")

# ---------- load all ----------
parts = []
for f in files:
    base = os.path.basename(f)
    if '(1)' in base:      # duplicate export
        continue
    df = pd.read_excel(f, sheet_name=0)
    if df.shape[1] == 19:
        df.columns = hdr
    df['_file'] = base
    parts.append(df)

R = pd.concat(parts, ignore_index=True)
print(f"\ncombined reviews: {len(R):,}")

# normalise column names to ASCII-ish
CN = {
    hdr[0]: 'ASIN', hdr[1]: 'title', hdr[2]: 'body', hdr[3]: 'VP',
    hdr[4]: 'Vine', hdr[5]: 'variant', hdr[6]: 'rating', hdr[7]: 'helpful',
    hdr[8]: 'n_images', hdr[9]: 'img_url', hdr[10]: 'has_video', hdr[11]: 'video_url',
    hdr[12]: 'review_url', hdr[13]: 'reviewer', hdr[14]: 'avatar', hdr[15]: 'country',
    hdr[16]: 'profile', hdr[17]: 'vine_prog', hdr[18]: 'date',
}
R = R.rename(columns=CN)
R['rating'] = pd.to_numeric(R['rating'], errors='coerce')
R['body'] = R['body'].fillna('').astype(str)
R['title'] = R['title'].fillna('').astype(str)
R['text'] = (R['title'] + ' . ' + R['body']).str.replace(r'\s+', ' ', regex=True).str.strip()
R['date'] = pd.to_datetime(R['date'], errors='coerce')

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P("=" * 110)
P("Amazon.ca 吹风机评论总览")
P("=" * 110)
P(f"评论文件: {len(files)} 个 ASIN | 评论总数: {len(R):,}")
P(f"ASIN 数: {R['ASIN'].nunique()} | 时间跨度: {R['date'].min()} ~ {R['date'].max()}")
P(f"已验证购买(VP)占比: {(R['VP']=='Y').mean()*100:.1f}%")
P(f"含图片评论: {R['n_images'].notna().sum():,} | 含视频: {(R['has_video']=='Y').sum():,}")

P("\n--- 星级分布 ---")
vc = R['rating'].value_counts().sort_index()
for s, n in vc.items():
    P(f"  {int(s)}星: {n:>5,}  ({100*n/len(R):>5.1f}%)  {'#'*int(60*n/len(R))}")
P(f"\n平均星级: {R['rating'].mean():.3f}")
P(f"差评率(1-2星): {100*(R['rating']<=2).mean():.1f}%  好评率(4-5星): {100*(R['rating']>=4).mean():.1f}%")

P("\n--- 按 ASIN 汇总 (评论数最多的15个) ---")
g = R.groupby('ASIN').agg(评论数=('rating', 'size'), 平均星=('rating', 'mean'),
                          差评率=('rating', lambda s: round(100*(s<=2).mean(), 1)),
                          好评率=('rating', lambda s: round(100*(s>=4).mean(), 1)))
P(g.sort_values('评论数', ascending=False).head(15).to_string())

with io.open('analysis/_rev_overview.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("\nwritten analysis/_rev_overview.txt")
R.to_pickle('analysis/reviews.pkl')
