"""从已安装的 pnpm 源码里找出 pnpm-workspace.yaml 支持的正确设置键名。"""
import io
import os
import re

PNPM_DIST = r'C:\Users\Mloong\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\pnpm\dist\pnpm.mjs'
src = io.open(PNPM_DIST, encoding='utf-8', errors='ignore').read()

out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W('=' * 88)
W('在 pnpm 源码中搜索设置键名')
W('=' * 88)

# pnpm 内部把 workspace yaml 的设置做成 camelCase
CANDS = ['nodeLinker', 'node-linker', 'enablePrePostScripts', 'enable-pre-post-scripts',
         'verifyDepsBeforeRun', 'verify-deps-before-run', 'allowBuilds', 'onlyBuiltDependencies']
for c in CANDS:
    n = src.count(c)
    W(f'   {c:<28} 出现 {n} 次')

W('')
W('=' * 88)
W('nodeLinker 附近的类型定义 / 合法取值')
W('=' * 88)
for m in list(re.finditer(r'nodeLinker', src))[:6]:
    seg = src[max(0, m.start() - 200):m.end() + 260]
    seg = re.sub(r'\s+', ' ', seg)
    W('   ' + seg[:420])
    W('')

W('=' * 88)
W('合法取值 hoisted / isolated / pnpm 的枚举定义')
W('=' * 88)
for m in list(re.finditer(r'"hoisted"|`hoisted`', src))[:5]:
    seg = src[max(0, m.start() - 180):m.end() + 180]
    seg = re.sub(r'\s+', ' ', seg)
    W('   ' + seg[:340])
    W('')

W('=' * 88)
W('allowBuilds 的定义（我上一轮写进 pnpm-workspace.yaml 的那个键）')
W('=' * 88)
for m in list(re.finditer(r'allowBuilds', src))[:4]:
    seg = src[max(0, m.start() - 200):m.end() + 300]
    seg = re.sub(r'\s+', ' ', seg)
    W('   ' + seg[:460])
    W('')

io.open('analysis/_pnpm_settings_keys.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_pnpm_settings_keys.txt')
