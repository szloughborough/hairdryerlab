"""在品牌对照表里补一节「本轮完成」，并修正 §3 待办中已过期的三条。"""
import io
import re

P = 'deliverables/品牌规范落地对照表.md'
t = io.open(P, encoding='utf-8').read()

# 1) 修正已过期的三条待办
FIX = [
    ('| §55 | 剩余组件：Product Hero、Comparison Table 组件化、Methodology Box、Hair-Type Card、Feature Card、Related Content、Author Box、Newsletter、Image Caption、Evidence Note |',
     '| §55 | ✅ 已上线 15/24（原 9 + 本轮接通 6 个孤儿组件）。**仍未建 9 个**：Product Hero、Comparison Table 组件化、Methodology Box、Hair-Type Card、Feature Card、Related Content、Author Box、Newsletter、Image caption |'),
    ('| §63 | `/how-we-test/` 需扩展为品牌文档列的 13 个章节（当前 8 节） |',
     '| §63 | ✅ 已扩展为 13 个主题章节 + FAQ（共 16 个 H2） |'),
    ('| §42–§45 | 五种页面类型的精确结构需同步进《内容结构标准.md》（布局顺序已在 `Article.astro` 实现） |',
     '| §42–§45 | ✅ 已重写《内容结构标准.md》为 v2.0：5 种类型结构 + 新 URL 分类法 + 品牌要求 vs 实际实现对照表 |'),
    ('| §27 §28 | 发质页（`/hair-types/*`）与需求页（`/best-hair-dryers/*`）尚未创建——首页已链向它们 |',
     '| §27 §28 | ✅ 已完成：8 个发质页 + 6 个榜单页全部上线 |'),
]
n = 0
for old, new in FIX:
    if old in t:
        t = t.replace(old, new, 1)
        n += 1
    else:
        print(f'  !! 未找到: {old[:60]}')

SECTION = """

---

## 6. 本轮完成（组件库 / 方法页 / 内容标准）

### 6.1 §55 组件库：从 9 个在用 → 15 个在用

**接通了 7 个此前「建好但零引用」的孤儿组件。** 接通方式分两类：

| 组件 | 接通方式 | 落地量 |
|---|---|---|
| **Lab Test Card**（§29 标志性组件） | 布局层渲染，frontmatter 可选覆盖；无实测数据时诚实显示 `Not yet tested` | **25 页** |
| **Best For / Skip if**（§6/§32） | 布局层渲染，新增 frontmatter `bestFor` / `skipIf` | **18 页** |
| **CategoryRatings**（§31） | 布局层渲染，新增 frontmatter `ratings`（只写有证据支撑的维度） | **18 页** |
| **Pros / Cons**（§70） | **rehype 插件**在 HAST 层包装，保留 bullet 里的粗体与链接 | **78 处 / 17 页** |
| **Evidence / source note**（§51） | **rehype 插件**把 `*(review analysis)*` 升级为 `.ev` 徽章 | **793 处** |
| **Price Box**（§48） | `ProductPick` 内部改用该组件 | **95 处 / 25 页** |
| **Affiliate CTA**（§35） | `ProductPick` 内部改用该组件 | **96 处 / 26 页** |

**为什么 Pros/Cons 与证据标签走 rehype 而不是改 44 篇 MDX**：这些 bullet 里含 `**粗体**`、`[链接]` 与 `*(证据标注)*`。若改成 `<ProsCons liked={["…"]} />` 字符串数组，markdown 不再被解析，读者会看到字面的星号与方括号。在 HAST 层包装可完整保留内联标记 —— 已验证产物中 `**` 字面残留为 **0**。

**仍未建的 9 个**：Product Hero、Comparison Table（组件化）、Methodology Box、Hair-Type Card、Feature Card、Related Content、Author Box、Newsletter、Image caption。

> `Faq.astro` 亦为孤儿：FAQ 由正文 markdown 渲染 + `JsonLd.astro` 生成 `FAQPage`，检查器已验证 DOM 与 schema 逐字一致，功能要求已满足。

### 6.2 §63 `/how-we-test/`：8 节 → 13 节

按品牌文档补齐：Why we test · Products we test · How sourced · Test environment · Drying-speed test · Noise test · Weight test · Heat test · Real-world use · Hair-type feedback · Price/value methodology · Affiliate independence · Update policy。

**5–8 章（干发/噪音/重量/温度）每章首句都是显式未测声明**，随后只给将要执行的协议（距离、时长、重复次数、单位）。全文 `*(Measured)*` 标注为 **0 处** —— 没有任何编造的实测值。

### 6.3 《内容结构标准.md》→ v2.0

- 按品牌 §42–§45 重写 5 种页面结构
- URL 分类法改为站点实际值（`/best-hair-dryers/` · `/reviews/` · `/comparisons/` · `/hair-types/` · `/guides/`）
- 新增「品牌要求 → 实际实现 → 差异 → 差异原因」对照表
- 保留强制的八维评测标准
- **把「方案 B：价格用约数」写进文档**，避免以后又写精确价

### 6.4 顺带修掉的合规缺口

**8 个发质页（`for`）此前披露只出现在页脚。** 它们各有 4–5 条联盟外链，而 `isCommercial` 未包含 `for`，导致 §37 要求的「页首或正文前」披露缺失 —— 页脚披露属弱合规。已把 `for` 纳入商业页判定，现在**全站含外链的页面披露缺失数为 0**。
"""

if '## 6. 本轮完成' not in t:
    t = t.rstrip() + '\n' + SECTION
    n += 1

io.open(P, 'w', encoding='utf-8').write(t)
print(f'品牌对照表更新 {n} 处')
