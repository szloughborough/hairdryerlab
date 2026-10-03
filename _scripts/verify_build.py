"""验证 Astro 构建产物：结构、SEO 元素、JSON-LD、内链、锚点、图片。"""
import io, os, re, json, glob

DIST = 'site/dist'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

P('=' * 92)
P('Astro 构建产物验证')
P('=' * 92)

files = []
for root, _, fns in os.walk(DIST):
    for fn in fns:
        if fn.endswith(('.html', '.xml', '.txt', '.css', '.js', '.svg', '.ico')):
            p = os.path.join(root, fn)
            files.append((os.path.relpath(p, DIST), os.path.getsize(p)))
P('\n--- 产物清单 ---')
for p, s in sorted(files):
    P(f'  {p:<44} {s:>8,} bytes')

CSS_FILES = [p for p, _ in files if p.endswith('.css')]

def check(rel, label, is_article):
    p = os.path.join(DIST, rel)
    if not os.path.exists(p):
        P(f'\n!! 缺少 {rel}'); return {}
    h = io.open(p, encoding='utf-8').read()
    P(f'\n--- {rel}  ({label}) ---')
    n_h1 = len(re.findall(r'<h1[\s>]', h))
    # 目录组件自身的 <h2>On this page</h2> 不算内容标题
    content_h2 = [m for m in re.findall(r'<h2[^>]*>', h) if 'class="toc"' not in m]
    h2_all = re.findall(r'<h2[^>]*>', h)
    h2_ids = len(re.findall(r'<h2 id=', h))
    toc_h2 = len(h2_all) - h2_ids
    P(f'  H1 数 = {n_h1}   {"PASS" if n_h1 == 1 else "**FAIL**"}')
    P(f'  H2 数 = {len(h2_all)}（带 id {h2_ids} / 无 id {toc_h2} —— 无 id 的是目录标题）'
      f'   {"PASS" if h2_ids == len(h2_all) - 1 or h2_ids == len(h2_all) else "检查"}')
    can = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    cv = can.group(1) if can else ''
    P(f'  canonical = {cv}   {"PASS" if can else "**FAIL**"}')
    if cv and ('?' in cv or '#' in cv):
        P('  **FAIL** canonical 含 query/fragment')
    ti = re.search(r'<title>(.*?)</title>', h, re.S)
    t = ti.group(1) if ti else ''
    P(f'  title({len(t)}) = {t[:72]}   {"PASS" if 45 <= len(t) <= 70 else "WARN"}')
    de = re.search(r'<meta name="description" content="([^"]*)"', h)
    dl = len(de.group(1)) if de else 0
    P(f'  meta desc 长度 = {dl}   {"PASS" if 130 <= dl <= 175 else "WARN"}')
    P(f'  og:title = {"有" if "og:title" in h else "缺"}')
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    types = []
    for b in blocks:
        try:
            d = json.loads(b)
            for node in d.get('@graph', [d]):
                types.append(node.get('@type'))
        except Exception as e:
            P(f'  **FAIL** JSON-LD 解析失败: {e}')
    P(f'  JSON-LD = {types if types else "**无**"}')
    alljson = ' '.join(blocks)
    P(f'  无 Offer = {"PASS" if chr(34)+"Offer"+chr(34) not in alljson else "**FAIL**"}'
      f'   无 aggregateRating = {"PASS" if "aggregateRating" not in alljson else "**FAIL**"}')
    n_tbl = len(re.findall(r'<table', h))
    n_link = len(re.findall(r'href="/', h))
    n_img = len(re.findall(r'<img[\s>]', h))
    P(f'  <table> = {n_tbl}   内链 = {n_link}   <img> = {n_img}')
    if n_img:
        srcs = re.findall(r'<img[^>]+src="([^"]+)"', h)
        n_alt = len(re.findall(r'<img[^>]+alt="[^"]+"', h))
        P(f'    图片 alt 覆盖 = {n_alt}/{n_img}   {"PASS" if n_alt == n_img else "**FAIL**"}')
        P(f'    首个 src = {srcs[0][:78]}')
    P(f'  页脚={"✓" if "site-footer" in h else "✗"}  导航={"✓" if "main-nav" in h else "✗"}  '
      f'面包屑={"✓" if "breadcrumbs" in h else "✗"}')
    if is_article:
        P(f'  目录TOC={"✓" if "class=" + chr(34) + "toc" + chr(34) in h else "✗"}   '
          f'联盟披露={"✓" if "Affiliate disclosure" in h else "N/A"}')
        P(f'  FAQ 问题 = {len(re.findall(r"<strong>[^<]*?</strong>", h))} 个粗体小标题')
    return {'h1': n_h1, 'img': n_img}

pages = []
for p in sorted(glob.glob(os.path.join(DIST, '**', '*.html'), recursive=True)):
    rel = os.path.relpath(p, DIST).replace('\\', '/')
    if rel == '404.html':
        pages.append((rel, '404', False)); continue
    label = '内容页' if rel != 'index.html' else '首页'
    pages.append((rel, label, rel != 'index.html'))

for rel, label, is_article in pages:
    check(rel, label, is_article)

P('\n--- sitemap ---')
for f in sorted(glob.glob(os.path.join(DIST, 'sitemap*.xml'))):
    x = io.open(f, encoding='utf-8').read()
    locs = re.findall(r'<loc>(.*?)</loc>', x)
    P(f'  {os.path.basename(f)}: {len(locs)}')
    if 'index' not in f:
        for l in locs: P(f'    {l}')

P('\n--- 静态文件 ---')
for f in ['robots.txt', 'llms.txt', 'favicon.svg', 'og-default.svg']:
    P(f'  {f}: {"✓" if os.path.exists(os.path.join(DIST, f)) else "**缺失**"}')
rt = io.open(os.path.join(DIST, 'robots.txt'), encoding='utf-8').read() if os.path.exists(os.path.join(DIST, 'robots.txt')) else ''
P(f'  robots 允许 AI 爬虫: {"✓ " + str(len(re.findall(r"User-agent: (GPTBot|PerplexityBot|ClaudeBot|Google-Extended|CCBot)", rt))) + "/5" if rt else "✗"}')

io.open('analysis/_build_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_build_check.txt')
