"""
字体文件去重。

Google Fonts 对 Inter 返回的是可变字体：400/500/600 三个字重指向同一个文件。
上面的下载把它们各存了一份，浪费约 340 KB。这里按内容哈希去重，
并重写 fonts.css 让多个字重共用同一文件。
"""
import hashlib
import io
import os
import re

FDIR = 'site/public/fonts'
CSS = 'site/src/styles/fonts.css'

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

files = sorted(os.listdir(FDIR))
by_hash = {}
for f in files:
    p = os.path.join(FDIR, f)
    h = hashlib.sha256(io.open(p, 'rb').read()).hexdigest()[:16]
    by_hash.setdefault(h, []).append(f)

W(f'目录内 {len(files)} 个文件，{len(by_hash)} 份唯一内容')
W('')
dups = {h: fs for h, fs in by_hash.items() if len(fs) > 1}
for h, fs in dups.items():
    W(f'   重复组: {", ".join(fs)}')

# 每组保留一个规范名（优先不带字重后缀差异的、名字最短的），删除其余
canon = {}
removed = []
for h, fs in by_hash.items():
    if len(fs) == 1:
        canon[h] = fs[0]
        continue
    # 规范名：inter-<weight>-<subset> 里取最小的 weight 作为代表名不好读，
    # 改为 inter-variable-<subset> 这类语义名
    fam = fs[0].split('-')[0]
    subset = fs[0].split('-')[-1].replace('.woff2', '')
    keep_name = f'{fam}-variable-{subset}.woff2'
    src = os.path.join(FDIR, fs[0])
    dst = os.path.join(FDIR, keep_name)
    if os.path.exists(dst) and dst != src:
        os.remove(dst)
    os.rename(src, dst)
    for other in fs[1:]:
        op = os.path.join(FDIR, other)
        if os.path.exists(op):
            os.remove(op)
            removed.append(other)
    canon[h] = keep_name

W('')
W(f'删除重复文件 {len(removed)} 个: {removed}')

# 重写 CSS：按 (family, weight, subset) 生成，src 指向去重后的文件
css = io.open(CSS, encoding='utf-8').read()
head = css.split('@font-face')[0]

# 从原 CSS 里取回每条的 family/weight/style/unicode-range
entries = re.findall(
    r"font-family: '([^']+)';\s*\n\s*font-style: (\w+);\s*\n\s*font-weight: (\d+);\s*\n"
    r"\s*font-display: swap;\s*\n\s*src: url\(/fonts/([^)]+)\)[^;]*;\s*\n"
    r"(?:\s*unicode-range: ([^;]+);)?",
    css)

# 旧文件名 → 新文件名
rename_map = {}
for h, fs in by_hash.items():
    if len(fs) > 1:
        for f in fs:
            rename_map[f] = canon[h]

lines = [head.rstrip(), '']
seen = set()
for fam, style, wt, fname, urange in entries:
    newf = rename_map.get(fname, fname)
    key = (fam, wt, newf)
    if key in seen:
        continue
    seen.add(key)
    lines.append('@font-face {')
    lines.append(f"  font-family: '{fam}';")
    lines.append(f'  font-style: {style};')
    lines.append(f'  font-weight: {wt};')
    lines.append('  font-display: swap;')
    lines.append(f'  src: url(/fonts/{newf}) format("woff2");')
    if urange:
        lines.append(f'  unicode-range: {urange.strip()};')
    lines.append('}')
    lines.append('')

io.open(CSS, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))

final = sorted(os.listdir(FDIR))
total = sum(os.path.getsize(os.path.join(FDIR, f)) for f in final)
W('')
W(f'最终 {len(final)} 个文件，合计 {total:,} 字节（{total/1024:.0f} KB）')
for f in final:
    W(f'   {os.path.getsize(os.path.join(FDIR, f)):>8,} B  {f}')

io.open('analysis/_fonts_dedupe.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(f'kept {len(final)} files, total {total} bytes')
print('written analysis/_fonts_dedupe.txt')
