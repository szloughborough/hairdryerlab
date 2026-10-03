"""记录 §79 平台裁决（Astro）、§55 完成度、以及 for 页纳入商业页判定。"""
import io
import os
import re

def patch(path, pairs, label):
    if not os.path.exists(path):
        print(f'  !! 不存在 {path}')
        return
    t = io.open(path, encoding='utf-8').read()
    n = 0
    for old, new in pairs:
        if old in t:
            t = t.replace(old, new, 1)
            n += 1
        else:
            print(f'  !! [{label}] 未找到: {old[:70]}')
    if n:
        io.open(path, 'w', encoding='utf-8').write(t)
    print(f'{label}: 改 {n} 处')

# ---- 1. 品牌对照表：§79 裁决 + §55 完成度 ----
patch('deliverables/品牌规范落地对照表.md', [
    ('### ⚠️ 冲突一：§79 指定 WordPress + Astra，本项目用 Astro',
     '### ✅ 冲突一：§79 指定 WordPress + Astra → **已裁决采用 Astro**（2026-10-03 站方确认）'),
    ('| §55 | ✅ 已上线 15/24（原 9 + 本轮接通 6 个孤儿组件）。**仍未建 9 个**：Product Hero、Comparison Table 组件化、Methodology Box、Hair-Type Card、Feature Card、Related Content、Author Box、Newsletter、Image caption |',
     '| §55 | ✅ **24/24 全部上线**。第二批接通：Product Hero、Comparison Table（+ rehype 表格滚动外壳）、Methodology Box、Hair-Type Card、Feature Card、Related Content、Author Box、Newsletter、Image caption |'),
], '品牌对照表')

# ---- 2. 内容结构标准：for 页已纳入商业页 ----
patch('deliverables/内容结构标准.md', [
    ('`isCommercial = best/review/compare/ca` 才渲染',
     '`isCommercial = best/review/compare/ca/for` 才渲染（`for` 于 2026-10-03 补入，理由见下）'),
], '内容结构标准')

print()
print('=== 复查：关键表述是否已更新 ===')
t = io.open('deliverables/品牌规范落地对照表.md', encoding='utf-8').read()
for label, pat in [
    ('§79 已裁决为 Astro', r'已裁决采用 Astro'),
    ('§55 标注 24/24', r'24/24 全部上线'),
]:
    print(f'   {"OK" if re.search(pat, t) else "**缺失**"}  {label}')

t2 = io.open('deliverables/内容结构标准.md', encoding='utf-8').read()
print(f'   {"OK" if "ca/for" in t2 else "**缺失**"}  内容结构标准已含 for 页判定')

# ---- 3. 追加本轮完成记录 ----
P = 'deliverables/品牌规范落地对照表.md'
t = io.open(P, encoding='utf-8').read()
SEC = """

---

## 7. 第二批组件接通（§55 收口至 24/24）

### 7.1 接通方式

| 组件 | 接通方式 | 落地量 |
|---|---|---|
| **Product Hero**（§42(5)） | 布局层渲染 `products[0]` | 25 页 |
| **Comparison Table**（§55(9)） | rehype 插件给全部 markdown 表格套 `.table-scroll` 外壳 + `.cmp-table` 类 | **158 个表格 / 43 页** |
| **Methodology Box**（§55(14)） | 布局层，商业页默认渲染 | 25 页 |
| **Hair-Type Card**（§55(16)） | `/hair-types/` 栏目页 MDX，按发质分组 | 5 张卡 |
| **Feature Card**（§55(17)） | 同一页按**需求**分组 | 6 张卡 |
| **Related Content**（§55(18)） | 布局层；`related` 的 URL 由页面层解析成标题 | **42 页** |
| **Author Box**（§55(19)） | 布局层，替代原单行 byline | 43 页 |
| **Newsletter**（§55(22)） | frontmatter `newsletter: true` 开启 | 1 页 |
| **Image caption**（§55(23)） | 支持「待拍摄」状态 | 1 页 |

### 7.2 两个需要说明的设计决定

**① Newsletter 默认不渲染表单。** 邮件服务未接入前，渲染一个提交不到任何地方的输入框就是假控件。组件内置 `SHOW_FORM = false`，当前显示诚实的「我们还没有邮件列表」说明。接入服务商后需同时更新隐私政策。

**② Image caption 支持「待拍摄」状态。** §62 要求 About 页展示真实测试环境照片，§38 禁止用通用图库照片冒充。我们尚未拍摄，因此把原来读者看不见的 HTML 注释占位改成可见的诚实占位 —— 与 Lab Test Card 的「Not yet tested」是同一套做法。

### 7.3 顺带修掉的三个问题

1. **`isCommercial` 未包含 `for`（发质页）** —— 8 个发质页各有 4–5 条联盟外链，但披露只出现在页脚，违反 §37「页首或正文前」要求。已补入。
2. **markdown 表格没有移动端滚动外壳** —— §33 要求可横向滚动，此前 158 个表格全部裸露。已由 rehype 插件统一包裹。
3. **Dyson 平替篇的 4 条陈旧内部链接** —— 指向改版前的 URL 分类法（`/compare/`、`/learn/`、`/best-hair-dryer/`、`/laifen/`）。这些 URL 写在 frontmatter 的 `related` 里，**此前没有任何组件渲染它们，所以一直隐形**；接通 Related Content 后才暴露。已全量迁移。

### 7.4 §79 平台裁决

**站方确认采用 Astro**，不迁移 WordPress + Astra。裁决依据：§81 的冲突原则（信任 / 清晰 / 准确推荐）平台无关，§79 的实质要求（全局 token、可复用组件、响应式对比表、移动优先、自定义 Lab Test Card）已全部在 Astro 实现，且 §55 的 24 个组件现已 100% 落地。
"""
if '## 7. 第二批组件接通' not in t:
    t = t.rstrip() + '\n' + SEC
    io.open(P, 'w', encoding='utf-8').write(t)
    print('品牌对照表: 已追加第 7 节')
