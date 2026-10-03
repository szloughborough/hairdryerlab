"""全站扫描：找出「媒体区有 CSS 支持、标记里却没渲染 <img>」的同类问题。"""
import io
import os
import re

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

# 找所有带 -media / media 类的容器，看其内部是否含 <img>
MEDIA_RE = re.compile(r'<div class="([^"]*\bmedia\b[^"]*)"[^>]*>(.*?)</div>', re.S)

W('=' * 92)
W('检查所有 site/src 下的 .astro 与 .tsx 组件/页面')
W('=' * 92)

issues = []
checked = 0
for root in ('site/src/components', 'site/src/pages', 'site/src/layouts'):
    if not os.path.isdir(root):
        continue
    for f in sorted(os.listdir(root)):
        if not f.endswith(('.astro', '.tsx', '.ts')):
            continue
        p = os.path.join(root, f)
        t = io.open(p, encoding='utf-8').read()
        checked += 1
        for m in MEDIA_RE.finditer(t):
            cls, inner = m.group(1), m.group(2)
            has_img = '<img' in inner
            if not has_img:
                # 排除刻意为之的占位（含 muted 文字 + 条件渲染的 img 分支）
                issues.append((p, cls, re.sub(r'\s+', ' ', inner.strip())[:100]))

W(f'  扫描文件数: {checked}')
W('')
if issues:
    W(f'发现 {len(issues)} 处媒体区没有 <img>：')
    for p, cls, inner in issues:
        W(f'   {p}')
        W(f'      class="{cls}"')
        W(f'      内容: {inner}')
        W('')
else:
    W('  没有发现问题 ✓')

W('')
W('=' * 92)
W('确认首页已修复')
W('=' * 92)
idx = io.open('site/src/pages/index.astro', encoding='utf-8').read()
n = len(re.findall(r'PRODUCT_IMAGES\[m\.asin\]', idx))
W(f'  index.astro 中 PRODUCT_IMAGES[m.asin] 引用: {n} 处（应为 2：条件与 src）')
W(f'  是否含 <img: {"是" if "<img" in idx else "否"}')

io.open('analysis/_media_without_img.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_media_without_img.txt')
