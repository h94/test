/**
 * 將 Sprint 流程類文件從待人工審核移到文件清單，status 改為 skipped
 */
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const dir = dirname(fileURLToPath(import.meta.url));
const indexPath = join(dir, '_index.md');

/** 本次處理的頁面 ID（摘要為 Sprint 流程／與服務開發無直接關係） */
const pageIds = [
  '5341447', // Sprint 3 - Code Review
  '5341322', // Sprint 3 - Sonarqube Report
  '47218855', // TCZB Sprint 101
  '47222957', // TCZB Sprint 125
  '32540546', // TCZB Sprint 61
  '38011950', // TCZB Sprint 76
  '55579071', // TCZB Sprint 166
  '47219731', // TCZB Sprint 106
  '79462891', // TCZB Sprint 213
  '44663388', // TCZB Sprint 95
];

const idSet = new Set(pageIds);
const content = readFileSync(indexPath, 'utf8').replace(/\r\n/g, '\n');
const lines = content.split('\n');
const movedRows = [];

const filtered = lines.filter((line) => {
  const match = line.match(/^\| (\d+) \|/);
  if (!match || !idSet.has(match[1])) return true;
  const skippedLine = line.replace(/\| ✅ done \|$/, '| ⏭️ skipped |');
  movedRows.push(skippedLine);
  return false;
});

if (movedRows.length !== pageIds.length) {
  const found = movedRows.map((r) => r.match(/^\| (\d+) \|/)?.[1]);
  console.error(`預期移動 ${pageIds.length} 筆，實際找到 ${movedRows.length} 筆`);
  console.error('找到:', found);
  process.exit(1);
}

const docListStart = filtered.findIndex((l) => l === '## 文件清單');
const serviceSectionStart = filtered.findIndex((l) => l === '## 依服務分類');
let insertAt = -1;

for (let i = docListStart; i < serviceSectionStart; i++) {
  const line = filtered[i].trim();
  if (line === '|--------|------|------|---------|--------|----------------|------|--------|') {
    insertAt = i + 1;
    break;
  }
}

if (insertAt < 0) {
  console.error('找不到文件清單表格插入點');
  process.exit(1);
}

filtered.splice(insertAt, 0, ...movedRows);
writeFileSync(indexPath, filtered.join('\n'), 'utf8');
console.log(`已移動 ${movedRows.length} 筆至「## 文件清單」，status = ⏭️ skipped`);
