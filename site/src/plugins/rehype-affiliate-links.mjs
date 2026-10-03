/**
 * rehype 插件：把正文里的 {{affiliate_url_xxx}} 替换成真实推广链接。
 *
 * 常见位置：
 *   - markdown 链接语法  [Check price at Amazon.ca]({{affiliate_url_laifen_air}})
 *   - frontmatter 以外的正文散落文本
 * frontmatter 的 affiliateUrl 由 src/data/affiliate.mjs 的 resolveAffiliateUrl() 处理。
 *
 * 用 rehype 而不是字符串替换，是因为这里拿到的是已经解析好的 HAST，
 * 只需处理链接属性与文本节点，不会误伤代码块 / 属性 / 正文中的其他花括号。
 *
 * ⚠️ 两个关键细节（曾导致占位符泄漏到线上）：
 *   1. HAST 里元素属性在 node.properties.href，**不是** node.url。
 *   2. markdown 解析器会把 URL 里的花括号百分号编码：
 *      {{affiliate_url_x}} → %7B%7Baffiliate_url_x%7D%7D
 *      所以必须解码后再判断，否则 indexOf('{{') 永远匹配不到。
 */

import { resolveString } from '../data/affiliate.mjs';

const SKIP_TAGS = new Set(['code', 'pre', 'script', 'style']);

/** 解码可能被 markdown 编码过的 URL；失败则原样返回 */
function decodeMaybe(value) {
  if (typeof value !== 'string') return value;
  if (value.indexOf('%7B') === -1 && value.indexOf('%7b') === -1) return value;
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

/** 解析占位符；非占位符原样返回 */
function resolveValue(value, file) {
  const decoded = decodeMaybe(value);
  if (typeof decoded !== 'string' || decoded.indexOf('{{') === -1) return value;
  try {
    return resolveString(decoded);
  } catch (err) {
    throw new Error(`[${file?.path ?? 'unknown'}] ${err.message}`);
  }
}

/** 未解析时 affiliate.mjs 生成的占位片段 */
function isPending(href) {
  return typeof href === 'string' && href.startsWith('#affiliate-pending');
}

/**
 * 联盟外链的合规属性。
 * /affiliate-disclosure/ 页面明确承诺「联盟链接标记 rel="sponsored"」，
 * 所以解析成功后必须真的加上——否则页面声明与实现不符
 * （FTC 背书指南 / 加拿大竞争法都要求披露商业关系）。
 */
function markSponsored(node, resolvedHref) {
  if (!/^https?:/i.test(resolvedHref)) return;
  const props = node.properties || (node.properties = {});
  props.rel = ['sponsored', 'nofollow', 'noopener'];
  props.target = '_blank';
}

/**
 * 未解析的占位符降级为**真正不可点击**的文本。
 *
 * 设计意图（见《联盟API接入-对接说明.md》）：pending 必须是不可点击的，
 * 否则会得到一个「点了没反应」的假链接；而且 #fragment 配上 target="_blank"
 * 会打开空白标签页，比不做更糟。
 */
function degradeToText(node) {
  const props = node.properties || (node.properties = {});
  delete props.href;
  delete props.rel;
  delete props.target;
  node.tagName = 'span';
  props.className = ['affiliate-pending'];
}

function walk(node, file) {
  if (!node || typeof node !== 'object') return;

  if (Array.isArray(node.children)) {
    for (const child of node.children) walk(child, file);
  }

  if (node.type === 'element') {
    if (SKIP_TAGS.has(node.tagName)) return;

    const props = node.properties;
    if (props) {
      // <a href="{{...}}"> —— 这是实际泄漏的位置
      if (typeof props.href === 'string') {
        const before = props.href;
        const after = resolveValue(before, file);
        if (after !== before) {
          if (node.tagName === 'a' && isPending(after)) {
            degradeToText(node);
          } else {
            props.href = after;
            if (node.tagName === 'a') markSponsored(node, after);
          }
        }
      }
      // <img src="{{...}}"> 之类
      if (typeof props.src === 'string') {
        props.src = resolveValue(props.src, file);
      }
    }
    return;
  }

  // 文本节点：占位符以纯文本形式出现时兜底处理
  if (node.type === 'text' && typeof node.value === 'string' && node.value.indexOf('{{') !== -1) {
    node.value = resolveValue(node.value, file);
  }
}

export default function rehypeAffiliateLinks() {
  return (tree, file) => {
    walk(tree, file);
  };
}
