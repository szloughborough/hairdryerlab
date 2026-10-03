"""追加 ImageCaption 的 pending 状态样式（Python 显式 UTF-8，避免 PowerShell 编码问题）。"""
import io

P = 'site/src/styles/global.css'
css = io.open(P, encoding='utf-8').read()

BLOCK = '''
/* ---- §55(23) Image caption：待拍摄状态 ---------------------------------
   §38 禁止用通用图库照片冒充真实拍摄，§62 要求 About 页展示真实测试环境。
   我们目前没有拍摄，因此显示诚实的占位，而不是留一个读者看不见的注释。 */
.fig__slot {
  display: flex; align-items: center; justify-content: center;
  aspect-ratio: 16 / 9;
  border: 1px dashed var(--hdl-border);
  border-radius: var(--hdl-radius-md);
  background: var(--hdl-ice);
}
.fig__slot-text {
  font-family: 'Manrope', sans-serif; font-size: 12px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--hdl-text-secondary);
}
'''

MARK = 'Image caption：待拍摄状态'
if MARK in css:
    print('已存在，跳过')
else:
    if not css.endswith('\n'):
        css += '\n'
    css += BLOCK
    io.open(P, 'w', encoding='utf-8', newline='\n').write(css)
    print(f'已追加，文件现为 {len(css):,} 字符')

raw = io.open(P, 'rb').read()
try:
    raw.decode('utf-8')
    print('encoding: valid UTF-8')
except UnicodeDecodeError as e:
    print(f'encoding: INVALID at {e.start}')
