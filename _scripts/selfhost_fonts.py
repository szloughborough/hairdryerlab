"""
把 Google Fonts 改为自托管。

原因：从 fonts.googleapis.com 加载字体，会让 Google 在每次页面加载时收到
访客的 IP 与 User-Agent。这有两个问题：
  1. 隐私政策未披露该第三方请求（政策只列了「三样东西」）
  2. 部分司法辖区（如德国）已判定 Google Fonts 远程加载违反数据保护法

自托管同时消除该请求并改善性能（少一个 DNS + TLS 握手，缓存更久）。

只保留 latin / latin-ext 子集 —— 本站为 en-CA，法语（§67）也用这两个子集。
"""
import io
import os
import re
import urllib.request

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')
CSS_URL = ('https://fonts.googleapis.com/css2?'
           'family=Manrope:wght@600;700;800&family=Inter:wght@400;500;600&display=swap')
KEEP_SUBSETS = {'latin', 'latin-ext'}
OUT_DIR = 'site/public/fonts'

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

req = urllib.request.Request(CSS_URL, headers={'User-Agent': UA})
css = urllib.request.urlopen(req, timeout=40).read().decode('utf-8')
W(f'取回 CSS {len(css):,} 字节')

# 每个 @font-face 前有一个 /* subset */ 注释
blocks = re.findall(r'/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)
W(f'共 {len(blocks)} 个 @font-face 块')

os.makedirs(OUT_DIR, exist_ok=True)
kept = []
for subset, block in blocks:
    if subset not in KEEP_SUBSETS:
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
    wt = re.search(r'font-weight:\s*(\d+)', block).group(1)
    url = re.search(r'url\((https://[^)]+\.woff2)\)', block).group(1)
    urange = re.search(r'unicode-range:\s*([^;]+);', block)
    style = re.search(r'font-style:\s*(\w+)', block)

    fname = f'{fam.lower().replace(" ", "-")}-{wt}-{subset}.woff2'
    dest = os.path.join(OUT_DIR, fname)
    data = urllib.request.urlopen(
        urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40).read()
    io.open(dest, 'wb').write(data)
    kept.append((fam, wt, style.group(1) if style else 'normal',
                 subset, fname, len(data), urange.group(1).strip() if urange else ''))

W(f'下载 {len(kept)} 个 woff2 到 {OUT_DIR}')
W('')
for fam, wt, st, sub, fname, size, _ in kept:
    W(f'   {fam:<10} {wt:<4} {sub:<10} {size:>7,} B   {fname}')

# 生成自托管 CSS
lines = ['/* ---------------------------------------------------------------',
         '   自托管字体 —— 由 _scripts/selfhost_fonts.py 生成，请勿手改。',
         '',
         '   为什么不用 Google Fonts CDN：远程加载会让 Google 在每次页面加载时',
         '   收到访客 IP 与 User-Agent，而隐私政策未披露该请求。自托管同时',
         '   少一个 DNS + TLS 握手，缓存策略也更可控。',
         '',
         '   子集：latin + latin-ext（en-CA；法语同样使用这两个子集，见 §67）',
         '   --------------------------------------------------------------- */',
         '']
for fam, wt, st, sub, fname, _, urange in kept:
    lines.append('@font-face {')
    lines.append(f"  font-family: '{fam}';")
    lines.append(f'  font-style: {st};')
    lines.append(f'  font-weight: {wt};')
    lines.append('  font-display: swap;')
    lines.append(f'  src: url(/fonts/{fname}) format("woff2");')
    if urange:
        lines.append(f'  unicode-range: {urange};')
    lines.append('}')
    lines.append('')

css_path = 'site/src/styles/fonts.css'
io.open(css_path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
W('')
W(f'生成 {css_path}（{len(lines)} 行）')

io.open('analysis/_selfhost_fonts.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(f'downloaded {len(kept)} font files')
print('written analysis/_selfhost_fonts.txt')
