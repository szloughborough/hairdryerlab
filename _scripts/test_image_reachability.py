"""
测试首页 5 张 Amazon 商品图的真实可达性。

同时测两种情况，因为 Amazon CDN 可能按 Referer 拒绝：
  A. 不带 Referer（直接请求）
  B. 带 Referer: https://hairdryerlab.ca/（模拟浏览器从本站引用）

这一步很重要：如果 Amazon 拒绝外链，那修好标记也仍然是白图，
需要改为下载后自托管。
"""
import io
import re
import urllib.error
import urllib.request

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

h = io.open('site/dist/index.html', encoding='utf-8').read()
urls = [u for u in re.findall(r'<img[^>]*src="(https?://[^"]+)"', h)]
# 去重
seen, uniq = set(), []
for u in urls:
    if u not in seen:
        seen.add(u)
        uniq.append(u)

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W(f'待测图片: {len(uniq)} 张')
W('')

def probe(url, referer=None):
    headers = {'User-Agent': UA, 'Accept': 'image/avif,image/webp,image/*,*/*;q=0.8'}
    if referer:
        headers['Referer'] = referer
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
            return ('OK', r.status, len(data), r.headers.get('Content-Type', ''))
    except urllib.error.HTTPError as e:
        return (f'HTTP {e.code}', e.code, 0, e.reason or '')
    except Exception as e:
        return ('ERR', 0, 0, type(e).__name__)

W('=' * 96)
W(f'{"图片":<48}{"无 Referer":<20}{"带本站 Referer"}')
W('=' * 96)
allok = True
for u in uniq:
    a = probe(u)
    b = probe(u, 'https://hairdryerlab.ca/')
    name = u.split('/')[-1][:46]
    W(f'{name:<48}{a[0] + f" {a[2]:,}B":<20}{b[0] + f" {b[2]:,}B"}')
    if a[0] != 'OK' or b[0] != 'OK':
        allok = False
        W(f'    -> A: {a[3]}')
        W(f'    -> B: {b[3]}')

W('')
W('=' * 96)
if allok:
    W('结论: 全部可达，且带本站 Referer 也不被拒 —— 图片应能正常显示')
else:
    W('结论: 有图片不可达或被 Referer 拒绝 —— 需要改为下载后自托管')
W('=' * 96)

io.open('analysis/_image_reachability.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_image_reachability.txt')
