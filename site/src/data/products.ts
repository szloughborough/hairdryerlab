/**
 * 产品数据 —— 单一数据源。
 *
 * 来源：SellerSprite BSR 导出（Amazon.ca Hair Dryers 类目，核对日期 2026-10-02）
 * 所有文章 frontmatter 的 `products` 与图片都以本文件为准，改这里即可全站生效。
 *
 * ⚠️ 图片合规（上线前必须决策，详见 README §7）
 *  - 当前 image 指向 Amazon 商品主图。
 *  - Amazon Associates 对商品图有有限授权；严格做法是走 Product Advertising API。
 *  - 不要直接使用品牌官网图片（版权归品牌，通常未授权第三方转载）。
 *  - 长期最优解：自费购买后自拍实拍图（零风险，且是无法复制的护城河）。
 */

/** 全站价格/评分核对日期（所有商业页必须显示） */
export const PRICE_CHECKED = '2026-10-02';

/**
 * 展示用「约数价格」（方案 B）。
 *
 * 为什么不用精确价：Amazon Associates 运营协议要求，页面上展示的 Amazon 商品价格
 * 必须是**当前的**（通常需 PA-API 实时获取），否则不应展示。我们持有的是自己采集的
 * 历史观察值，因此对外一律展示约数，精确值只留在 frontmatter 里供内部比较。
 *
 * 口径（与 _scripts/plan_b_prices.py 保持一致）：
 *   < 100 取整 · 100–299 取 5 · 300 以上取 10
 */
export function approxPrice(n: number): string {
  const r =
    n < 100 ? Math.round(n) : n < 300 ? Math.round(n / 5) * 5 : Math.round(n / 10) * 10;
  return `about C$${r}`;
}

/** 价格展示的统一说明：约数 + 核对日期 + 指向零售商实时价 */
export const PRICE_NOTE =
  'Prices shown are approximate figures from our own research, not live retailer pricing. ' +
  'Check the current price on the retailer page before buying.';

export interface ProductRecord {
  asin: string;
  brand: string;
  /** 产品线名称（用于正文与 alt） */
  line: string;
  priceCAD: number;
  rating: number;
  ratingCount: number;
  /** Amazon.ca 估算月销量（SellerSprite） */
  unitsMonth: number;
  /** 细分小类 BSR */
  bsr: number;
  daysOnline: number;
  /** 同 ASIN 卖家数（1 = 品牌自控，Buy Box 稳定） */
  sellers: number;
  buyBox: string;
  image: string;
  imageAlt: string;
}

