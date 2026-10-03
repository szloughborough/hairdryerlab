import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * 全站统一 frontmatter schema。
 * 6 个内容集合与《技术SEO与信息架构规划.md》的 6 个 Pillar 一一对应。
 */
const productSchema = z.object({
  name: z.string(),
  brand: z.string(),
  priceCAD: z.number(),
  rating: z.number(),
  ratingCount: z.number(),
  asin: z.string(),
  image: z.string().optional(),
  affiliateUrl: z.string(),
});

const faqSchema = z.object({
  q: z.string(),
  a: z.string(),
});

/**
 * YAML 会把不带引号的 2026-10-05 解析成 Date 对象，
 * 因此这里统一归一化为 'YYYY-MM-DD' 字符串。
 */
const dateLike = z
  .union([z.string(), z.date()])
  .transform((v) => (v instanceof Date ? v.toISOString().slice(0, 10) : v));

const base = {
  title: z.string(),
  h1: z.string(),
  description: z.string(),
  /** §42(3) 一行结论，出现在 H1 正下方 */
  verdict: z.string().optional(),
  /** §61 编辑元数据：测试日期 */
  tested: z.string().optional(),
  /** §61 编辑元数据：产品获得方式，如 "Review sample supplied by Laifen" */
  source: z.string().optional(),
  slug: z.string(),
  primaryKeyword: z.string(),
  secondaryKeywords: z.array(z.string()).default([]),
  intent: z.enum(['commercial', 'informational', 'transactional', 'comparison', 'navigational']),
  priority: z.number().min(1).max(3).default(2),
  schema: z.enum(['ItemList', 'Product', 'Review', 'Article', 'FAQPage', 'HowTo', 'WebPage']),
  author: z.string(),
  published: dateLike,
  updated: dateLike,
  /**
   * 可选：显式指定完整路由（不含首尾斜杠），用于不遵循集合前缀的页面。
   * 例：how-we-test 按品牌规范 §54 位于根级 → route: "how-we-test"
   * 未提供时，路由 = COLLECTION_PREFIX[集合] + slug（见 src/data/site.ts）
   */
  route: z.string().optional(),
  /** 可选：canonical 由布局按最终路由自动生成，此处仅作覆盖用途 */
  canonical: z.string().optional(),
  draft: z.boolean().default(false),
  related: z.array(z.string()).default([]),
  products: z.array(productSchema).optional(),
  faq: z.array(faqSchema).default([]),

  // ---- §55 组件库的可选 frontmatter 驱动字段（加了就能被布局渲染） ----
  /** §6/§30/§32 Best for / Skip if —— 替代「Overall Winner」，页级 */
  bestFor: z.string().optional(),
  skipIf: z.string().optional(),
  /** §31 分类结论 —— 替代数字总分（禁止 9.4/10、94%） */
  ratings: z
    .array(
      z.object({
        label: z.string(),
        grade: z.string(),
        measured: z.string().optional(),
      }),
    )
    .optional(),
  /** §29 Lab Test Card —— 缺省时布局渲染「尚未实测」状态 */
  labTest: z
    .object({
      product: z.string().optional(),
      metrics: z
        .array(z.object({ label: z.string(), value: z.string(), unit: z.string().optional() }))
        .optional(),
      tested: z.string().optional(),
    })
    .optional(),
  /** §55(22) 是否在页尾渲染 Newsletter 区块（默认关闭，理由见 Newsletter.astro） */
  newsletter: z.boolean().default(false),
};

const make = (baseDir) =>
  defineCollection({
    loader: glob({ pattern: '**/*.mdx', base: baseDir }),
    schema: z.object(base),
  });

export const collections = {
  best: make('./src/content/best'),
  review: make('./src/content/review'),
  compare: make('./src/content/compare'),
  for: make('./src/content/for'),
  learn: make('./src/content/learn'),
  ca: make('./src/content/ca'),
};
