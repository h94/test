/**
 * 依摘要從待人工審核掃描並移動至文件清單（skipped）
 * 規則：僅「明顯無內容」或「Sprint 流程模板（完全不涉及服務業務/技術）」
 * 排除：operation_guide 等有知識庫價值的操作／維運文件
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const dir = dirname(fileURLToPath(import.meta.url));
const indexPath = join(dir, '_index.md');
const processedDir = join(dir, 'processed');
const runAll = process.argv.includes('--all');
const batchSize = runAll ? Infinity : Number(process.argv.find((a) => /^\d+$/.test(a)) || 20);

/**
 * 從文件清單讀取已標 skipped 的頁面 ID
 */
function loadAlreadySkipped(lines) {
  const ids = new Set();
  const docStart = lines.findIndex((l) => l === '## 文件清單');
  const docEnd = lines.findIndex((l) => l === '## 依服務分類');
  for (let i = docStart; i < docEnd; i++) {
    const m = lines[i].match(/^\| (\d+) \|.*\| ⏭️ skipped \|$/);
    if (m) ids.add(m[1]);
  }
  return ids;
}

/** 明顯無內容（缺資料、無法讀取、僅空白／僅連結無說明） */
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

/** Sprint 流程模板（不涉及任何服務業務／技術，與第 1 批標準一致） */
const sprintProcessPatterns = [
  /TCZB Sprint|Sprint_\d+|Sprint \d+\s*-/,
  /Sprint 流程|Sprint 管理|流程手冊|流程模板|流程指引/,
  /Scrum.*流程|通用 Sprint|Sprint 執行流程|Sprint 週期.*檢查/,
  /專案管理流程|標準作業流程|標準化流程.*檢查清單|標準流程步驟/,
  /Code Review.*Sprint|Sprint.*Code Review|SonarQube.*報告/,
];

/** 摘要明確有開發或規格價值時排除 */
const keepPatterns = [
  /定義了.*API|明確了.*端點|API 規格/,
  /業務規則.*包含|核心業務|具體業務規則/,
  /技術設計.*細節|實作細節|技術實作|Schema|時序圖.*展示/,
  /有助於.*(整合|介面|開發|實作)/,
  /操作步驟|圖文操作|登入帳密|工作清單|負責人/,
];

/**
 * 從表格列解析類型欄位
 */
function parseRowType(line) {
  const parts = line.split('|').map((p) => p.trim());
  return parts[3] || '';
}

/**
 * 從 summary 檔擷取「## 摘要」段落文字
 */
function extractSummaryText(summaryPath) {
  if (!existsSync(summaryPath)) return '';
  const text = readFileSync(summaryPath, 'utf8').replace(/\r\n/g, '\n');
  const match = text.match(/## 摘要\s*\n+<!--[\s\S]*?-->\s*\n+([\s\S]*?)(?=\n## |\n---|\n*$)/);
  if (match) return match[1].trim();
  const fallback = text.match(/## 摘要\s*\n+([\s\S]*?)(?=\n## |\n---)/);
  return fallback ? fallback[1].trim() : '';
}

/**
 * 判斷摘要是否應標為 skipped
 */
function shouldSkip(summary, docType, title) {
  if (!summary || summary.length < 10) return { skip: true, reason: '摘要過短或空白' };
  const combined = `${title} ${summary}`;
  for (const pattern of sprintProcessPatterns) {
    if (pattern.test(combined)) return { skip: true, reason: `Sprint流程:${pattern.source}` };
  }
  for (const pattern of noContentPatterns) {
    if (pattern.test(summary)) return { skip: true, reason: `明顯無內容:${pattern.source}` };
  }
  // 操作手冊／維運紀錄：視為知識庫，不自動 skipped（除非明顯無內容）
  if (docType === 'operation_guide' && !noContentPatterns.some((p) => p.test(summary))) {
    return { skip: false, reason: '' };
  }
  if (/操作說明|操作手冊|操作指引|工作清單/.test(title) && !noContentPatterns.some((p) => p.test(summary))) {
    return { skip: false, reason: '' };
  }
  if (keepPatterns.some((p) => p.test(summary))) return { skip: false, reason: '' };
  return { skip: false, reason: '' };
}

const content = readFileSync(indexPath, 'utf8').replace(/\r\n/g, '\n');
const lines = content.split('\n');
const alreadySkipped = loadAlreadySkipped(lines);
const reviewStart = lines.findIndex((l) => l === '## 待人工審核清單');
if (reviewStart < 0) {
  console.error('找不到待人工審核清單');
  process.exit(1);
}

const candidates = [];

for (let i = reviewStart + 1; i < lines.length; i++) {
  const rowMatch = lines[i].match(/^\| (\d+) \| (.+?) \|/);
  if (!rowMatch) continue;
  const pageId = rowMatch[1];
  const title = rowMatch[2];
  if (alreadySkipped.has(pageId)) continue;

  const docType = parseRowType(lines[i]);
  const summaryPath = join(processedDir, `${pageId}-summary.md`);
  const summary = extractSummaryText(summaryPath);
  const { skip, reason } = shouldSkip(summary, docType, title);
  if (skip) candidates.push({ pageId, title, reason });
}

const toMove = candidates.slice(0, batchSize);
if (!runAll && toMove.length < batchSize) {
  console.warn(`僅找到 ${toMove.length} 筆符合條件（目標 ${batchSize} 筆）`);
}

console.log(`本次將移動 ${toMove.length} 筆`);
if (toMove.length <= 20) {
  toMove.forEach((c) => console.log(`  ${c.pageId} | ${c.title} | ${c.reason}`));
} else {
  toMove.slice(0, 5).forEach((c) => console.log(`  ${c.pageId} | ${c.title} | ${c.reason}`));
  console.log(`  ... 其餘 ${toMove.length - 5} 筆`);
}

if (toMove.length === 0) {
  console.log('無符合條件的項目，結束');
  process.exit(0);
}

const idSet = new Set(toMove.map((c) => c.pageId));
const movedRows = [];
const filtered = lines.filter((line) => {
  const match = line.match(/^\| (\d+) \|/);
  if (!match || !idSet.has(match[1])) return true;
  movedRows.push(line.replace(/\| ✅ done \|$/, '| ⏭️ skipped |'));
  return false;
});

if (movedRows.length !== toMove.length) {
  console.error(`移動失敗：預期 ${toMove.length}，實際 ${movedRows.length}`);
  process.exit(1);
}

const docListStart = filtered.findIndex((l) => l === '## 文件清單');
const serviceSectionStart = filtered.findIndex((l) => l === '## 依服務分類');
let insertAt = -1;
for (let i = docListStart; i < serviceSectionStart; i++) {
  if (filtered[i].trim() === '|--------|------|------|---------|--------|----------------|------|--------|') {
    insertAt = i + 1;
    break;
  }
}

filtered.splice(insertAt, 0, ...movedRows);
writeFileSync(indexPath, filtered.join('\n'), 'utf8');
console.log(`\n已移動 ${movedRows.length} 筆至「## 文件清單」，status = ⏭️ skipped`);
