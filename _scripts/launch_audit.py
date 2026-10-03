"""上线就绪审计：把「上线前必须解决」的项逐条实测出来。"""
import glob
import io
import os
import re
from collections import Counter

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

D = 'site/dist'
pages = glob.glob(f'{D}/**/*.html', recursive=True)
def dom(p):
    return io.open(p, encoding='utf-8').read()

W('=' * 96)
W('A. 站点与法律配置')
W('=' * 96)
site = io.open('site/src/data/site.ts', encoding='utf-8').read()
for label, pat in [
    ('SITE_URL / 域名', r"SITE_URL\s*=\s*['\"]([^'\"]+)"),
    ('contactEmail', r"contactEmail:\s*['\"]([^'\"]+)"),
    ('operatorName', r"operatorName:\s*['\"]([^'\"]+)"),
    ('effectiveDate', r"effectiveDate:\s*['\"]([^'\"]+)"),
    ('jurisdiction', r"jurisdiction:\s*['\"]([^'\"]+)"),
]:
    m = re.search(pat, site)
    W(f'   {label:<18} {m.group(1) if m else "(未找到)"}')

W('')
W('   canonical 是否都用该域名:')
canon = Counter()
for p in pages[:60]:
    m = re.search(r'<link rel="canonical" href="([^"]+)"', dom(p))
    if m:
        canon[re.match(r'https?://[^/]+', m.group(1)).group(0)] += 1
for k, v in canon.most_common():
    W(f'      {k}  ×{v}')

W('')
W('=' * 96)
W('B. 联盟链接覆盖（网络高佣 vs Amazon Associates 兜底）')
W('=' * 96)
links_src = io.open('site/src/data/affiliate-links.mjs', encoding='utf-8').read()
prod_src = io.open('site/src/data/affiliate-products.mjs', encoding='utf-8').read()

# LINKS 块里每条记录形如： "token": { url: "...", asin: "...", provider: "..." },
resolved = re.findall(r'"([a-z0-9_]+)":\s*\{\s*url:\s*"([^"]+)"[^}]*provider:\s*"([^"]+)"', links_src)
by_provider = Counter(p for _, _, p in resolved)
W(f'   注册表 token 总数            {len(re.findall(chr(34) + "affiliate_url_", prod_src))}')
W(f'   已有联盟网络链接            {len(resolved)}')
for k, v in by_provider.most_common():
    W(f'      {k:<16} {v}')
# META.pending 是权威的未解析列表
m = re.search(r'"pending":\s*\[(.*?)\]', links_src, re.S)
pending = re.findall(r'"([^"]+)"', m.group(1)) if m else []
W(f'   仍走 Associates 兜底        {len(pending)}')
for t in pending:
    W(f'      {t}')
m2 = re.search(r'"syncedAt":\s*"([^"]+)"', links_src)
W(f'   最后同步时间                {m2.group(1) if m2 else "?"}')

W('')
W('=' * 96)
W('C. 商品图片：是否直链 Amazon CDN（依赖 Amazon + 协议风险）')
W('=' * 96)
img_hosts = Counter()
for p in pages:
    for m in re.findall(r'<img[^>]*src="(https?://[^"]+)"', dom(p)):
        img_hosts[re.match(r'https?://([^/]+)', m).group(1)] += 1
for k, v in img_hosts.most_common():
    W(f'   {k:<34} {v} 个 <img>')
local = {k: v for k, v in img_hosts.items() if 'amazon' not in k}
W(f'   → 非 Amazon 来源的图: {sum(local.values())} 个（其余全部直链 Amazon CDN）')

W('')
W('=' * 96)
W('D. 未发布 / 占位内容')
W('=' * 96)
drafts = sorted(glob.glob('deliverables/drafts/*.mdx'))
drafted, placeholders = [], []
for p in drafts:
    t = io.open(p, encoding='utf-8').read()
    if re.search(r'(?m)^draft:\s*true', t):
        drafted.append(os.path.basename(p)[:-4])
    n = len(re.findall(r'【[^】]*(?:待实测|待核实|待补)[^】]*】', t))
    if n:
        placeholders.append((os.path.basename(p)[:-4], n))
W(f'   draft: true（不上线）: {drafted if drafted else "无"}')
W(f'   含待实测/待核实占位符:')
for n, c in placeholders:
    W(f'      {n}  ×{c}')
if not placeholders:
    W('      无')

W('')
W('=' * 96)
W('E. 每页 OG 图 / 结构化数据 / 语言')
W('=' * 96)
og_default = sum(1 for p in pages if '/brand/og-default.png' in dom(p))
W(f'   OG 图 = og-default.png（全站同一张）: {og_default}/{len(pages)}')
custom_og = len(pages) - og_default
W(f'   OG 图 = 每页自定义: {custom_og}')
ld = sum(1 for p in pages if 'application/ld+json' in dom(p))
W(f'   含 JSON-LD 结构化数据的页面: {ld}/{len(pages)}')
W(f'   html lang="en-CA" 的页面: {sum(1 for p in pages if chr(34)+"en-CA"+chr(34) in dom(p)[:600])}')
W(f'   存在 /fr/ 法语版: {"是" if os.path.isdir(f"{D}/fr") else "否"}')

W('')
W('=' * 96)
W('F. 信任页与合规页是否齐全')
W('=' * 96)
need = {
    '/about/': 'About',
    '/contact/': 'Contact',
    '/editorial-policy/': 'Editorial policy',
    '/affiliate-disclosure/': 'Affiliate disclosure',
    '/privacy-policy/': 'Privacy policy',
    '/terms/': 'Terms',
    '/how-we-test/': 'How we test',
    '/authors/hair-dryer-lab-editorial/': 'Author page',
}
for route, label in need.items():
    okk = os.path.exists(f'{D}{route}index.html')
    W(f'   {"OK " if okk else "缺失"}  {label:<22} {route}')

W('')
W('=' * 96)
W('G. 源码里的待办与外部依赖')
W('=' * 96)
todos = 0
for root in ('site/src', 'deliverables/drafts'):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if not f.endswith(('.astro', '.ts', '.mjs', '.mdx')):
                continue
            fp = os.path.join(dp, f)
            for m in re.finditer(r'(?i)TODO|FIXME|待办|上线前必须|尚未接入|未接入', io.open(fp, encoding='utf-8', errors='ignore').read()):
                ln = io.open(fp, encoding='utf-8', errors='ignore').read()[:m.start()].count('\n') + 1
                if todos < 20:
                    W(f'   {fp}:{ln}')
                todos += 1
W(f'   合计 {todos} 处标记')

io.open('analysis/_launch_audit.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_launch_audit.txt')
