"""
检查商品图的背景是否为纯白 —— 决定能否用 mix-blend-mode: multiply 去掉白底。

若能：产品会直接「浮」在冰蓝背景上，像一次静物拍摄；
      否则只能用白色卡片托底，看起来就是个商品网格。

同时报告四角与边缘的像素值，因为有些 Amazon 图不是纯白（带极浅灰或渐变）。
"""
import io
import urllib.request

from PIL import Image

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

URLS = [
    ('Slopehill 1902', 'https://m.media-amazon.com/images/I/41v5yqhOsNL._AC_US600_.jpg'),
    ('Laifen Air', 'https://m.media-amazon.com/images/I/31Nr35JXX7L._AC_US600_.jpg'),
    ('Dreame Pocket Pro', 'https://m.media-amazon.com/images/I/41TFuIwjFiL._AC_US600_.jpg'),
]

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W(f'{"图片":<20}{"尺寸":<14}{"四角像素 (RGB)":<40}{"是否纯白"}')
W('-' * 92)

all_white = True
for name, url in URLS:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    data = urllib.request.urlopen(req, timeout=30).read()
    im = Image.open(io.BytesIO(data)).convert('RGB')
    w, h = im.size
    corners = [
        im.getpixel((0, 0)),
        im.getpixel((w - 1, 0)),
        im.getpixel((0, h - 1)),
        im.getpixel((w - 1, h - 1)),
    ]
    # 边缘中点也看一下
    edges = [
        im.getpixel((w // 2, 0)),
        im.getpixel((w // 2, h - 1)),
        im.getpixel((0, h // 2)),
        im.getpixel((w - 1, h // 2)),
    ]
    white = all(c == (255, 255, 255) for c in corners + edges)
    if not white:
        all_white = False
    W(f'{name:<20}{f"{w}x{h}":<14}{str(corners[0]) + " " + str(corners[1]):<40}{"是" if white else "否"}')
    W(f'{"":<20}边中点: {edges}')
    W('')

W('=' * 92)
if all_white:
    W('结论: 全部为纯白背景 —— 可以用 mix-blend-mode: multiply 去掉白底')
    W('      产品会直接呈现在冰蓝背景上，无需白色卡片托底')
else:
    W('结论: 存在非纯白背景 —— multiply 会留下可见色块')
    W('      应保留白色卡片托底，或先用 Pillow 处理成透明 PNG')
W('=' * 92)

io.open('analysis/_image_bg_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