export const PRODUCTS: Record<string, ProductRecord> = {
  // ---------------- Laifen（主推品牌，Buy Box 全部自控）----------------
  B0GWHF4SHD: {
    asin: 'B0GWHF4SHD', brand: 'Laifen', line: 'Laifen Air',
    priceCAD: 99.99, rating: 4.5, ratingCount: 278, unitsMonth: 534, bsr: 25,
    daysOnline: 126, sellers: 1, buyBox: 'Laifen Official',
    image: 'https://m.media-amazon.com/images/I/31Nr35JXX7L._AC_US600_.jpg',
    imageAlt: 'Laifen Air high-speed ionic hair dryer in pink',
  },
  B0FKBFZNHK: {
    asin: 'B0FKBFZNHK', brand: 'Laifen', line: 'Laifen SE Lite',
    priceCAD: 109.99, rating: 4.5, ratingCount: 550, unitsMonth: 448, bsr: 7,
    daysOnline: 408, sellers: 1, buyBox: 'Laifen Official',
    image: 'https://images-na.ssl-images-amazon.com/images/I/61sVMjRFaUL._AC_US600_.jpg',
    imageAlt: 'Laifen SE Lite ionic hair dryer with diffuser in milk tea colour',
  },
  B0GWHGTBDY: {
    asin: 'B0GWHGTBDY', brand: 'Laifen', line: 'Laifen Air Diffuser',
    priceCAD: 99.99, rating: 4.6, ratingCount: 379, unitsMonth: 377, bsr: 16,
    daysOnline: 122, sellers: 1, buyBox: 'Laifen Official',
    image: 'https://images-na.ssl-images-amazon.com/images/I/51c-rKLj81L._AC_US600_.jpg',
    imageAlt: 'Laifen Air Diffuser travel hair dryer in milk tea colour',
  },
  B0FPMBBG2J: {
    asin: 'B0FPMBBG2J', brand: 'Laifen', line: 'Laifen SE2',
    priceCAD: 143.98, rating: 4.5, ratingCount: 189, unitsMonth: 319, bsr: 17,
    daysOnline: 348, sellers: 2, buyBox: 'Laifen Official',
    image: 'https://m.media-amazon.com/images/I/31XSIqtJQ+L._AC_US600_.jpg',
    imageAlt: 'Laifen SE2 high-speed hair dryer with diffuser in white',
  },
  B0D141Q8ZF: {
    asin: 'B0D141Q8ZF', brand: 'Laifen', line: 'Laifen Swift (gen 1)',
    priceCAD: 149.98, rating: 4.1, ratingCount: 442, unitsMonth: 113, bsr: 39,
    daysOnline: 703, sellers: 1, buyBox: 'Laifen Official',
    image: 'https://m.media-amazon.com/images/I/21hmTJO91UL._AC_US600_.jpg',
    imageAlt: 'Laifen Swift professional high-speed hair dryer in black',
  },
  B0D13MYLJC: {
    asin: 'B0D13MYLJC', brand: 'Laifen', line: 'Laifen Swift + Diffuser',
    priceCAD: 219.99, rating: 4.5, ratingCount: 104, unitsMonth: 179, bsr: 54,
    daysOnline: 905, sellers: 1, buyBox: 'Laifen Official',
    image: 'https://m.media-amazon.com/images/I/318faSLIFeL._AC_US600_.jpg',
    imageAlt: 'Laifen Swift hair dryer with diffuser in black',
  },

  // ---------------- Dyson（流量品牌，价格锚点）----------------
  B0GHZMFY9W: {
    asin: 'B0GHZMFY9W', brand: 'Dyson', line: 'Dyson Supersonic Travel',
    priceCAD: 399.99, rating: 4.4, ratingCount: 310, unitsMonth: 234, bsr: 34,
    daysOnline: 198, sellers: 1, buyBox: 'Dyson',
    image: 'https://m.media-amazon.com/images/I/21xKwL1kaCL._SX600_SY600_CR,0,0,600,600_.jpg',
    imageAlt: 'Dyson Supersonic Travel hair dryer in ceramic pink and rose gold',
  },
  B0FHJFTZ57: {
    asin: 'B0FHJFTZ57', brand: 'Dyson', line: 'Dyson Supersonic Nural',
    priceCAD: 629.99, rating: 4.5, ratingCount: 125, unitsMonth: 182, bsr: 36,
    daysOnline: 377, sellers: 1, buyBox: 'Dyson',
    image: 'https://m.media-amazon.com/images/I/31h2pGOqiAL._AC_US600_.jpg',
    imageAlt: 'Dyson Supersonic Nural hair dryer in amber silk special edition',
  },

  // ---------------- Shark（高速吹风机，高客单）----------------
  B0DFDQ3THF: {
    asin: 'B0DFDQ3THF', brand: 'Shark', line: 'Shark SpeedStyle Pro',
    priceCAD: 199.99, rating: 4.4, ratingCount: 64, unitsMonth: 288, bsr: 13,
    daysOnline: 743, sellers: 2, buyBox: 'Shark',
    image: 'https://images-na.ssl-images-amazon.com/images/I/51LP6S9RJ9L._AC_US600_.jpg',
    imageAlt: 'Shark SpeedStyle Pro high-velocity hair dryer system, straight and wavy',
  },

  // ---------------- dreame / slopehill / wavytalk ----------------
  B0F8QH8XHV: {
    asin: 'B0F8QH8XHV', brand: 'dreame', line: 'Dreame Pocket Pro',
    priceCAD: 159.99, rating: 4.6, ratingCount: 252, unitsMonth: 163, bsr: 52,
    daysOnline: 443, sellers: 1, buyBox: 'Dreame Technology HK',
    image: 'https://m.media-amazon.com/images/I/41TFuIwjFiL._AC_US600_.jpg',
    imageAlt: 'Dreame Pocket Pro dual-voltage travel hair dryer with diffuser',
  },
  B0C3M9WBQF: {
    asin: 'B0C3M9WBQF', brand: 'slopehill', line: 'Slopehill 1902 Ionic',
    priceCAD: 42.99, rating: 4.5, ratingCount: 22195, unitsMonth: 8660, bsr: 1,
    daysOnline: 1153, sellers: 3, buyBox: 'Stellartech (third party)',
    image: 'https://m.media-amazon.com/images/I/41v5yqhOsNL._AC_US600_.jpg',
    imageAlt: 'Slopehill Professional Ionic 1800W hair dryer in black with concentrator nozzles and diffuser',
  },
  B08HRQG2M6: {
    asin: 'B08HRQG2M6', brand: 'slopehill', line: 'Slopehill Brushless',
    priceCAD: 79.99, rating: 4.6, ratingCount: 6087, unitsMonth: 835, bsr: 11,
    daysOnline: 2085, sellers: 5, buyBox: 'Poweriseca (third party)',
    image: 'https://images-na.ssl-images-amazon.com/images/I/71RRkmjGoEL._AC_US600_.jpg',
    imageAlt: 'Slopehill brushless motor hair dryer with LED display in grey',
  },
  B0CY4QMMBH: {
    asin: 'B0CY4QMMBH', brand: 'slopehill', line: 'Slopehill Ionic + Diffuser',
    priceCAD: 99.99, rating: 4.6, ratingCount: 1809, unitsMonth: 557, bsr: 12,
    daysOnline: 897, sellers: 2, buyBox: 'Muxuexue (third party)',
    image: 'https://m.media-amazon.com/images/I/41ZVjpENpKL._AC_US600_.jpg',
    imageAlt: 'Slopehill Professional Ionic hair dryer with diffuser',
  },
  B09JZ18GLJ: {
    asin: 'B09JZ18GLJ', brand: 'wavytalk', line: 'Wavytalk 1875W',
    priceCAD: 39.99, rating: 4.3, ratingCount: 32950, unitsMonth: 2948, bsr: 3,
    daysOnline: 1716, sellers: 1, buyBox: 'wavytalk CA',
    image: 'https://images-na.ssl-images-amazon.com/images/I/61K2CN-F2iL._AC_US600_.jpg',
    imageAlt: 'Wavytalk 1875W ionic hair dryer with diffuser and three attachments',
  },

  // ---------------- 传统预算品牌（流量词覆盖）----------------
  B0852913V2: {
    asin: 'B0852913V2', brand: 'Conair', line: 'Conair 318RC',
    priceCAD: 24.97, rating: 4.4, ratingCount: 9491, unitsMonth: 1957, bsr: 4,
    daysOnline: 2368, sellers: 3, buyBox: 'Amazon',
    image: 'https://images-na.ssl-images-amazon.com/images/I/51k2g057h5L._AC_US600_.jpg',
    imageAlt: 'Conair 318RC 1875W mid-size hair dryer in blue',
  },
  B0CFQ3R4CQ: {
    asin: 'B0CFQ3R4CQ', brand: 'Conair', line: 'Conair 330C Titanium Pro',
    priceCAD: 39.97, rating: 4.5, ratingCount: 518, unitsMonth: 1196, bsr: 10,
    daysOnline: 1132, sellers: 2, buyBox: 'Amazon',
    image: 'https://images-na.ssl-images-amazon.com/images/I/413UbvFqxSL._AC_US600_.jpg',
    imageAlt: 'Conair 330C Titanium Pro 1875W hair dryer with concentrator and diffuser',
  },
  B0B15P7SDS: {
    asin: 'B0B15P7SDS', brand: 'Conair', line: 'InfinitiPro FloMotion Pro',
    priceCAD: 60.60, rating: 4.5, ratingCount: 1079, unitsMonth: 1081, bsr: 14,
    daysOnline: 1500, sellers: 3, buyBox: 'Amazon',
    image: 'https://m.media-amazon.com/images/I/31VRnkeS1ML._AC_US600_.jpg',
    imageAlt: 'InfinitiPro by Conair FloMotion Pro hair dryer with diffuser',
  },
  B07NF1CLMQ: {
    asin: 'B07NF1CLMQ', brand: 'Revlon', line: 'Revlon RVDR5034F',
    priceCAD: 18.99, rating: 4.4, ratingCount: 3491, unitsMonth: 3106, bsr: 5,
    daysOnline: 2755, sellers: 2, buyBox: 'Amazon',
    image: 'https://images-na.ssl-images-amazon.com/images/I/61prMMOC-QL._AC_US600_.jpg',
    imageAlt: 'Revlon RVDR5034F compact travel hair dryer in black',
  },
  B0DMWNFZRH: {
    asin: 'B0DMWNFZRH', brand: 'Aina', line: 'AINA Diffuser Dryer',
    priceCAD: 25.99, rating: 4.4, ratingCount: 3887, unitsMonth: 3030, bsr: 2,
    daysOnline: 592, sellers: 1, buyBox: 'Aina Canada Official Store',
    image: 'https://m.media-amazon.com/images/I/41bFvHSw1cL._AC_US600_.jpg',
    imageAlt: 'AINA 1600W diffuser hair dryer in Vader black',
  },
  B0BN2F767S: {
    asin: 'B0BN2F767S', brand: 'Remington', line: 'Remington Damage Protection',
    priceCAD: 25.65, rating: 4.5, ratingCount: 806, unitsMonth: 536, bsr: 6,
    daysOnline: 1379, sellers: 1, buyBox: 'Amazon',
    image: 'https://images-na.ssl-images-amazon.com/images/I/81nzbBp2pkL._AC_US600_.jpg',
    imageAlt: 'Remington damage protection 1875W hair dryer in purple',
  },
  B08DLGCKGK: {
    asin: 'B08DLGCKGK', brand: 'Remington', line: 'Remington Ceramic Ionic',
    priceCAD: 28.49, rating: 4.4, ratingCount: 48228, unitsMonth: 319, bsr: 9,
    daysOnline: 1959, sellers: 1, buyBox: 'Amazon',
    image: 'https://images-na.ssl-images-amazon.com/images/I/711ugJ+ad4L._AC_US600_.jpg',
    imageAlt: 'Remington damage protection ceramic ionic hair dryer',
  },
};

