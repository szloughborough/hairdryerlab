"""
修复 global.css 的 GBK 编码片段，并全仓扫描其他被同类污染的源文件。
（成因：此前用 PowerShell Add-Content 追加含中文的内容，写入时按 ANSI/GBK 编码。）
"""
import io
import os

FIX = 'site/src/styles/global.css'
out = []
def P(*a): out.append(' '.join(str(x) for x in a))

raw = io.open(FIX, 'rb').read()
before = len(raw)

# 找到第一个非法 UTF-8 位置，前后切开
i = 0
first_bad = None
while i < len(raw):
    try:
        raw[i:].decode('utf-8')
        break
    except UnicodeDecodeError as e:
        if first_bad is None:
            first_bad = i + e.start
            break
        i = i + e.start + 1

if first_bad is not None:
    head = raw[:first_bad]
    tail = raw[first_bad:]
    # 头部应是合法 UTF-8；尾部按 GBK 解码还原为中文
    head_txt = head.decode('utf-8')
    try:
        tail_txt = tail.decode('gbk')
        P(f'尾部按 GBK 解码成功（{len(tail)} 字节 → {len(tail_txt)} 字符）')
    except UnicodeDecodeError:
        # 混合情况：逐字节兜底
        tail_txt = tail.decode('gbk', errors='replace')
        P('尾部含无法按 GBK 解码的字节，已用 replace 兜底')
    fixed = head_txt + tail_txt
    io.open(FIX, 'w', encoding='utf-8', newline='\n').write(fixed)
    P(f'已重写 {FIX}：{before:,} → {len(fixed.encode("utf-8")):,} 字节')
else:
    P(f'{FIX}: 无非法 UTF-8，未改动')

# 全仓扫描
P('')
P('=' * 84)
P('全仓扫描：其他含非法 UTF-8 的源文件')
P('=' * 84)
roots = ['site/src', 'deliverables', '_scripts', 'site/public']
bad_files = []
for root in roots:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ('node_modules', '.astro', 'dist', '__pycache__')]
        for fn in filenames:
            if not fn.endswith(('.astro', '.ts', '.mjs', '.js', '.css', '.md', '.mdx', '.json', '.py', '.txt', '.example')):
                continue
            p = os.path.join(dirpath, fn)
            try:
                io.open(p, 'rb').read().decode('utf-8')
            except UnicodeDecodeError as e:
                bad_files.append((p, e.start, e.reason))
            except Exception:
                pass

if bad_files:
    P(f'发现 {len(bad_files)} 个文件含非法 UTF-8：')
    for p, pos, why in bad_files:
        P(f'   {p}   首错位置 {pos}   {why}')
else:
    P('   未发现其他损坏文件 ✓')

io.open('analysis/_encoding_fix.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_encoding_fix.txt')
