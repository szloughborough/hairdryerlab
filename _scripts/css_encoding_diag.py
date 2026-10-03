"""诊断 global.css 的编码损坏范围。"""
import io

P = 'site/src/styles/global.css'
raw = io.open(P, 'rb').read()
out = []
def W(*a): out.append(' '.join(str(x) for x in a))

W(f'文件字节数: {len(raw):,}')

# 逐字节找非 UTF-8 序列的位置
bad = []
try:
    raw.decode('utf-8')
    W('整个文件是合法 UTF-8')
except UnicodeDecodeError as e:
    W(f'首个非法字节位置: {e.start} (0x{raw[e.start]:02x})，原因: {e.reason}')

# 找出所有非法位置
i = 0
while i < len(raw):
    try:
        raw[i:].decode('utf-8')
        break
    except UnicodeDecodeError as e:
        bad.append(i + e.start)
        i = i + e.start + 1

W(f'非法字节总数: {len(bad)}')
if bad:
    W(f'首个: {bad[0]}   末个: {bad[-1]}')
    W(f'分布区间: {"文件后段" if bad[0] > len(raw) * 0.8 else "文件中前段"}')

# 尝试用 GBK 解码，看中文是否可读
for enc in ('gbk', 'latin-1'):
    try:
        t = raw.decode(enc)
        # 看是否含典型乱码
        mangle = sum(t.count(c) for c in '鑱鍑鈥锛')
        W(f'{enc} 解码成功，乱码特征字符 {mangle} 个')
        if enc == 'gbk':
            gbk_text = t
    except Exception as e:
        W(f'{enc} 解码失败: {e}')

# 定位非法字节附近的上下文
if bad:
    p = max(0, bad[0] - 120)
    W('')
    W('=== 首个非法字节附近的原始字节 ===')
    W(repr(raw[p:bad[0] + 80]))

io.open('analysis/_css_encoding_diag.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_css_encoding_diag.txt')