/** 兼容既有组件（ProductPick / ProductPicks）的图片映射 */
export const PRODUCT_IMAGES: Record<
  string,
  { asin: string; brand: string; image: string; imageAlt: string }
> = Object.fromEntries(
  Object.entries(PRODUCTS).map(([k, p]) => [
    k,
    { asin: p.asin, brand: p.brand, image: p.image, imageAlt: p.imageAlt },
  ]),
);

/** 类目级数据（Amazon.ca Hair Dryers Top 50，核对 2026-10-02） */
export const CATEGORY = {
  unitsMonthTop50: 33507,
  revenueMonthTop50: 1809118,
  avgPrice: 53.99,
  medianPrice: 49.39,
  priceBandComplaintRate: {
    under50: { reviews: 3259, avgRating: 3.39, complaintRate: 30.3 },
    mid50to120: { reviews: 887, avgRating: 3.52, complaintRate: 29.0 },
    over120: { reviews: 334, avgRating: 4.43, complaintRate: 9.6 },
  },
} as const;

/** 评论分析关键结论（独家一手数据，全站可引用；口径见 /how-we-test/） */
export const REVIEW_INSIGHTS = {
  totalReviews: 8261,
  models: 98,
  verifiedShare: 93.1,
  spanStart: 'Feb 2015',
  spanEnd: 'Sep 2026',
  sampleAvgRating: 3.37,
  medianReportedFailureMonths: 5.5,
  meanReportedFailureMonths: 6.0,
  reviewsNamingFailureMonth: 552,
  doaRate: 0.8,
  failureModes: {
    stoppedWorking: 601,
    cordOrConnector: 417,
    switch: 300,
    motorDegradation: 196,
    smokeOrFire: 182,
    heatingElement: 71,
    plasticMelting: 64,
  },
  durabilityNegativeMentions: 946,
  durabilityNegativeShare: 84,
  heatNegativeMentions: 590,
  smokeFireNegativeShare: 96,
  smellMentions: 215,
  smellNegativeShare: 84,
  attachmentFallMentions: 186,
  warrantyNegativeMentions: 610,
  warrantyNegativeShare: 81,
  voltageMentions: 785,
  alciMentions: 27,
  frenchReviews: 757,
  frenchShare: 9.2,
} as const;
