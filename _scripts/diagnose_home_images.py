"""诊断首页图片：提取所有 <img>，逐个测试可达性，找失败规律。"""
import io
import re
import urllib.error
import urllib.request
from collections import Counter

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

html = io.open('site/dist/index.html', encoding='utf-8').read()
imgs = re.findall(r'<img[^>]*>', html)

W('=' * 96)
W(f'首页 <img> 数量: {len(imgs)}')
W('=' * 96)

rows = []
for tag in imgs:
    src = re.search(r'src="([^"]+)"', tag)
    alt = re.search(r'alt="([^"]*)"', tag)
    if not src:
        continue
    rows.append((src.group(1), alt.group(1) if alt else ''))

hosts = Counter(re.match(r'https?://([^/]+)', u).group(1) for u, _ in rows if u.startswith('http'))
W('')
W('按域名:')
for h, n in hosts.most_common():
    W(f'   {h:<40} {n}')

W('')
W('=' * 96)
W('逐个测试可达性')
W('=' * 96)

results = []
for url, alt in rows:
    if not url.startswith('http'):
        results.append((url, 'LOCAL', '-', alt))
        continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            size = len(r.read())
            results.append((url, r.status, f'{size:,}B', alt))
    except urllib.error.HTTPError as e:
        results.append((url, f'HTTP {e.code}', e.reason or '', alt))
    except Exception as e:
        results.append((url, 'ERR', type(e).__name__, alt))

ok = [r for r in results if r[1] == 200]
bad = [r for r in results if r[1] != 200]

W(f'  可达: {len(ok)}   失败: {len(bad)}')
W('')
if bad:
    W('失败明细:')
    for url, status, note, alt in bad:
        W(f'   [{status}] {note}')
        W(f'      {url[:110]}')
        W(f'      alt: {alt[:70]}')
        W('')
else:
    W('全部可达 —— 说明问题不在 URL 本身')

W('')
W('=== 成功样本（前 5 个）===')
for url, status, size, alt in ok[:5]:
    W(f'   [{status}] {size}  {url[:100]}')

io.open('analysis/_homepage_images.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out[-40:]))
