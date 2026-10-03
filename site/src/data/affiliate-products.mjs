/**
 * 联盟链接 token 注册表 —— Python 同步脚本与 Astro 构建共用同一份数据。
 *
 * ⚠️ 本文件是 .mjs（纯 JavaScript），**不能使用 TypeScript 语法**
 *    （export type / export interface / 类型标注都会导致 Rollup 解析失败：
 *     "Parse failure: Expected '{', got 'type'"）。
 *    类型信息用 JSDoc 表达，见下方 @typedef。
 *
 * 背景：正文与 frontmatter 里写的是字面占位符 `{{affiliate_url_xxx}}`。
 *      这里的 `token` 就是占位符去掉 `{{ }}` 的部分。
 *
 * 字段说明
 *  - asin      : Amazon.ca ASIN，来自 src/data/products.ts（必须与该文件一致）
 *  - providers : 依次尝试的联盟网络。注意这是「尝试顺序」而非最终归属——
 *                同步脚本按顺序查询，第一个成功返回链接的网络胜出，
 *                结果记录在 affiliate-links.mjs 的 provider 字段里。
 *  - defer     : true = 已知尚未接入任何网络，同步脚本不重试，构建时以
 *                pending 占位 URL 渲染。等推广计划通过后把该行删掉即可。
 *
 * 新增产品：在 src/data/products.ts 加产品，然后在这里加一行。
 */

/**
 * @typedef {'levanta' | 'partnerboost' | 'artemis'} ProviderId
 */

/**
 * @typedef {Object} AffiliateProduct
 * @property {string} token
 * @property {string} asin
 * @property {string} label
 * @property {ProviderId[]} providers
 * @property {boolean} [defer]
 */

/** @type {AffiliateProduct[]} */
export const AFFILIATE_PRODUCTS = [
  // ---------------- Laifen（主推品牌）----------------
  {
    token: 'affiliate_url_laifen_air',
    asin: 'B0GWHF4SHD',
    label: 'Laifen Air',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_laifen_se_lite',
    asin: 'B0FKBFZNHK',
    label: 'Laifen SE Lite',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_laifen_air_diffuser',
    asin: 'B0GWHGTBDY',
    label: 'Laifen Air Diffuser',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_laifen_se2',
    asin: 'B0FPMBBG2J',
    label: 'Laifen SE2',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_laifen_swift',
    asin: 'B0D141Q8ZF',
    label: 'Laifen Swift (gen 1)',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_laifen_swift_diffuser',
    asin: 'B0D13MYLJC',
    label: 'Laifen Swift + Diffuser',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },

  // ---------------- Dyson ----------------
  {
    token: 'affiliate_url_dyson_travel',
    asin: 'B0GHZMFY9W',
    label: 'Dyson Supersonic Travel',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_dyson_nural',
    asin: 'B0FHJFTZ57',
    label: 'Dyson Supersonic Nural',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },

  // ---------------- Shark ----------------
  {
    token: 'affiliate_url_shark_speedstyle',
    asin: 'B0DFDQ3THF',
    label: 'Shark SpeedStyle Pro',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },

  // ---------------- dreame / slopehill / wavytalk ----------------
  {
    token: 'affiliate_url_dreame',
    asin: 'B0F8QH8XHV',
    label: 'Dreame Pocket Pro',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_slopehill',
    asin: 'B0C3M9WBQF',
    label: 'Slopehill 1902 Ionic',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_slopehill_brushless',
    asin: 'B08HRQG2M6',
    label: 'Slopehill Brushless',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_slopehill_diffuser',
    asin: 'B0CY4QMMBH',
    label: 'Slopehill Ionic + Diffuser',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_wavytalk',
    asin: 'B09JZ18GLJ',
    label: 'Wavytalk 1875W',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },

  // ---------------- 传统预算品牌 ----------------
  {
    token: 'affiliate_url_conair_318rc',
    asin: 'B0852913V2',
    label: 'Conair 318RC',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_conair_330c',
    asin: 'B0CFQ3R4CQ',
    label: 'Conair 330C Titanium Pro',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },
  {
    token: 'affiliate_url_conair_flomotion',
    asin: 'B0B15P7SDS',
    label: 'Conair InfinitiPro FloMotion Pro',
    providers: ['levanta', 'partnerboost', 'artemis'],
  },

  // ---------------- 旅行 / 其他高销量型号 ----------------
  // 这三个品牌暂未接入任何联盟网络，先标 defer 以免同步脚本反复重试。
  // 接入后删掉 defer 即可。
  {
    token: 'affiliate_url_revlon_travel',
    asin: 'B07NF1CLMQ',
    label: 'Revlon RVDR5034F Travel',
    providers: ['levanta', 'partnerboost', 'artemis'],
    defer: true,
  },
  {
    token: 'affiliate_url_aina',
    asin: 'B0DMWNFZRH',
    label: 'AINA Diffuser Dryer',
    providers: ['levanta', 'partnerboost', 'artemis'],
    defer: true,
  },

  // ---------------- Remington（传统品牌，各 1 个 SKU）----------------
  {
    token: 'affiliate_url_remington_damage',
    asin: 'B0BN2F767S',
    label: 'Remington Damage Protection',
    providers: ['levanta', 'partnerboost', 'artemis'],
    defer: true,
  },
  {
    token: 'affiliate_url_remington_ceramic',
    asin: 'B08DLGCKGK',
    label: 'Remington Ceramic Ionic',
    providers: ['levanta', 'partnerboost', 'artemis'],
    defer: true,
  },
];

/**
 * Amazon Associates 兜底 tag。
 *
 * 这是公开信息（它会出现在每一条 Amazon 链接里），所以直接写在代码里，
 * 而不是只放 .env —— 这样新克隆的仓库不配 .env 也能构建出可点击的链接。
 * 需要覆盖时设环境变量 AMAZON_ASSOCIATE_TAG。
 *
 * 优先级：联盟网络链接优先，拿不到网络链接的商品才用这个 tag。
 * 同一商品绝不叠加两种追踪参数（会同时违反两边的协议）。
 */
export const AMAZON_ASSOCIATE_TAG = 'baldselect06b-20';

/** token → 记录，供快速查找 @type {Record<string, AffiliateProduct>} */
export const TOKEN_INDEX = Object.fromEntries(
  AFFILIATE_PRODUCTS.map((p) => [p.token, p]),
);
