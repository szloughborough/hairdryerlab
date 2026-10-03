"""清理 Plausible 残留，并把 FAQ 里的分析工具表述改为 GA4 + Clarity。"""
import io
import os
import re

EDITS = {
    'deliverables/drafts/privacy-policy.mdx': [
        ('a: "Google Analytics 4 sets cookies. Plausible Analytics does not use cookies. If you click through to a retailer such as Amazon.ca, that retailer may set its own cookies, which are governed by its privacy policy rather than ours."',
         'a: "Yes. Google Analytics 4 and Microsoft Clarity both set cookies. Clarity also records session replays, which is a more invasive category and is described in full in the analytics section above. If you click through to a retailer such as Amazon.ca, that retailer may set its own cookies, governed by its privacy policy rather than ours."'),
        ('Google Analytics 4 sets cookies. Plausible Analytics does not use cookies. If you click through to a retailer such as Amazon.ca, that retailer may set its own cookies, which are governed by its privacy policy rather than ours.',
         'Yes. Google Analytics 4 and Microsoft Clarity both set cookies. Clarity also records session replays, which is a more invasive category and is described in full in the analytics section above. If you click through to a retailer such as Amazon.ca, that retailer may set its own cookies, governed by its privacy policy rather than ours.'),
        ('- **No newsletter.** We do not operate a mailing list',
         '- **No newsletter.** We do not operate a mailing list'),
    ],
}

for path, pairs in EDITS.items():
    if not os.path.exists(path):
        print(f'  !! 不存在 {path}')
        continue
    t = io.open(path, encoding='utf-8').read()
    n = 0
    for old, new in pairs:
        if old == new:
            continue
        if old in t:
            t = t.replace(old, new)
            n += 1
    if n:
        io.open(path, 'w', encoding='utf-8').write(t)
    print(f'{path.split("/")[-1]}: 改 {n} 处')

# 全站排查 Plausible 残留
print()
print('=== 全站 Plausible 残留排查 ===')
hits = 0
for root in ('deliverables', 'site/src', 'site/public'):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('node_modules', '.astro', 'dist')]
        for f in fn:
            if not f.endswith(('.md', '.mdx', '.astro', '.ts', '.mjs')):
                continue
            p = os.path.join(dp, f)
            t = io.open(p, encoding='utf-8', errors='ignore').read()
            for m in re.finditer(r'(?i)plausible', t):
                line = t[:m.start()].count('\n') + 1
                print(f'   {p}:{line}')
                hits += 1
if not hits:
    print('   无残留 ✓')
