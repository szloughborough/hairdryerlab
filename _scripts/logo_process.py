"""
处理品牌 logo：
  1. 按 alpha 精确裁切（去掉多余留白）
  2. 导出 header 用 lockup 与 mark
  3. 生成 favicon 组（ice blue 圆角方底 + 原色 navy mark）—— 遵循品牌规范 §65
  4. 生成 1200×630 OG 图（PNG，替代原先的 SVG —— 多数平台不解析 SVG OG 图）
输出到 site/public/brand/
"""
from PIL import Image, ImageDraw, ImageFont
import io, os

SRC = 'site/src/assets/brand-src'   # 原始大图（不发布）
OUT = 'site/public/brand'           # 派生产物（发布）
os.makedirs(OUT, exist_ok=True)

# 品牌色（品牌规范 §13）
NAVY = (24, 49, 83)        # #183153
ICE = (234, 243, 247)      # #EAF3F7
WARM = (250, 250, 248)     # #FAFAF8
CORAL = (232, 93, 74)      # #E85D4A
TEXT2 = (102, 114, 122)    # #66727A

log = []
def P(*a): log.append(' '.join(str(x) for x in a))


def trim(im, thresh=8):
    """
    清除极淡的 alpha 光晕（alpha < thresh 视为完全透明），再按 alpha 精确裁切。
    源文件带 alpha 1–8 的不可见光晕，若不清理会留下大量隐形留白，
    导致 logo 在页面上显得偏小。
    """
    im = im.convert('RGBA')
    r, g, b, a = im.split()
    a = a.point(lambda v: 0 if v < thresh else v)
    cleaned = Image.merge('RGBA', (r, g, b, a))
    bbox = a.getbbox()
    return cleaned.crop(bbox), bbox


mark = Image.open(f'{SRC}/_src-mark.png').convert('RGBA')
lockup = Image.open(f'{SRC}/_src-lockup.png').convert('RGBA')

P('=' * 70)
P('1) 裁切')
mark_t, mb = trim(mark)
lockup_t, lb = trim(lockup)
P(f'  mark   {mark.size} -> {mark_t.size}   (裁掉 {mb})')
P(f'  lockup {lockup.size} -> {lockup_t.size}   (裁掉 {lb})')

# ---------- 2) header 用 lockup：输出 2x ----------
LOCK_H = 64
lock_w = round(lockup_t.width * LOCK_H / lockup_t.height)
lockup_out = lockup_t.resize((lock_w, LOCK_H), Image.LANCZOS)
lockup_out.save(f'{OUT}/logo-lockup.png', optimize=True)
P('')
P('2) 导出')
P(f'  logo-lockup.png  {lockup_out.size}   ({os.path.getsize(f"{OUT}/logo-lockup.png"):,} bytes)')

# mark：输出 640 宽
MARK_W = 640
mark_h = round(mark_t.height * MARK_W / mark_t.width)
mark_out = mark_t.resize((MARK_W, mark_h), Image.LANCZOS)
mark_out.save(f'{OUT}/logo-mark.png', optimize=True)
P(f'  logo-mark.png    {mark_out.size}   ({os.path.getsize(f"{OUT}/logo-mark.png"):,} bytes)')


# ---------- 3) favicon 组 ----------
def rounded(size, radius_ratio=0.22, bg=ICE):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = round(size * radius_ratio)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=bg)
    return im


def favicon(size):
    """ice blue 圆角方底 + 原色 navy mark（§65 允许 "navy mark"，保持 logo 原色不改）"""
    canvas = rounded(size)
    pad = round(size * 0.17)
    inner_w = size - pad * 2
    inner_h = round(mark_t.height * inner_w / mark_t.width)
    m = mark_t.resize((inner_w, inner_h), Image.LANCZOS)
    x = pad
    y = (size - inner_h) // 2
    canvas.alpha_composite(m, (x, y))
    return canvas


P('')
P('3) favicon 组（ice blue 圆角底 + 原色 mark）')
for s, fn in [(32, 'favicon-32.png'), (180, 'apple-touch-icon.png'),
              (192, 'favicon-192.png'), (512, 'favicon-512.png')]:
    im = favicon(s)
    im.save(f'{OUT}/{fn}', optimize=True)
    P(f'  {fn:<24} {im.size}   {os.path.getsize(f"{OUT}/{fn}"):,} bytes')

# ICO（多尺寸，兼容旧浏览器与书签）
ico = favicon(64)
ico.save(f'{OUT}/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
P(f'  favicon.ico              multi-size   {os.path.getsize(f"{OUT}/favicon.ico"):,} bytes')


# ---------- 4) OG 图 1200x630 ----------
def load_font(size, bold=False):
    cands = [
        r'C:\Windows\Fonts\segoeuib.ttf' if bold else r'C:\Windows\Fonts\segoeui.ttf',
        r'C:\Windows\Fonts\arialbd.ttf' if bold else r'C:\Windows\Fonts\arial.ttf',
    ]
    for c in cands:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


OG_W, OG_H = 1200, 630
og = Image.new('RGBA', (OG_W, OG_H), WARM + (255,))
d = ImageDraw.Draw(og)

# 顶部 navy 条（品牌规范 §66 结构）
d.rectangle([0, 0, OG_W, 8], fill=NAVY)

# 左上：logo lockup
lg_h = 52
lg_w = round(lockup_t.width * lg_h / lockup_t.height)
og.alpha_composite(lockup_t.resize((lg_w, lg_h), Image.LANCZOS), (72, 62))

# 分隔线
d.line([72, 168, OG_W - 72, 168], fill=(221, 227, 230), width=2)

# 主标题
d.text((72, 206), 'Independent hair dryer reviews', font=load_font(44, True), fill=NAVY)
d.text((72, 262), 'for Canadian shoppers.', font=load_font(44, True), fill=NAVY)

# 副标题
d.text((72, 336), 'Tested. Compared. Explained.', font=load_font(26), fill=TEXT2)

# 关键指标（§49 统一单位；§66 一个关键指标）
d.text((72, 408), '8,261 verified Canadian reviews analysed', font=load_font(26, True), fill=NAVY)
d.text((72, 448), 'Median reported failure: 5.5 months', font=load_font(26, True), fill=NAVY)

# 底部域名
d.text((72, OG_H - 74), 'hairdryerlab.ca', font=load_font(22), fill=TEXT2)

# 右侧：mark（占位产品图位置，§66 允许产品图 + logo）
mk_w = 300
mk_h = round(mark_t.height * mk_w / mark_t.width)
og.alpha_composite(mark_t.resize((mk_w, mk_h), Image.LANCZOS),
                   (OG_W - mk_w - 72, (OG_H - mk_h) // 2 + 20))

og.convert('RGB').save(f'{OUT}/og-default.png', optimize=True)
P('')
P('4) OG 图')
P(f'  og-default.png   {OG_W}x{OG_H}   {os.path.getsize(f"{OUT}/og-default.png"):,} bytes')

# ---------- 5) site.webmanifest ----------
manifest = """{
  "name": "Hair Dryer Lab",
  "short_name": "Hair Dryer Lab",
  "description": "Independent hair dryer reviews and comparisons for Canadian shoppers.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#FAFAF8",
  "theme_color": "#183153",
  "icons": [
    { "src": "/brand/favicon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/brand/favicon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
"""
io.open('site/public/site.webmanifest', 'w', encoding='utf-8').write(manifest)
P('')
P('5) site.webmanifest 已写入')

io.open('analysis/_logo_process.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('written analysis/_logo_process.txt')
