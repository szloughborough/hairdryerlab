"""
为剩余 9 个 §55 组件追加样式。
用 Python 显式 UTF-8 写入 —— 之前用 PowerShell Add-Content 导致过 GBK 损坏。
类名刻意避开已存在的 .hero / .table-scroll / .pillar-card。
"""
import io
import re

P = 'site/src/styles/global.css'
css = io.open(P, encoding='utf-8').read()

BLOCK = '''
/* ============================================================
   §55 组件库（第二批）—— Product Hero / Comparison Table /
   Methodology Box / Hair-Type Card / Feature Card /
   Related Content / Author Box / Newsletter / Image Caption
   ============================================================ */

/* ---- §42(5) Product Hero ------------------------------------------------
   文章顶部的首选产品块。移动端纵向堆叠，桌面端图左文右。
   §41：首屏 1–1.5 屏内要能看到产品名、一行结论、图、best-for 与价格 CTA。 */
.product-hero {
  display: grid;
  grid-template-columns: 168px minmax(0, 1fr);
  gap: var(--s5);
  align-items: start;
  border: 1px solid var(--hdl-border);
  border-left: 3px solid var(--hdl-navy);
  border-radius: var(--hdl-radius-md);
  background: var(--hdl-white);
  padding: var(--s5);
  margin: var(--s6) 0;
}
.product-hero__media { margin: 0; }
.product-hero__media img { width: 100%; height: auto; border-radius: var(--hdl-radius-sm); display: block; }
.product-hero__eyebrow {
  font-family: 'Manrope', sans-serif; font-size: 12px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--hdl-text-secondary);
  margin: 0 0 var(--s2);
}
.product-hero__name {
  font-family: 'Manrope', sans-serif; font-size: 24px; font-weight: 800;
  color: var(--hdl-navy); margin: 0 0 var(--s2); line-height: 1.2;
}
.product-hero__verdict { font-size: 16px; margin: 0 0 var(--s3); }
.product-hero__facts {
  display: flex; flex-wrap: wrap; gap: var(--s2) var(--s4);
  font-size: 14px; color: var(--hdl-text-secondary); margin: 0 0 var(--s3);
}
.product-hero__facts .num { color: var(--hdl-navy); font-weight: 700; font-family: 'Manrope', sans-serif; }

/* ---- §55(9) Comparison Table -------------------------------------------
   组件渲染用 .cmp-table；markdown 表格由 rehype 插件套上 .table-scroll 外壳。 */
.cmp-table { width: 100%; border-collapse: collapse; font-size: 15px; }
.cmp-table th, .cmp-table td {
  border-bottom: 1px solid var(--hdl-border);
  padding: var(--s3) var(--s3);
  text-align: left;
  vertical-align: top;
}
.cmp-table thead th {
  font-family: 'Manrope', sans-serif; font-weight: 700; color: var(--hdl-navy);
  border-bottom: 2px solid var(--hdl-navy); white-space: nowrap;
}
.cmp-table tbody th { font-weight: 600; color: var(--hdl-text); }
.cmp-table__note { font-size: 13px; color: var(--hdl-text-secondary); margin: var(--s2) 0 0; }
.cmp-table__caption {
  font-family: 'Manrope', sans-serif; font-weight: 700; font-size: 15px;
  color: var(--hdl-navy); margin: 0 0 var(--s3);
}

/* ---- §55(14) Methodology Box -------------------------------------------
   §51：把方法与来源说清楚，与广告内容分开。 */
.method-box {
  border: 1px solid var(--hdl-border);
  border-radius: var(--hdl-radius-md);
  background: var(--hdl-ice);
  padding: var(--s4) var(--s5);
  margin: var(--s6) 0;
  font-size: 15px;
}
.method-box__label {
  font-family: 'Manrope', sans-serif; font-size: 12px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--hdl-navy);
  margin: 0 0 var(--s2);
}
.method-box ul { margin: var(--s2) 0 0; padding-left: var(--s5); }
.method-box li { margin: var(--s1) 0; }
.method-box a { font-weight: 500; }

/* ---- §55(16)(17) Hair-Type Card / Feature Card -------------------------
   §75 视觉优先级：信息优先，不做大色块装饰。 */
.tile-grid {
  display: grid; gap: var(--s4);
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: var(--s5) 0;
}
.tile {
  display: block; text-decoration: none; color: inherit;
  border: 1px solid var(--hdl-border); border-radius: var(--hdl-radius-md);
  background: var(--hdl-white); padding: var(--s4);
  transition: border-color 0.15s ease;
}
.tile:hover { border-color: var(--hdl-navy); }
.tile__media { margin: 0 0 var(--s3); }
.tile__media img { width: 100%; height: auto; border-radius: var(--hdl-radius-sm); display: block; }
.tile__name {
  font-family: 'Manrope', sans-serif; font-size: 17px; font-weight: 700;
  color: var(--hdl-navy); margin: 0 0 var(--s2);
}
.tile__blurb { font-size: 14px; color: var(--hdl-text-secondary); margin: 0; }
.tile--hair { border-top: 3px solid var(--hdl-navy); }
.tile--feature { border-top: 3px solid var(--hdl-ice); }

/* ---- §55(18) Related Content ------------------------------------------- */
.related { border-top: 1px solid var(--hdl-border); margin-top: var(--s8); padding-top: var(--s5); }
.related__title {
  font-family: 'Manrope', sans-serif; font-size: 18px; font-weight: 700;
  color: var(--hdl-navy); margin: 0 0 var(--s4);
}
.related__list { list-style: none; padding: 0; margin: 0; display: grid; gap: var(--s2); }
.related__item { font-size: 16px; }
.related__item a { font-weight: 500; }

/* ---- §55(19) Author Box ------------------------------------------------ */
.authorbox {
  border: 1px solid var(--hdl-border); border-radius: var(--hdl-radius-md);
  background: var(--hdl-white); padding: var(--s5);
  margin: var(--s7) 0 0; font-size: 15px;
}
.authorbox__label {
  font-family: 'Manrope', sans-serif; font-size: 12px; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase; color: var(--hdl-text-secondary);
  margin: 0 0 var(--s2);
}
.authorbox__name {
  font-family: 'Manrope', sans-serif; font-size: 17px; font-weight: 700;
  color: var(--hdl-navy); margin: 0 0 var(--s2);
}
.authorbox__text { margin: 0 0 var(--s2); color: var(--hdl-text-secondary); }
.authorbox__links { margin: 0; font-size: 14px; }
.authorbox__links a { margin-right: var(--s3); }

/* ---- §55(22) Newsletter ------------------------------------------------
   ⚠️ 未接入邮件服务前不渲染表单（否则是个假输入框）。见 Newsletter.astro。 */
.signup {
  border: 1px solid var(--hdl-border); border-radius: var(--hdl-radius-md);
  background: var(--hdl-ice); padding: var(--s5); margin: var(--s7) 0 0;
}
.signup__title {
  font-family: 'Manrope', sans-serif; font-size: 18px; font-weight: 700;
  color: var(--hdl-navy); margin: 0 0 var(--s2);
}
.signup__text { font-size: 15px; margin: 0; color: var(--hdl-text-secondary); }
.signup__form { display: flex; flex-wrap: wrap; gap: var(--s2); margin-top: var(--s4); }
.signup__input {
  flex: 1 1 240px; min-width: 0; padding: var(--s3);
  border: 1px solid var(--hdl-border); border-radius: var(--hdl-radius-sm);
  font: inherit; font-size: 15px; background: var(--hdl-white); color: var(--hdl-text);
}
.signup__note { font-size: 13px; color: var(--hdl-text-secondary); margin: var(--s2) 0 0; }

/* ---- §55(23) Image caption -------------------------------------------- */
.fig { margin: var(--s6) 0; }
.fig img { width: 100%; height: auto; border-radius: var(--hdl-radius-sm); display: block; }
.fig__cap {
  font-size: 13.5px; color: var(--hdl-text-secondary);
  margin: var(--s2) 0 0; line-height: 1.5;
}

/* ---- 移动端折叠（§41 移动优先） ---------------------------------------- */
@media (max-width: 720px) {
  .product-hero { grid-template-columns: 1fr; }
  .product-hero__media { max-width: 200px; }
  .tile-grid { grid-template-columns: 1fr; }
}
@media (min-width: 721px) and (max-width: 1024px) {
  .tile-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
'''

MARK = '§55 组件库（第二批）'
if MARK in css:
    print('已存在第二批组件样式，跳过')
else:
    if not css.endswith('\n'):
        css += '\n'
    css += BLOCK
    io.open(P, 'w', encoding='utf-8', newline='\n').write(css)
    print(f'已追加 {len(BLOCK):,} 字符，文件现为 {len(css):,} 字符')

# 校验编码
raw = io.open(P, 'rb').read()
try:
    raw.decode('utf-8')
    print('编码校验: 合法 UTF-8 ✓')
except UnicodeDecodeError as e:
    print(f'编码校验: **非法字节 @ {e.start}**')
