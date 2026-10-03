/** 站点级配置 —— 严格遵循《品牌规范-HairDryerLab-v1.0.md》§22 / §24 / §54 */

export const SITE_URL = 'https://hairdryerlab.ca';
export const SITE_NAME = 'Hair Dryer Lab';
/** §3 / §80 */
export const SITE_TAGLINE = 'Tested. Compared. Explained.';
export const SITE_POSITIONING = 'Find the right hair dryer. Based on testing, not hype.';
export const SITE_DESCRIPTION =
  'Independent hair dryer reviews and comparisons for Canadian shoppers.';
/** 首页 meta description（§SEO 150–160 字符；可见文案仍用 SITE_DESCRIPTION） */
export const SITE_META_DESCRIPTION =
  'Independent hair dryer reviews, comparisons and buying guides for Canadian shoppers. Built from thousands of verified Canadian reviews.';

/** §3 主品牌陈述 */
export const BRAND_STATEMENT =
  'Independent hair dryer reviews, comparisons and real-world testing for Canadian shoppers.';

/**
 * §22 Header 导航
 * 明确不包含 Home / Blog / Shop / Deals / News。
 */
export const NAV = [
  { label: 'Best Hair Dryers', href: '/best-hair-dryers/' },
  { label: 'Reviews', href: '/reviews/' },
  { label: 'Comparisons', href: '/comparisons/' },
  { label: 'Hair Types', href: '/hair-types/' },
  { label: 'Guides', href: '/guides/' },
  { label: 'How We Test', href: '/how-we-test/' },
];

/** §24 Footer — Main Navigation */
export const FOOTER_MAIN = [
  { label: 'Best Hair Dryers', href: '/best-hair-dryers/' },
  { label: 'Reviews', href: '/reviews/' },
  { label: 'Comparisons', href: '/comparisons/' },
  { label: 'Hair Types', href: '/hair-types/' },
  { label: 'Guides', href: '/guides/' },
  { label: 'How We Test', href: '/how-we-test/' },
];

/** §24 Footer — Company */
export const FOOTER_COMPANY = [
  { label: 'About', href: '/about/' },
  { label: 'Contact', href: '/contact/' },
  { label: 'Editorial Policy', href: '/editorial-policy/' },
  { label: 'Affiliate Disclosure', href: '/affiliate-disclosure/' },
  { label: 'Privacy Policy', href: '/privacy-policy/' },
  { label: 'Terms', href: '/terms/' },
];

/** §24 Canada 行（品牌文档指定文案） */
export const FOOTER_CANADA_LINE =
  'Independent hair dryer reviews and buying advice for Canadian shoppers.';

/**
 * §54 核心导航分类法 —— 集合 → URL 前缀
 * 页面最终 URL = {prefix}{slug}/（除非 frontmatter 用 route 显式覆盖，例如 /how-we-test/）
 */
export const COLLECTION_PREFIX: Record<string, string> = {
  best: '/best-hair-dryers/',
  review: '/reviews/',
  compare: '/comparisons/',
  for: '/hair-types/',
  learn: '/guides/',
  ca: '/best-hair-dryers/', // 加拿大购买类内容归入购买决策集群
};

/** 面包屑父级（集合 → Pillar） */
export const PILLAR: Record<string, { label: string; href: string }> = {
  best: { label: 'Best Hair Dryers', href: '/best-hair-dryers/' },
  review: { label: 'Reviews', href: '/reviews/' },
  compare: { label: 'Comparisons', href: '/comparisons/' },
  for: { label: 'Hair Types', href: '/hair-types/' },
  learn: { label: 'Guides', href: '/guides/' },
  ca: { label: 'Best Hair Dryers', href: '/best-hair-dryers/' },
};

/** §37 联盟披露标准文案（不得改写） */
export const DISCLOSURE_COPY =
  "Hair Dryer Lab may earn a commission when you buy through our links. This doesn't affect how we test or review products.";

/** §49 统一计量单位（全站必须一致） */
export const UNITS = {
  drying: 'min:sec',
  noise: 'dB @ 1 m',
  weight: 'g',
  temperature: '°C',
  cord: 'm',
  power: 'W',
} as const;

/** §31 分类结论用词（禁止数字总分） */
export const GRADE_SCALE = ['Excellent', 'Very Good', 'Good', 'Fair', 'Limited'] as const;

/**
 * 第三方脚本与站点验证 —— 单一数据源，改这里即全站生效。
 *
 * ⚠️ 合规要点（改这项前务必读）：
 *   1. **这里列出的每一项都必须在 `/privacy-policy/` 与 `/affiliate-disclosure/` 如实披露。**
 *      尤其是 Microsoft Clarity —— 它不只统计，而是**录制会话回放与热图**，
 *      属于比分析工具更侵入的一类，披露要求更高。
 *   2. 新增或移除工具后，必须同步更新 LEGAL.analytics 数组与 Privacy Policy 正文。
 *   3. 本地 dev 默认不加载，避免污染统计数据。
 */
export const ANALYTICS = {
  /** GA4 衡量 ID（gtag.js）—— 会写 cookie */
  ga4: 'G-FGWTDV59DY',
  /** Microsoft Clarity 项目 ID —— 会话回放 / 热图，比 GA4 更侵入 */
  clarity: 'yrs10sr6pg',
  /** Google Search Console 站点验证 */
  googleSiteVerification: 'ViysjFF_EJFI-6tPem4t39Q_qTNZi9Iouy36BeNhGpI',
  /** Bing Webmaster Tools 站点验证 */
  bingVerification: 'DBDA9C5B702CB4727F1CFE5872FFA081',
} as const;

/**
 * 法律与信任页配置（Privacy / Terms / Contact / About / Editorial Policy 共用）
 * 单一数据源，改这里即全站生效。
 *
 * ⚠️ 上线前必须确认：
 *   1. contactEmail 对应的邮箱**已在域名邮箱服务商处创建**，否则页面上是死地址
 *   2. operatorName 若日后改为注册实体，需同步更新 Terms / Privacy
 *   3. analytics 数组必须与 ANALYTICS 实际加载的工具一致（漏一个就是虚假披露）
 * 另：公开页面**不得出现联盟平台内部名称**（如 Levanta），只写面向消费者的零售商与品牌。
 */
export const LEGAL = {
  /** 公开运营方署名 */
  operatorName: 'Hair Dryer Lab',
  /** 公开联系邮箱（须真实可达） */
  contactEmail: 'editorial@hairdryerlab.ca',
  /** 适用法律（仅确认到国家层级，不臆造省份） */
  jurisdiction: 'Canada',
  /** 网站域名 */
  domain: 'hairdryerlab.ca',
  /** 条款生效日期 */
  effectiveDate: '2026-10-05',
  /**
   * 实际加载的分析/追踪工具（Privacy Policy 必须如实列出）。
   * 与 ANALYTICS 保持一致：GA4 会写 cookie；Clarity 会做会话回放。
   */
  analytics: ['Google Analytics 4', 'Microsoft Clarity'],
  /** 面向消费者的联盟跳转目标（不列内部平台名） */
  affiliateRetailers: ['Amazon.ca'],
  /** 联盟合作的品牌（已在正文中出现的品牌名，可公开） */
  affiliateBrands: ['Laifen', 'Dreame', 'Slopehill'],
  /** 内容更新承诺 */
  updateCadence: 'monthly',
} as const;
