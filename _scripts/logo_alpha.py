"""诊断 logo 的 alpha 分布，用阈值找真实内容边界。"""
from PIL import Image
import io

log = []
def P(*a): log.append(' '.join(str(x) for x in a))

for name in ['_src-mark.png', '_src-lockup.png']:
    im = Image.open(f'site/public/brand/{name}').convert('RGBA')
    a = im.getchannel('A')
    w, h = im.size
    hist = a.histogram()
    total = w * h
    P('=' * 72)
    P(f'{name}  {w}x{h}')
    P('  alpha 分布（抽样档位）：')
    bands = [(0, 0), (1, 8), (9, 32), (33, 96), (97, 200), (201, 254), (255, 255)]
    for lo, hi in bands:
        n = sum(hist[lo:hi + 1])
        P(f'    {lo:>3}-{hi:<3} : {n:>9,}  ({100*n/total:5.1f}%)')

    # 用不同阈值求 bbox
    P('  不同 alpha 阈值的边界：')
    for t in [0, 8, 32, 96, 200, 250]:
        mask = a.point(lambda v, t=t: 255 if v > t else 0)
        bb = mask.getbbox()
        if bb:
            P(f'    >{t:<4}  bbox={bb}  尺寸 {bb[2]-bb[0]}x{bb[3]-bb[1]}')
        else:
            P(f'    >{t:<4}  无')
    # 每行/每列 alpha 最大值轮廓（找内容真实上下界）
    P('  行 alpha 峰值（首/末 8 行有内容的）：')
    rows = [max(a.crop((0, y, w, y + 1)).getdata()) for y in range(h)]
    first = next((y for y, v in enumerate(rows) if v > 32), None)
    last = max((y for y, v in enumerate(rows) if v > 32), default=None)
    P(f'    第一行 alpha>32: y={first}   最后: y={last}')
    cols = [max(a.crop((x, 0, x + 1, h)).getdata()) for x in range(w)]
    fc = next((x for x, v in enumerate(cols) if v > 32), None)
    lc = max((x for x, v in enumerate(cols) if v > 32), default=None)
    P(f'    第一列 alpha>32: x={fc}   最后: x={lc}')

io.open('analysis/_logo_alpha.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('ok')
