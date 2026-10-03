"""
全量合规检查运行器 —— 正确区分「通过 / 有 FAIL / 脚本崩溃」。

之所以要单独写这个：此前用 PowerShell 循环 + `2>$null` 调用检查器，
崩溃时 stderr 被吞掉，然后读到的是上一次跑出来的陈旧结果文件，
于是崩溃被静默当成了通过。这里用退出码判断，且崩溃会显式报出来。

退出码约定（见 check_article.py 末尾）：
    0 = 通过    2 = 有 FAIL    1 = 脚本崩溃
"""
import glob
import io
import os
import re
import subprocess
import sys

PY = sys.executable
DRAFTS = sorted(glob.glob('deliverables/drafts/*.mdx'))

passed, failed, crashed = [], [], []
for p in DRAFTS:
    name = os.path.basename(p)[:-4]
    r = subprocess.run([PY, '_scripts/check_article.py', p],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode == 0:
        passed.append(name)
    elif r.returncode == 2:
        failed.append(name)
    else:
        crashed.append((name, (r.stderr or '').strip().splitlines()[-1:] or ['(无 stderr)']))

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 88)
W(f'合规检查：{len(DRAFTS)} 篇')
W('=' * 88)
W(f'  通过      {len(passed):>3}')
W(f'  有 FAIL   {len(failed):>3}   {failed}')
W(f'  脚本崩溃  {len(crashed):>3}')
for name, err in crashed:
    W(f'      !! {name}: {err[0][:110]}')

if failed:
    W('')
    W('=== 未通过明细（FAIL 行）===')
    for name in failed:
        subprocess.run([PY, '_scripts/check_article.py', f'deliverables/drafts/{name}.mdx'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
        # 报告写在文件里，不在 stdout
        rep = io.open('analysis/_compliance.txt', encoding='utf-8').read()
        W(f'  --- {name}')
        for ln in [x for x in rep.splitlines() if 'FAIL' in x][:8]:
            W(f'      {ln.strip()[:130]}')

W('')
W('=' * 88)
ok = not crashed and not failed
W('  判定: ' + ('全部通过' if ok else (
    '**有脚本崩溃，结果不可信**' if crashed else f'{len(failed)} 篇有 FAIL')))
W('=' * 88)

io.open('analysis/_compliance_all.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(f'pass={len(passed)} fail={len(failed)} crash={len(crashed)}')
print('written analysis/_compliance_all.txt')
sys.exit(1 if crashed else 0)
