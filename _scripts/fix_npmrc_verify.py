"""给 site/.npmrc 加上 verify-deps-before-run=false，消除 pnpm 运行前的强制重装。

背景：pnpm 11 在 `pnpm preview` / `pnpm build` 前会校验 node_modules 状态，
判定为「过期」时会尝试删除并重装整个 node_modules；在无 TTY 环境（CI、脚本、
受限沙箱）下这会直接失败：

    ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY

本项目的 node_modules 已正确安装且构建通过（node-linker=hoisted + esbuild/sharp
原生二进制均就绪），因此运行前的这次校验只带来摩擦，不带来收益。
依赖真的缺失时，构建会以明确的模块解析错误失败，不会静默通过。

用 Python 显式 UTF-8 写入，避免 PowerShell 的 GBK 编码问题。
"""
import io
import os

P = 'site/.npmrc'
t = io.open(P, encoding='utf-8').read()

MARK = 'verify-deps-before-run'
BLOCK = '''
# 关闭运行前的依赖校验。
# pnpm 11 判定 node_modules「过期」时会尝试删除并重装，无 TTY 环境下报
# ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY 直接失败。
# 本项目依赖已装好且构建通过，依赖若真缺失，构建会以模块解析错误明确失败。
verify-deps-before-run=false
'''

if MARK in t:
    print('.npmrc 已包含该设置，跳过')
else:
    if not t.endswith('\n'):
        t += '\n'
    t += BLOCK
    io.open(P, 'w', encoding='utf-8', newline='\n').write(t)
    print(f'已写入 {P}（{len(t)} 字符）')

raw = io.open(P, 'rb').read()
try:
    raw.decode('utf-8')
    print('encoding: valid UTF-8')
except UnicodeDecodeError as e:
    print(f'encoding: INVALID at {e.start}')

print()
print('=== .npmrc 最终内容 ===')
for ln in io.open(P, encoding='utf-8').read().splitlines():
    print('  ' + ln)
