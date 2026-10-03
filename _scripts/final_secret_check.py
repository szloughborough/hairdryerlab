"""提交前最后一关：确认暂存区里没有任何 .env 真密钥（纯 ASCII 输出，避免控制台编码问题）。"""
import io
import os
import re
import subprocess

env = {}
for ln in io.open('site/.env', encoding='utf-8').read().splitlines():
    if '=' in ln and not ln.strip().startswith('#'):
        k, v = ln.split('=', 1)
        v = v.strip().strip('"').strip("'")
        if len(v) >= 12:
            env[k.strip()] = v

secrets = {k: v for k, v in env.items()
           if any(h in k.upper() for h in ('KEY', 'TOKEN', 'SECRET'))}

lines = []
def W(*a): lines.append(' '.join(str(x) for x in a))

W(f'secret keys in site/.env : {len(secrets)}  -> {sorted(secrets)}')

files = subprocess.run(['git', 'ls-files'], capture_output=True, text=True,
                       encoding='utf-8', errors='replace').stdout.splitlines()
W(f'files staged             : {len(files)}')

hits = []
for f in files:
    if not os.path.isfile(f) or os.path.getsize(f) > 5_000_000:
        continue
    try:
        t = io.open(f, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    for k, v in secrets.items():
        if v in t:
            hits.append((k, f))

W('')
if hits:
    W(f'LEAKS: {len(hits)}')
    for k, f in hits:
        W(f'   {k} appears in {f}')
    W('')
    W('RESULT: FAIL - do not commit')
else:
    W('LEAKS: 0')
    W('RESULT: PASS - no real secret value appears in any staged file')

bad = [f for f in files if re.search(r'(^|/)\.env$', f) or re.search(r'\.(pem|key)$', f)]
W('')
W(f'dotenv/cert files staged : {len(bad)}' + (f'  -> {bad}' if bad else '  (none)'))

io.open('analysis/_final_secret_check.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
