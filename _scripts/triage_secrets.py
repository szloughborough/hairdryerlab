"""甄别扫描命中：区分「真密钥」与「非敏感配置」。值只打码显示。"""
import io
import re

env = {}
for ln in io.open('site/.env', encoding='utf-8').read().splitlines():
    ln = ln.strip()
    if not ln or ln.startswith('#') or '=' not in ln:
        continue
    k, v = ln.split('=', 1)
    v = v.strip().strip('"').strip("'")
    env[k.strip()] = v

def mask(v):
    if not v:
        return '(空)'
    if len(v) <= 6:
        return v
    return v[:3] + '*' * (len(v) - 5) + v[-2:]

# 被扫描标记的键
FLAGGED = ['LEVANTA_BASE_URL', 'LEVANTA_MARKETPLACE', 'PARTNERBOOST_BASE_URL',
           'ARTEMIS_BASE_URL', 'ARTEMIS_MARKETPLACE', 'AMAZON_ASSOCIATE_TAG',
           'LEVANTA_API_KEY', 'PARTNERBOOST_TOKEN', 'ARTEMIS_API_KEY']

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 88)
W('site/.env 中各键的性质判定')
W('=' * 88)
W(f"{'键名':<26}{'长度':>5}   {'打码值':<24}{'性质'}")
W('-' * 88)

SECRET_HINT = ('KEY', 'TOKEN', 'SECRET', 'PASSWORD')
for k in FLAGGED:
    v = env.get(k, '')
    if any(h in k.upper() for h in SECRET_HINT):
        kind = '★ 真密钥，绝不能入库'
    else:
        kind = '非敏感配置（域名/市场代码）'
    W(f'{k:<26}{len(v):>5}   {mask(v):<24}{kind}')

W('')
W('=' * 88)
W('结论')
W('=' * 88)
secrets = {k: v for k, v in env.items()
           if any(h in k.upper() for h in SECRET_HINT) and len(v) >= 8}
W(f'  真密钥共 {len(secrets)} 个: {list(secrets)}')
W('')
W('  这些密钥是否出现在将入库的文件里？')

import os
import subprocess
files = subprocess.run(['git', '-c', 'core.quotePath=false', 'ls-files'],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace').stdout.splitlines()

found = False
for k, v in secrets.items():
    for f in files:
        if not os.path.isfile(f) or os.path.getsize(f) > 3_000_000:
            continue
        t = io.open(f, encoding='utf-8', errors='ignore').read()
        if v in t:
            W(f'    !! {k} 出现在 {f}')
            found = True
if not found:
    W('    ✓ 没有任何真密钥的值出现在将入库的文件里')

io.open('analysis/_secret_triage.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_secret_triage.txt')
