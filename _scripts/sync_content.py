"""
把 deliverables/drafts 的 MDX 同步到 site/src/content/ 对应集合目录。

规则：
  - 去掉正文里的 `# H1` 行（H1 由 Astro 布局从 frontmatter 渲染，保证全站只有一个 H1）
  - 依据 frontmatter 的 type 字段决定放入哪个集合目录：
      best -> best/ , review -> review/ , compare -> compare/ ,
      for -> for/ , learn -> learn/ , ca -> ca/
用法：python _scripts/sync_content.py
"""
import io, os, re, sys

SRC_DIR = 'deliverables/drafts'
SITE = 'site/src/content'

TYPE_TO_DIR = {
    'best': 'best', 'review': 'review', 'compare': 'compare',
    'for': 'for', 'learn': 'learn', 'ca': 'ca',
}

def demote_h1(text: str) -> str:
    """删除正文中第一处 `# ` 开头的一级标题行（保留 frontmatter 不变）"""
    m = re.match(r'(?s)^(---\n.*?\n---\n)(.*)$', text)
    if not m:
        return text
    fm, body = m.group(1), m.group(2)
    body = re.sub(r'(?m)^#\s+.*\n', '', body, count=1)
    body = body.lstrip('\n')
    return fm + '\n' + body


def mdx_comments(text: str) -> str:
    """
    MDX 不支持 HTML 注释 `<!-- -->`，必须写成 `{/* */}`。
    在 frontmatter 之后把 HTML 注释块统一转换，避免编译报错。
    """
    m = re.match(r'(?s)^(---\n.*?\n---\n)(.*)$', text)
    if not m:
        return text
    fm, body = m.group(1), m.group(2)
    body = re.sub(r'<!--(.*?)-->', lambda mm: '{/*' + mm.group(1) + '*/}', body, flags=re.S)
    return fm + '\n' + body

def main():
    if not os.path.isdir(SRC_DIR):
        print('no drafts dir'); return

    # 先清空集合目录里的 .mdx（保留 .gitkeep），避免 slug 改名后旧文件残留在站点造成重复页面
    for sub in set(TYPE_TO_DIR.values()):
        d = os.path.join(SITE, sub)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith('.mdx'):
                os.remove(os.path.join(d, fn))

    n = 0
    for fn in sorted(os.listdir(SRC_DIR)):
        if not fn.endswith('.mdx'):
            continue
        p = os.path.join(SRC_DIR, fn)
        text = io.open(p, encoding='utf-8').read()
        # 跳过草稿（draft: true）—— 它们不在站点发布范围内，且可能与正式版同 slug 冲突
        if re.search(r'(?m)^draft:\s*true\s*$', text):
            print(f'  skip (draft: true): {fn}'); continue
        tm = re.search(r'(?m)^type:\s*(\w+)', text)
        if not tm:
            print(f'  skip (no type): {fn}'); continue
        t = tm.group(1)
        sub = TYPE_TO_DIR.get(t)
        if not sub:
            print(f'  skip (unknown type "{t}"): {fn}'); continue
        slug = re.search(r'(?m)^slug:\s*"?([\w-]+)"?', text)
        slug = slug.group(1) if slug else os.path.splitext(fn)[0]
        out_dir = os.path.join(SITE, sub)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, slug + '.mdx')
        io.open(out, 'w', encoding='utf-8').write(mdx_comments(demote_h1(text)))
        print(f'  {fn}  ->  {out}')
        n += 1
    print(f'synced {n} file(s)')

if __name__ == '__main__':
    main()
