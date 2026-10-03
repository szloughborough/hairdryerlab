"""检查 logo 文件属性：尺寸、色彩模式、背景色、内容边界、主色。"""
from PIL import Image
import io, collections

out = []
def P(*a): out.append(' '.join(str(x) for x in a))

for name in ['_src-mark.png', '_src-lockup.png']:
    p = f'site/public/brand/{name}'
    im = Image.open(p)
    P('=' * 70)
    P(f'{name}')
    P(f'  尺寸 = {im.size}   模式 = {im.mode}')
    P(f'  信息 = {im.info.get("dpi", "-")}')

    rgba = im.convert('RGBA')
    w, h = rgba.size
    px = rgba.load()

    # 四角颜色
    corners = {
        'TL': px[0, 0], 'TR': px[w - 1, 0],
        'BL': px[0, h - 1], 'BR': px[w - 1, h - 1],
    }
    P(f'  四角像素 = {corners}')

    # 是否已有透明通道
    alphas = rgba.getchannel('A')
    amin, amax = alphas.getextrema()
    P(f'  Alpha 范围 = {amin}..{amax}  ({"已有透明" if amin < 255 else "无透明，实底"})')

    # 主色统计（量化到 16 级）
    small = rgba.convert('RGB').resize((min(300, w), min(300, h)))
    cnt = collections.Counter(small.getdata())
    P('  前 6 主色：')
    for c, n in cnt.most_common(6):
        P(f'     rgb{c}  #{c[0]:02X}{c[1]:02X}{c[2]:02X}  {n} px')

    # 内容边界（与背景色差异大于阈值的像素）
    bg = cnt.most_common(1)[0][0]
    import math
    def diff(c):
        return math.dist(c[:3], bg[:3])
    minx, miny, maxx, maxy = w, h, 0, 0
    step = max(1, w // 600)
    for y in range(0, h, step):
        for x in range(0, w, step):
            if diff(px[x, y]) > 40:
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    if maxx > minx:
        P(f'  背景色 = rgb{bg}')
        P(f'  内容边界 = ({minx},{miny}) - ({maxx},{maxy})  尺寸 {maxx-minx+1}x{maxy-miny+1}')
        P(f'  四周留白 = L{minx} R{w-1-maxx} T{miny} B{h-1-maxy}')
        P(f'  内容占比 = {100*(maxx-minx+1)/w:.1f}% 宽 x {100*(maxy-miny+1)/h:.1f}% 高')
    else:
        P('  未检测到内容边界')

io.open('analysis/_logo_check.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written analysis/_logo_check.txt')
