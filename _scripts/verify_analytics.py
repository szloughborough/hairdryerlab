"""核验 4 个验证/分析代码是否真的注入了每个页面的 <head>。"""
import glob
import io
import re

D = 'site/dist'
pages = glob.glob(f'{D}/**/*.html', recursive=True)
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

PATTERNS = {
    'GA4 衡量 ID (G-FGWTDV59DY)': r'G-FGWTDV59DY',
    'GA4 gtag.js 加载器': r'googletagmanager\.com/gtag/js',
    'GA4 gtag config 调用': r"gtag\('config'",
    'GSC 验证 meta': r'name="google-site-verification" content="ViysjFF_EJFI-6tPem4t39Q_qTNZi9Iouy36BeNhGpI"',
    'Bing 验证 meta': r'name="msvalidate\.01" content="DBDA9C5B702CB4727F1CFE5872FFA081"',
    'Clarity 项目 ID': r'yrs10sr6pg',
    'Clarity 脚本域名': r'clarity\.ms/tag/',
    'Clarity 队列函数': r"c\[a\]\.q=c\[a\]\.q",
}

W('=' * 84)
W(f'第三方代码注入核验（共 {len(pages)} 个页面）')
W('=' * 84)
for label, pat in PATTERNS.items():
    hit = sum(1 for p in pages if re.search(pat, io.open(p, encoding='utf-8').read()))
    ok = hit == len(pages)
    W(f'   {label:<30} {hit:>3}/{len(pages)}  {"OK" if ok else ("**只有部分页面**" if hit else "**缺失**")}')

W('')
W('=' * 84)
W('抽查首页 <head> 中的实际注入位置')
W('=' * 84)
h = io.open(f'{D}/index.html', encoding='utf-8').read()
head = h[:h.find('</head>')]
for label, pat in [
    ('GSC meta', r'<meta name="google-site-verification"[^>]*>'),
    ('Bing meta', r'<meta name="msvalidate\.01"[^>]*>'),
    ('GA4 loader', r'<script[^>]*googletagmanager[^>]*>'),
    ('Clarity', r'<script[^>]*>[^<]*clarity[^<]*</script>'),
]:
    m = re.search(pat, head, re.S)
    W(f'   {label}:')
    W(f'      {m.group(0)[:150] if m else "**未找到**"}')

W('')
W('=' * 84)
W('隐私政策是否已如实披露两个工具')
W('=' * 84)
pp = io.open(f'{D}/privacy-policy/index.html', encoding='utf-8').read()
for label, pat in [
    ('披露 Google Analytics 4', r'Google Analytics 4'),
    ('披露 Microsoft Clarity', r'Microsoft Clarity'),
    ('说明会话回放', r'session replay|Session replay'),
    ('已移除 Plausible 表述', r'(?!x)x'),
]:
    if label.startswith('已移除'):
        n = len(re.findall(r'Plausible Analytics', pp))
        W(f'   {"OK" if n == 0 else "**仍有 " + str(n) + " 处**"}  {label}')
    else:
        n = len(re.findall(pat, pp))
        W(f'   {"OK" if n else "**缺失**"}  {label}（{n} 处）')

io.open('analysis/_analytics_verify.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_analytics_verify.txt')
