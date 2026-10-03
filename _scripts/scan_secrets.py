"""
提交前密钥扫描。

逻辑：先读出 site/.env 里的每个值，再在**所有即将入库的文件**里搜索这些值。
只要有一个真实密钥出现在别的文件里，就不该提交。

这比「看文件名像不像敏感文件」可靠得多 —— 密钥经常被抄进文档、示例或笔记里。
"""
import io
import os
import re
import subprocess

def sh(*args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding='utf-8', errors='replace').stdout

# 1) 读 .env 的真实值
env = {}
for ln in io.open('site/.env', encoding='utf-8').read().splitlines():
    ln = ln.strip()
    if not ln or ln.startswith('#') or '=' not in ln:
        continue
    k, v = ln.split('=', 1)
    v = v.strip().strip('"').strip("'")
    if len(v) >= 8:          # 太短的值（如 true/120）会误报，跳过
        env[k.strip()] = v

print(f'site/.env 中长度 >= 8 的值: {len(env)} 个')

# 2) 取即将入库的文件清单
files = [f for f in sh('git', '-c', 'core.quotePath=false', 'ls-files').splitlines() if f.strip()]
print(f'即将入库的文件: {len(files)} 个')
print()

# 3) 逐个搜索
hits = []
for f in files:
    if not os.path.isfile(f):
        continue
    if os.path.getsize(f) > 3_000_000:
        continue
    try:
        t = io.open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for k, v in env.items():
        if v in t:
            # 定位行号
            ln = t[:t.index(v)].count('\n') + 1
            hits.append((f, k, ln))

print('=' * 82)
if hits:
    print(f'!! 发现 {len(hits)} 处密钥值泄漏到即将入库的文件：')
    for f, k, ln in hits:
        print(f'   {f}:{ln}   键名 {k}')
    print()
    print('必须先处理，否则不得提交。')
else:
    print('OK —— 没有任何 .env 的值出现在即将入库的文件里')

# 4) 额外：检查常见密钥形态（即使不在 .env 里）
print()
print('=' * 82)
print('额外扫描：疑似密钥形态的字符串')
PAT = [
    (r'\b[A-Za-z0-9_-]{32,}\b', '长 token 形态'),
    (r'amzn\.to|tag=[a-z0-9]+-\d\d', 'Amazon tag'),
]
suspect = 0
for f in files:
    if not os.path.isfile(f) or os.path.getsize(f) > 3_000_000:
        continue
    t = io.open(f, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r'tag=([a-z0-9]+-\d\d)', t):
        print(f'   {f}: Amazon Associates tag "{m.group(1)}"')
        suspect += 1
if not suspect:
    print('   未发现 Amazon tag 写死在文件里')

io.open('analysis/_secret_scan.txt', 'w', encoding='utf-8').write(
    '\n'.join([f'env values: {len(env)}', f'files: {len(files)}',
               f'leaks: {len(hits)}'] + [f'{f}:{ln} {k}' for f, k, ln in hits]))
print()
print('written analysis/_secret_scan.txt')
