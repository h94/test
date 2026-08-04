/**
 * 將指定頁面從文件清單 skipped 還原至待人工審核清單
 */
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const dir = dirname(fileURLToPath(import.meta.url));
const indexPath = join(dir, '_index.md');
const revertIds = process.argv.slice(2);

if (revertIds.length === 0) {
  console.error('用法: node revert_skipped.mjs <pageId> ...');
  process.exit(1);
}

const idSet = new Set(revertIds);
const content = readFileSync(indexPath, 'utf8').replace(/\r\n/g, '\n');
const lines = content.split('\n');
const restored = [];

const filtered = lines.filter((line) => {
  const m = line.match(/^\| (\d+) \|/);
  if (!m || !idSet.has(m[1])) return true;
  restored.push(line.replace(/\| ⏭️ skipped \|$/, '| ✅ done |'));
  return false;
});

if (restored.length !== revertIds.length) {
  console.error(`還原失敗：預期 ${revertIds.length}，實際 ${restored.length}`);
  process.exit(1);
}

const reviewStart = filtered.findIndex((l) => l === '## 待人工審核清單');
let insertAt = reviewStart + 1;
for (let i = reviewStart + 1; i < filtered.length; i++) {
  if (filtered[i].match(/^\| \d+ \|/)) insertAt = i + 1;
}

filtered.splice(insertAt, 0, ...restored);
writeFileSync(indexPath, filtered.join('\n'), 'utf8');
restored.forEach((r) => console.log(`已還原: ${r.match(/^\| (\d+)/)?.[1]}`));
