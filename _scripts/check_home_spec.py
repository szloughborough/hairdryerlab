"""对首页实际发布的 CSS 做品牌规范符合性复核。

Astro 把 <style> 抽成 dist/_astro/*.css，并给选择器加 [data-astro-cid-*] 作用域属性，
所以必须读那个文件，且正则要容忍属性选择器。
"""
import glob
import io
import re

# 找到首页引用的 CSS
html = io.open('site/dist/index.html', encoding='utf-8').read()
hrefs = re.findall(r'href="(/_astro/[^"]+\.css)"', html)
raw = ''
for h in hrefs:
    raw += io.open('site/dist' + h, encoding='utf-8').read()

# Astro 会给选择器插入作用域属性，如 .hhero[data-astro-cid-x] h1[data-astro-cid-x]。
# 匹配前先剥掉它们，否则正则全部落空（曾因此误报 6 项 MISSING）。
css = re.sub(r'\[data-astro-cid-[a-z0-9]+\]', '', raw)

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W(f'首页引用的 CSS: {hrefs}')
W(f'原始 CSS {len(raw):,} 字符；剥离作用域属性后 {len(css):,} 字符')
W('')

# 作用域属性形如 [data-astro-cid-xxxx]，写正则时统一容忍
def rule(sel, body_pat):
    """在 css 中找 .sel 开头的规则（允许其后跟作用域属性），并检查 body 里是否有 body_pat"""
    pat = re.compile(r'\.' + re.escape(sel) + r'[^{]*\{([^}]*)\}')
    for m in pat.finditer(css):
        if re.search(body_pat, m.group(1)):
            return True
    return False

CHECKS = [
    ('§17 H1 = 48px (desktop)',            'hhero h1',   r'font-size:\s*48px'),
    ('§17 H1 line-height 1.1–1.2',         'hhero h1',   r'line-height:\s*1\.1'),
    ('§17 H2 = 34px (desktop)',            'sec__h',     r'font-size:\s*34px'),
    ('§17 H3 = 24px (model card)',         'model__name', r'font-size:\s*24px'),
    ('§17 H3 = 24px (trust column)',       'trust__h',   r'font-size:\s*24px'),
    ('§17 body = 17px',                    'sec__p',     r'font-size:\s*17px'),
    ('§13 proof band = Ice Blue',          'proof',      r'background:\s*var\(--hdl-ice\)'),
    ('§20 cards radius-md (12px)',         'model',      r'border-radius:\s*var\(--hdl-radius-md\)'),
    ('§20 badges radius-pill (999px)',     'model__status', r'border-radius:\s*var\(--hdl-radius-pill\)'),
    ('§25 hero still-life present',        'still',      r'background:\s*var\(--hdl-ice\)'),
    ('mix-blend-mode on still images',     'still__item img', r'mix-blend-mode:\s*multiply'),
]

W('=' * 88)
W('品牌规范符合性')
W('=' * 88)
for label, sel, pat in CHECKS:
    W(f'   {"OK      " if rule(sel, pat) else "MISSING "} {label}')

W('')
W('=' * 88)
W('§13 Navy 不得用于整幅底色（数据带已改为冰蓝）')
W('=' * 88)
navy_bg = re.findall(r'\.proof[^{]*\{[^}]*background:\s*var\(--hdl-navy\)', css)
W(f'   .proof 使用 navy 底: {len(navy_bg)} 处  {"OK" if not navy_bg else "VIOLATION"}')

W('')
W('=' * 88)
W('§17 移动端字号（媒体查询内）')
W('=' * 88)
for label, pat in [
    ('H1 32–34px', r'\.hhero h1\{[^}]*font-size:3[234]px'),
    ('H2 26–28px', r'\.sec__h\{[^}]*font-size:2[678]px'),
    # 移动端这条是组合选择器 .model__name,.trust__h{...}，正则需容忍逗号
    ('H3 21–23px', r'\.model__name[^{]*\{[^}]*font-size:2[123]px'),
]:
    W(f'   {"OK      " if re.search(pat, css) else "MISSING "} {label}')

W('')
W('=' * 88)
W('页面结构')
W('=' * 88)
W(f'   <h1> {len(re.findall(r"<h1[ >]", html))}   <h2> {len(re.findall(r"<h2[ >]", html))}   <h3> {len(re.findall(r"<h3[ >]", html))}')
W(f'   「Not yet tested」: {html.count("Not yet tested")} 次（改版前 9 次）')
W(f'   状态徽章「Not yet bench-tested」: {html.count("Not yet bench-tested")} 次')
W(f'   首页 <img>: {len(re.findall(r"<img", html))} 个')
W(f'   TestedBadge 假徽章: {html.count("badge badge--tested")} 个（应为 0）')
W('')
W('   h3 逐个列出（确认没有意外的第三级标题）：')
for m in re.finditer(r'<h3[^>]*>(.*?)</h3>', html, re.S):
    txt = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    W(f'      {txt[:70]}')

io.open('analysis/_home_spec_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
