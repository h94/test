/**
 * 稽核文件清單中 skipped 項目，找出應還原至待人工審核者
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const dir = dirname(fileURLToPath(import.meta.url));
const indexPath = join(dir, '_index.md');
const processedDir = join(dir, 'processed');
const doRevert = process.argv.includes('--revert');

const noContentPatterns = [
  /文件內容為空|文件內容空白|內容為空|內容空白|內容缺失|內容幾乎為空|文件為空|幾乎為空/,
  /文件內容未提供|內容未提供|內容不明|無法提供摘要/,
  /無法分析並提供摘要|無法進行分析與摘要|無法進行分析|無法萃取出任何/,
  /無法存取|無法渲染|無法萃取/,
  /無法判斷.*(內容|資訊)|內容缺失.*無法判斷|文件內容缺失/,
  /實際內容未知|內容未知|無文字說明/,
  /僅為一行參考|僅有連結|僅包含.*連結|僅提供.*連結|重定向連結/,
  /無法為開發提供可執行的知識/,
];

const sprintProcessPatterns = [
  /TCZB Sprint|Sprint_\d+|Sprint \d+\s*-/,
  /Sprint 流程|Sprint 管理|流程手冊|流程模板|流程指引/,
  /Scrum.*流程|通用 Sprint|Sprint 執行流程|Sprint 週期.*檢查/,
  /專案管理流程|標準作業流程|標準化流程.*檢查清單|標準流程步驟/,
  /Code Review.*Sprint|Sprint.*Code Review|SonarQube.*報告/,
];

const keepPatterns = [
  /定義了.*API|明確了.*端點|API 規格/,
  /業務規則.*包含|核心業務|具體業務規則/,
  /技術設計.*細節|實作細節|技術實作|Schema|時序圖.*展示/,
  /有助於.*(整合|介面|開發|實作)/,
  /操作步驟|圖文操作|登入帳密|工作清單|負責人/,
  /UI 畫面|截圖|示意|可視化/,
  /操作說明|操作指引|維運|部署流程/,
];

function parseRowType(line) {
  const parts = line.split('|').map((p) => p.trim());
  return parts[3] || '';
}

function parseRowTitle(line) {
  const m = line.match(/^\| \d+ \| (.+?) \|/);
  return m ? m[1] : '';
}

function extractSummaryText(summaryPath) {
  if (!existsSync(summaryPath)) return '';
  const text = readFileSync(summaryPath, 'utf8').replace(/\r\n/g, '\n');
  const match = text.match(/## 摘要\s*\n+<!--[\s\S]*?-->\s*\n+([\s\S]*?)(?=\n## |\n---|\n*$)/);
  if (match) return match[1].trim();
  const fallback = text.match(/## 摘要\s*\n+([\s\S]*?)(?=\n## |\n---)/);
  return fallback ? fallback[1].trim() : '';
}

function shouldRemainSkipped(summary, docType, title) {
  if (!summary || summary.length < 10) return { skip: true, reason: '摘要過短或空白' };
  const combined = `${title} ${summary}`;
  for (const pattern of sprintProcessPatterns) {
    if (pattern.test(combined)) return { skip: true, reason: 'Sprint 流程模板' };
  }
  for (const pattern of noContentPatterns) {
    if (pattern.test(summary)) return { skip: true, reason: '明顯無內容' };
  }
  if (docType === 'operation_guide' && !noContentPatterns.some((p) => p.test(summary))) {
    return { skip: false, reason: 'operation_guide 有知識庫內容' };
  }
  if (/操作說明|操作手冊|操作指引|工作清單/.test(title) && !noContentPatterns.some((p) => p.test(summary))) {
    return { skip: false, reason: '標題為操作類文件且有內容' };
  }
  if (keepPatterns.some((p) => p.test(summary)) && !/無法為開發提供可執行的知識/.test(summary)) {
    return { skip: false, reason: '摘要有實質參考價值（知識庫）' };
  }
  return { skip: false, reason: '不符合現行 skipped 條件' };
}

const content = readFileSync(indexPath, 'utf8').replace(/\r\n/g, '\n');
const lines = content.split('\n');
const docStart = lines.findIndex((l) => l === '## 文件清單');
const docEnd = lines.findIndex((l) => l === '## 依服務分類');
const toRevert = [];

for (let i = docStart; i < docEnd; i++) {
  const line = lines[i];
  if (!line.includes('| ⏭️ skipped |')) continue;
  const pageId = line.match(/^\| (\d+) \|/)?.[1];
  if (!pageId) continue;
  const title = parseRowTitle(line);
  const docType = parseRowType(line);
  const summary = extractSummaryText(join(processedDir, `${pageId}-summary.md`));
  const { skip, reason } = shouldRemainSkipped(summary, docType, title);
  if (!skip) toRevert.push({ pageId, title, reason });
}

console.log(`稽核 skipped 共 ${lines.slice(docStart, docEnd).filter((l) => l.includes('| ⏭️ skipped |')).length} 筆`);
console.log(`建議還原 ${toRevert.length} 筆：\n`);
toRevert.forEach((r) => console.log(`  ${r.pageId} | ${r.title} | ${r.reason}`));

if (!doRevert || toRevert.length === 0) {
  if (doRevert) console.log('\n無需還原');
  else console.log('\n執行還原: node audit_skipped.mjs --revert');
  process.exit(0);
}

const idSet = new Set(toRevert.map((r) => r.pageId));
const restored = [];
const filtered = lines.filter((line) => {
  const m = line.match(/^\| (\d+) \|/);
  if (!m || !idSet.has(m[1])) return true;
  restored.push(line.replace(/\| ⏭️ skipped \|$/, '| ✅ done |'));
  return false;
});

const reviewStart = filtered.findIndex((l) => l === '## 待人工審核清單');
let insertAt = reviewStart + 1;
for (let i = reviewStart + 1; i < filtered.length; i++) {
  if (filtered[i].match(/^\| \d+ \|/)) insertAt = i + 1;
}
filtered.splice(insertAt, 0, ...restored);
writeFileSync(indexPath, filtered.join('\n'), 'utf8');
console.log(`\n已還原 ${restored.length} 筆至待人工審核清單`);
