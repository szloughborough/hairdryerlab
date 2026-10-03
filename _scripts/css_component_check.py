"""检查品牌 §55 组件的样式是否已定义在 global.css。"""
import io
import re

css = io.open('site/src/styles/global.css', encoding='utf-8').read()
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P(f'global.css 共 {len(css):,} 字符 / {len(css.splitlines())} 行')
P('')
P('=== 组件样式是否已在 global.css 中定义 ===')
for c in ['lab-test', 'verdict-split', 'proscons', 'ratings', 'price-box',
          'cta-support', 'evidence-label', 'picks', 'pick-card', 'verdict']:
    n = len(re.findall(r'\.' + re.escape(c) + r'\b', css))
    P(f'   .{c:<20} {n:>3} 处选择器')

P('')
P('=== global.css 的分区标题 ===')
for m in re.findall(r'(?m)^/\*\s*[-=─\s]*(.{0,70}?)\s*\*/', css):
    s = m.strip()
    if s and len(s) > 2:
        P('   ' + s)

P('')
P('=== 组件源码里的 class 清单 ===')
import os
for f in sorted(os.listdir('site/src/components')):
    if not f.endswith('.astro'):
        continue
    s = io.open(f'site/src/components/{f}', encoding='utf-8').read()
    cls = sorted(set(re.findall(r'class="([^"{]+)"', s)))
    if cls:
        P(f'   {f:<26} {", ".join(cls)[:100]}')

io.open('analysis/_css_component_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_css_component_check.txt')
