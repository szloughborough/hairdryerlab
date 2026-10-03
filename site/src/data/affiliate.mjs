/**
 * 联盟链接解析 —— 占位符 {{affiliate_url_xxx}} → 真实推广链接。
 *
 * 数据流：
 *   _scripts/sync_affiliate_links.py   调三家 API
 *        ↓ 写入
 *   src/data/affiliate-links.mjs       自动生成，不要手改
 *        ↓ 本文件解析
 *   正文 markdown / frontmatter         占位符被替换
 *
 * 为什么构建时严格报错：
 *   之前 dist 里出现了 href="%7B%7Baffiliate_url_laifen_air%7D%7D" —— 占位符
 *   直接泄漏到了线上，是坏链。宁可构建失败，也不上线坏链。
 *   确实还没接入网络的产品，在 affiliate-products.mjs 里标 defer: true，
 *   或临时设 AFFILIATE_LENIENT=1 构建（会渲染成不可点击的 pending 锚点）。
 */

import { LINKS, META } from './affiliate-links.mjs';
import { AFFILIATE_PRODUCTS, TOKEN_INDEX, AMAZON_ASSOCIATE_TAG } from './affiliate-products.mjs';

/** 宽松模式：未解析的 token 渲染成 pending 锚点而不是让构建失败 */
const ENV = (typeof process !== 'undefined' && process.env) || {};
const STRICT = ENV.AFFILIATE_STRICT === '1';
const LENIENT = !STRICT || ENV.AFFILIATE_LENIENT === '1';

/** 占位符正则：{{affiliate_url_xxx}} */
const PLACEHOLDER_RE = /\{\{\s*(affiliate_url_[A-Za-z0-9_]+)\s*\}\}/g;

/**
 * Amazon Associates 兜底。
 *
 * 为什么需要：三家联盟网络只覆盖它们签约的品牌。实测下来 Dyson / Shark /
 * Conair / wavytalk / Revlon / Aina 在三家都拿不到链接，于是 6 个高价值
 * 品牌评测页一条外链都没有 —— 对读者是「点了没反应」，对站点是零变现。
 *
 * 优先级规则（重要，也涉及合规）：
 *   1. 联盟网络链接优先（Laifen 15%、Dreame 10%，佣金远高于 Associates）
 *   2. 只有该商品拿不到任何网络链接时，才用 Associates 兜底
 *   3. 绝不叠加 —— 同一商品不会同时挂网络链接与 Associates tag，
 *      那会同时违反两边的协议
 */
const AMAZON_TAG = ENV.AMAZON_ASSOCIATE_TAG || AMAZON_ASSOCIATE_TAG;
const AMAZON_HOST = 'https://www.amazon.ca';

function amazonFallback(token) {
  if (!AMAZON_TAG) return null;
  const p = TOKEN_INDEX[token];
  const asin = p && p.asin;
  if (!asin) return null;
  return {
    url: `${AMAZON_HOST}/dp/${asin}?tag=${AMAZON_TAG}`,
    asin,
    provider: 'amazon-associates',
  };
}

/** 未解析时的兜底锚点：明显不是真实链接，方便上线前一眼发现 */
export function pendingHref(token) {
  return `#affiliate-pending-${token}`;
}

export function resolveToken(token) {
  const hit = LINKS[token];
  if (hit && hit.url) return hit;
  return amazonFallback(token);
}

/** 哪些 token 走了 Associates 兜底（而非联盟网络），供构建日志与报告使用 */
export function fallbackTokens() {
  return Object.keys(TOKEN_INDEX).filter((t) => {
    const hit = LINKS[t];
    return !(hit && hit.url) && Boolean(amazonFallback(t));
  });
}

/** 该商品最终由哪家结算：联盟网络 or Associates */
export function providerOf(token) {
  const hit = LINKS[token];
  if (hit && hit.url) return hit.provider || 'network';
  return amazonFallback(token) ? 'amazon-associates' : null;
}

function isKnownToken(token) {
  return Boolean(TOKEN_INDEX[token]);
}

/** 解析任意字符串里的所有占位符 */
export function resolveString(input) {
  if (!input || input.indexOf('{{') === -1) return input;
  return input.replace(PLACEHOLDER_RE, (whole, token) => {
    const hit = resolveToken(token);
    if (hit) return hit.url;
    if (LENIENT) return pendingHref(token);
    throw new Error(formatUnresolved([token]));
  });
}

export function hasPlaceholder(input) {
  return Boolean(input) && input.indexOf('{{') !== -1;
}

/**
 * 解析 frontmatter 的 affiliateUrl。
 * 优先按占位符 token 查；若作者直接写了真实 URL 则原样放行。
 * 两者都没有时，退回按 ASIN 查注册表。
 */
export function resolveAffiliateUrl(raw, asin) {
  if (raw && hasPlaceholder(raw)) return resolveString(raw);
  if (raw && /^https?:\/\//i.test(raw)) return raw;

  if (asin) {
    const product = AFFILIATE_PRODUCTS.find((p) => p.asin === asin);
    if (product) {
      const hit = resolveToken(product.token);
      if (hit) return hit.url;
    }
  }

  if (LENIENT) return pendingHref(raw || asin || 'unknown');
  throw new Error(
    `无法解析联盟链接：affiliateUrl=${JSON.stringify(raw)} asin=${JSON.stringify(asin)}\n` +
      formatUnresolved(raw && hasPlaceholder(raw) ? extractTokens(raw) : []),
  );
}

function extractTokens(input) {
  const out = [];
  for (const m of String(input).matchAll(PLACEHOLDER_RE)) out.push(m[1]);
  return out;
}

export function unresolvedTokens() {
  return Object.keys(TOKEN_INDEX).filter((t) => !resolveToken(t));
}

export function buildStatus() {
  const total = Object.keys(TOKEN_INDEX).length;
  const missing = unresolvedTokens().length;
  const net = total - missing - fallbackTokens().length;
  const fb = fallbackTokens().length;
  return (
    `${total - missing}/${total} 有链接  ` +
    `（联盟网络 ${net} · Amazon Associates 兜底 ${fb}${missing ? ` · 仍缺失 ${missing}` : ''}）  ` +
    `最后同步 ${META.syncedAt || '从未同步'}`
  );
}

function formatUnresolved(tokens) {
  const unique = [...new Set(tokens)];
  const unknown = unique.filter((t) => !isKnownToken(t));
  const lines = [
    '',
    '✗ 联盟链接占位符未解析，构建中止（避免坏链上线）。',
    '',
    `  未解析 (${unique.length}): ${unique.join(', ') || '(见 affiliate-links.mjs 的 pending)'}`,
  ];
  if (unknown.length) {
    lines.push(`  ⚠ 不在注册表中（疑似拼写错误）: ${unknown.join(', ')}`);
  }
  lines.push(
    '',
    '  处理方式：',
    '    1) 在 site/.env 填入联盟网络凭据，然后运行：',
    '         python _scripts/sync_affiliate_links.py',
    '    2) 该产品确实未接入任何网络 → 在 src/data/affiliate-products.mjs',
    '       对应条目加 defer: true，或删掉该产品',
    '    3) 临时预览：设 AFFILIATE_LENIENT=1 再构建',
    '',
  );
  return lines.join('\n');
}

/** 供构建脚本 / 调试打印用 */
export function assertAllResolved() {
  const missing = unresolvedTokens();
  if (missing.length && !LENIENT) throw new Error(formatUnresolved(missing));
}

export { META as AFFILIATE_META };
