/**
 * rehype 插件：把正文里已有的 markdown 模式升级为 §55 品牌组件结构。
 *
 * 为什么在 rehype 层做而不是改 44 篇 MDX：
 *   pros/cons 的 bullet 里含 **粗体**、[链接] 和 *(证据标注)*。
 *   若改成 <ProsCons liked={["..."]} /> 字符串数组，markdown 不会再被解析，
 *   读者会看到字面的星号和方括号。在 HAST 层包装可完整保留内联标记。
 *
 * 处理两种模式：
 *   A. §70 Pros / Cons
 *      <p><strong>What we liked</strong></p><ul>…</ul>
 *      <p><strong>What we didn't</strong></p><ul>…</ul>
 *      → <div class="proscons"><div class="proscons--liked"><h3>…</h3><ul>…</ul></div>…</div>
 *
 *   B. §51 证据等级标签
 *      <em>(review analysis)</em> → <span class="ev ev-analysis">Review analysis</span>
 *      非标签斜体（如 *What we cannot say.*）不受影响。
 */

/** 证据等级映射 —— 标签文字与 EvidenceLabel.astro 的 MAP 一致。
 *  注意：正文里写的是小写（*(review analysis)*），组件里是大写，因此按小写键查找。 */
const EV_MAP = {
  measured: 'ev-measured',
  'review analysis': 'ev-analysis',
  'amazon.ca data': 'ev-amazon',
  'buyer feedback': 'ev-feedback',
  'manufacturer claim': 'ev-claim',
};

/** 规范化后的显示文本（组件里用的是首字母大写形式） */
const EV_TEXT = {
  measured: 'Measured',
  'review analysis': 'Review analysis',
  'amazon.ca data': 'Amazon.ca data',
  'buyer feedback': 'Buyer feedback',
  'manufacturer claim': 'Manufacturer claim',
};

const LIKED_RE = /^what we liked\b/i;
const NOT_LIKED_RE = /^what we (?:didn'?t|did not|didn\u2019t)\b/i;

function textOf(node) {
  if (!node) return '';
  if (node.type === 'text') return node.value;
  if (Array.isArray(node.children)) return node.children.map(textOf).join('');
  return '';
}

function el(tagName, properties, children) {
  return { type: 'element', tagName, properties: properties || {}, children: children || [] };
}

function isTag(node, tagName) {
  return Boolean(node) && node.type === 'element' && node.tagName === tagName;
}

/** 跳过纯空白文本节点，返回下一个有意义子节点的下标 */
function nextSignificant(children, from) {
  let i = from;
  while (i < children.length) {
    const c = children[i];
    if (c.type === 'text' && !c.value.trim()) {
      i += 1;
      continue;
    }
    return i;
  }
  return -1;
}

/** B. 斜体证据标注 → .ev 徽章（就地替换） */
function upgradeEvidence(node) {
  if (!node || typeof node !== 'object' || !Array.isArray(node.children)) return;
  for (let i = 0; i < node.children.length; i += 1) {
    const child = node.children[i];
    if (isTag(child, 'em')) {
      const m = /^\(\s*(.+?)\s*\)$/.exec(textOf(child).trim());
      const key = m ? m[1].toLowerCase() : '';
      if (key && EV_MAP[key]) {
        node.children[i] = el('span', { className: ['ev', EV_MAP[key]] }, [
          { type: 'text', value: EV_TEXT[key] },
        ]);
        continue;
      }
    }
    upgradeEvidence(child);
  }
}

/** A. liked / notLiked 两段 → proscons 结构（在任意含 children 的节点上尝试） */
function wrapProsCons(parent) {
  const kids = parent.children;
  if (!Array.isArray(kids)) return;

  let i = 0;
  while (i < kids.length) {
    const node = kids[i];
    if (!isTag(node, 'p') || !LIKED_RE.test(textOf(node).trim())) {
      i += 1;
      continue;
    }

    const likedUl = nextSignificant(kids, i + 1);
    if (likedUl < 0 || !isTag(kids[likedUl], 'ul')) {
      i += 1;
      continue;
    }

    const notP = nextSignificant(kids, likedUl + 1);
    if (notP < 0 || !isTag(kids[notP], 'p') || !NOT_LIKED_RE.test(textOf(kids[notP]).trim())) {
      i += 1;
      continue;
    }

    const notUl = nextSignificant(kids, notP + 1);
    if (notUl < 0 || !isTag(kids[notUl], 'ul')) {
      i += 1;
      continue;
    }

    const wrapper = el('div', { className: ['proscons'] }, [
      el('div', { className: ['proscons--liked'] }, [
        el('h3', {}, [{ type: 'text', value: 'What we liked' }]),
        kids[likedUl],
      ]),
      el('div', { className: ['proscons--not'] }, [
        el('h3', {}, [{ type: 'text', value: 'What we didn\u2019t' }]),
        kids[notUl],
      ]),
    ]);

    kids.splice(i, notUl - i + 1, wrapper);
    i += 1;
  }
}

/** C. §33 表格：套上可横向滚动的外壳（移动端必需），并加统一类名 */
function wrapTables(node) {
  if (!node || !Array.isArray(node.children)) return;
  for (let i = 0; i < node.children.length; i += 1) {
    const child = node.children[i];
    // 已经是 .table-scroll 外壳的跳过（幂等）
    if (isTag(child, 'div') && Array.isArray(child.properties?.className)
        && child.properties.className.includes('table-scroll')) {
      continue;
    }
    if (isTag(child, 'table')) {
      if (!Array.isArray(child.properties.className)) child.properties.className = [];
      if (!child.properties.className.includes('cmp-table')) {
        child.properties.className.push('cmp-table');
      }
      node.children[i] = el('div', { className: ['table-scroll'] }, [child]);
    } else {
      wrapTables(child);
    }
  }
}

function walk(node) {
  if (!node || typeof node !== 'object' || !Array.isArray(node.children)) return;
  // 先递归处理子节点（证据徽章在这一层完成替换）
  upgradeEvidence(node);
  for (const child of node.children) walk(child);
  // 子节点处理完后，再在本层尝试包装 pros/cons 与表格
  wrapProsCons(node);
  wrapTables(node);
}

export default function rehypeBrandComponents() {
  return (tree) => {
    walk(tree);
  };
}
