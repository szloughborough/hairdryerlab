"""
一次性迁移：把草稿的 frontmatter 与内链对齐《品牌规范 v1.0》§54 的 URL 体系。
可重复执行（幂等）。

变更：
  1. best-dyson-alternatives-LAUNCH.mdx
     - slug: best-dyson-alternatives -> dyson-alternatives   （URL 变为 /best-hair-dryers/dyson-alternatives/）
     - 新增 verdict / tested / source（§42(3) §61）
     - 删除 canonical（改由布局按最终路由生成，避免漂移）
     - 内链 /best-dyson-alternatives/ -> /best-hair-dryers/dyson-alternatives/
  2. how-we-test.mdx
     - 新增 route: how-we-test（§54 中该页位于根级，不走 /guides/ 前缀）
     - 新增 verdict
     - 删除 canonical
  3. 两个文件的内链统一改为品牌规范的前缀体系
     /best-hair-dryer/            -> /best-hair-dryers/
     /laifen-vs-dyson/            -> /comparisons/laifen-vs-dyson/
     /for/travel-hair-dryer/      -> /hair-types/travel-hair-dryer/
     /ca/where-to-buy-laifen-canada/ -> /best-hair-dryers/where-to-buy-laifen-canada/
     /ca/hair-dryer-sale-canada/  -> /best-hair-dryers/hair-dryer-sale-canada/
     /learn/how-long-...          -> /guides/how-long-...
"""
import io, os, re

DRAFTS = 'deliverables/drafts'

LINK_MAP = [
    (r'/best-dyson-alternatives/', '/best-hair-dryers/dyson-alternatives/'),
    (r'/best-hair-dryer/(?!s)', '/best-hair-dryers/'),
    (r'/laifen-vs-dyson/', '/comparisons/laifen-vs-dyson/'),
    (r'/for/travel-hair-dryer/', '/hair-types/travel-hair-dryer/'),
    (r'/for/quiet-hair-dryer/', '/hair-types/quiet-hair-dryer/'),
    (r'/ca/where-to-buy-laifen-canada/', '/best-hair-dryers/where-to-buy-laifen-canada/'),
    (r'/ca/hair-dryer-sale-canada/', '/best-hair-dryers/hair-dryer-sale-canada/'),
    (r'/learn/', '/guides/'),
    (r'/reviews/laifen-air/', '/reviews/laifen/air/'),
    (r'/reviews/laifen-se2/', '/reviews/laifen/se2/'),
]

def set_field(fm: str, key: str, value: str) -> str:
    """新增或替换 frontmatter 顶层字段（单行）"""
    if re.search(rf'(?m)^{key}:', fm):
        return re.sub(rf'(?m)^{key}:.*$', f'{key}: {value}', fm)
    # 插到 description 之后，保持可读
    m = re.search(r'(?m)^description:.*$', fm)
    if m:
        return fm[:m.end()] + f'\n{key}: {value}' + fm[m.end():]
    return fm + f'\n{key}: {value}'

def drop_field(fm: str, key: str) -> str:
    return re.sub(rf'(?m)^{key}:.*\n?', '', fm)

def migrate(fn: str, is_launch: bool):
    p = os.path.join(DRAFTS, fn)
    if not os.path.exists(p):
        print(f'  skip (missing): {fn}'); return
    text = io.open(p, encoding='utf-8').read()
    m = re.match(r'(?s)^(---\n)(.*?)(\n---\n)(.*)$', text)
    if not m:
        print(f'  skip (no frontmatter): {fn}'); return
    open_d, fm, close_d, body = m.groups()

    # frontmatter
    fm = drop_field(fm, 'canonical')
    if is_launch:
        fm = re.sub(r'(?m)^slug:.*$', 'slug: dyson-alternatives', fm)
        fm = set_field(fm, 'verdict',
                       '"A cheaper Dyson alternative is only worth it if it lasts — here are the five that survive real Canadian use."')
        fm = set_field(fm, 'tested', '"Not yet bench-tested"')
        fm = set_field(fm, 'source', '"Analysis of 8,261 verified Amazon.ca reviews"')
    else:
        fm = set_field(fm, 'route', 'how-we-test')
        fm = set_field(fm, 'verdict',
                       '"Our guides are built from coded analysis of thousands of Canadian reviews — and we state plainly what we have not tested yet."')

    # 内链
    for pat, rep in LINK_MAP:
        body = re.sub(pat, rep, body)

    io.open(p, 'w', encoding='utf-8').write(open_d + fm.strip() + close_d + body)
    print(f'  migrated: {fn}')

print('migrating drafts to brand URL taxonomy...')
migrate('best-dyson-alternatives-LAUNCH.mdx', is_launch=True)
migrate('how-we-test.mdx', is_launch=False)

# 清理旧的 canonical 残留说明
print('\ndone. 现在重新运行 sync_content.py 同步到站点。')
