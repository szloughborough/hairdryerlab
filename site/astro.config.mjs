// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import rehypeAffiliateLinks from './src/plugins/rehype-affiliate-links.mjs';
import rehypeBrandComponents from './src/plugins/rehype-brand-components.mjs';
import { unresolvedTokens, buildStatus } from './src/data/affiliate.mjs';

// TODO: 换成正式域名后同步更新（canonical / sitemap / OG 都用它）
export const SITE = 'https://hairdryerlab.ca';

// 构建期提示联盟链接状态。缺链接不会静默通过——见下面的 AFFILIATE_STRICT。
const missing = unresolvedTokens();
if (missing.length) {
  console.warn(
    `\n⚠ 联盟链接：${buildStatus()}\n` +
      `  未解析 ${missing.length} 个：${missing.join(', ')}\n` +
      `  当前以 pending 锚点渲染（不可点击）。上线前请运行：\n` +
      `    python _scripts/sync_affiliate_links.py\n` +
      `  并设置 AFFILIATE_STRICT=1 构建，届时未解析会直接报错。\n`,
  );
}

export default defineConfig({
  site: SITE,
  trailingSlash: 'always',
  integrations: [
    mdx(),
    sitemap(),
  ],
  markdown: {
    // 标题锚点：AI 引用我们的内容时会带锚点定位到具体段落
    // 联盟占位符：{{affiliate_url_xxx}} → 真实推广链接
    rehypePlugins: [
      rehypeAffiliateLinks,
      rehypeBrandComponents,
      rehypeSlug,
      [rehypeAutolinkHeadings, { behavior: 'wrap', properties: { class: 'heading-anchor' } }],
    ],
  },
  vite: {
    resolve: {
      // 我们使用扁平（hoisted）node_modules（见 .npmrc），没有包符号链接，
      // 因此跳过符号链接解析是安全的。同时可避免 Vite 在 Windows 上调用
      // `net use` 检测网络驱动器——该调用在 VPN/企业网络下可能卡住或失败。
      preserveSymlinks: true,
    },
  },
  build: {
    inlineStylesheets: 'auto',
  },
});
