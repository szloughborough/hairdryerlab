"""把 Amazon Associates tag 追加到 .env 与 .env.example（UTF-8 安全写入）。"""
import io, os, re

BLOCK = """
# ---------------------------------------------------------------------------
# 4) Amazon Associates —— 兜底追踪 tag
#
#    这不是 API，只是链接尾部的 tag 参数，因此无需凭据、无需同步脚本。
#    优先级：联盟网络链接优先；网络拿不到的商品才用这个 tag 兜底。
#    同一商品绝不叠加两种追踪参数（会同时违反两边的运营协议）。
#
#    代码里已内置同样的默认值（src/data/affiliate-products.mjs），
#    这里留空 = 用内置默认值；填了 = 覆盖默认值。
# ---------------------------------------------------------------------------
AMAZON_ASSOCIATE_TAG=baldselect06b-20
"""

for path in ('site/.env', 'site/.env.example'):
    if not os.path.exists(path):
        print(f'  {path} 不存在，跳过')
        continue
    t = io.open(path, encoding='utf-8').read()
    if 'AMAZON_ASSOCIATE_TAG' in t:
        print(f'  {path} 已含该配置项，跳过')
        continue
    if not t.endswith('\n'):
        t += '\n'
    io.open(path, 'w', encoding='utf-8', newline='\n').write(t + BLOCK)
    raw = io.open(path, 'rb').read()
    txt = raw.decode('utf-8')
    ok = not any(c in txt for c in '鑱鍑鈥')
    print(f'  {path}  已追加  ·  {len(raw)} 字节  ·  {len(txt.splitlines())} 行  ·  无乱码: {ok}')
