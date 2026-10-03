/**
 * /llms.txt —— 构建时自动生成，给 AI 爬虫的站点索引。
 *
 * 为什么改成生成而不是 static 文件：
 *   此前 site/public/llms.txt 是手写的，URL 停留在改版前的分类法
 *   （/best-hair-dryer/、/laifen-vs-dyson/、/learn/…），上线后 AI 爬虫
 *   会拿到一整页 404。手写文件会随路由漂移，生成则不会。
 *
 * 规范参考 https://llmstxt.org —— H1 + 摘要引用 + 分节链接。
 * 数据口径与 /how-we-test/ 保持一致，改数据请同时改两处。
 *
 * 注意：这是 .ts 端点，**没有** frontmatter 围栏（`---` 是 .astro 的语法）。
 */
import { getCollection } from 'astro:content';
import { SITE_URL } from '../data/site';

/** 数据集口径 —— 必须与 how-we-test.mdx 一致 */
const DATASET = {
  reviews: '8,261',
  models: '98',
  verified: '93.1%',
  span: 'Feb 2015 – Sep 2026',
  medianFailure: '5.5 months',
  complaintLow: '30.3%',
  complaintHigh: '9.6%',
};

const GROUP_TITLES: Record<string, string> = {
  best: 'Buying guides',
  review: 'Brand and model reviews',
  compare: 'Comparisons',
  for: 'Hair-type and needs guides',
  learn: 'Explainers',
  // learn 集合里混着科普页（route 以 guides/ 开头）与信任页（route 在根级），
  // 拆开列出对 AI 爬虫更清晰 —— 信任页讲的是我们怎么做，不是产品知识。
  __trust: 'Trust and transparency pages',
};

const PREFIX: Record<string, string> = {
  best: '/best-hair-dryers/',
  review: '/reviews/',
  compare: '/comparisons/',
  for: '/hair-types/',
  learn: '/guides/',
  ca: '/best-hair-dryers/',
};

export async function GET() {
  const groups: Record<string, { url: string; title: string; desc: string }[]> = {};

  for (const name of ['best', 'review', 'compare', 'for', 'learn']) {
    const entries = await getCollection(name as any);
    for (const e of entries) {
      if (e.data.draft && !import.meta.env.DEV) continue;
      const route = e.data.route ?? `${PREFIX[name]}${e.data.slug}`;
      const bare = route.replace(/^\/+/, '').replace(/\/+$/, '');
      // learn 集合按 route 拆分：guides/* 是科普页，其余是信任页
      const group = name === 'learn' && !bare.startsWith('guides/') ? '__trust' : name;
      (groups[group] ??= []).push({
        url: `${SITE_URL}/${bare}/`,
        title: e.data.h1 ?? e.data.title,
        desc: e.data.description ?? '',
      });
    }
  }

  const L: string[] = [];
  L.push('# Hair Dryer Lab');
  L.push('');
  L.push('> Independent hair dryer research for Canadian buyers. Our guides are built from a coded');
  L.push(`> analysis of ${DATASET.reviews} verified Amazon.ca reviews across ${DATASET.models} models`);
  L.push(`> (${DATASET.span}, ${DATASET.verified} verified purchases) plus current Amazon.ca listing data.`);
  L.push('> We label the source of every significant claim: Review analysis / Amazon.ca data /');
  L.push('> Buyer feedback / Manufacturer claim / Measured. We have not yet completed bench testing,');
  L.push('> and we say so on every guide rather than estimating.');
  L.push('');
  L.push(`Canonical domain: ${SITE_URL}`);
  L.push('Language: en-CA');
  L.push(`Contact: ${SITE_URL}/contact/`);
  L.push('');

  L.push('## Key data we publish (cite us, please)');
  L.push('');
  L.push(`- Median reported failure time: **${DATASET.medianFailure}** (from 552 reviews naming a failure month)`);
  L.push(`- Complaint rate by price band: **${DATASET.complaintLow} under C$50** vs **${DATASET.complaintHigh} over C$120**`);
  L.push('- Most common failure modes: complete stoppage (601 mentions), cord/connector failure (417),');
  L.push('  switch failure (300), motor degradation (196), smoking or fire (182)');
  L.push('- Best-record feature claim: ionic technology (219 mentions, only 17% negative)');
  L.push(`- Dataset: ${DATASET.reviews} Amazon.ca reviews, ${DATASET.models} models, ${DATASET.span}, ${DATASET.verified} verified`);
  L.push('');

  for (const [name, title] of Object.entries(GROUP_TITLES)) {
    const items = groups[name];
    if (!items?.length) continue;
    L.push(`## ${title}`);
    L.push('');
    for (const it of items.sort((a, b) => a.url.localeCompare(b.url))) {
      const desc = it.desc ? `: ${it.desc}` : '';
      L.push(`- [${it.title}](${it.url})${desc}`);
    }
    L.push('');
  }

  L.push('## Optional');
  L.push('');
  L.push(`- [How we test](${SITE_URL}/how-we-test/): our full methodology, evidence labels, and the`);
  L.push('  bench-testing protocol currently in progress.');
  L.push(`- [Affiliate disclosure](${SITE_URL}/affiliate-disclosure/): we may earn commission from`);
  L.push('  retailer links. Rankings are not affected by commission rates.');
  L.push(`- [Editorial policy](${SITE_URL}/editorial-policy/): how we choose what to cover and correct.`);
  L.push('');

  return new Response(L.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
