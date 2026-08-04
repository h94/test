/**
 * 由 _index.md 產生含 CSS 的 XHTML
 */
import { readFileSync, writeFileSync, unlinkSync } from 'fs';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const dir = dirname(fileURLToPath(import.meta.url));

const PAGE_STYLES = `
  body { font-family: "Segoe UI", system-ui, sans-serif; margin: 1.5rem 2rem; line-height: 1.5; color: #172b4d; }
  h1 { border-bottom: 2px solid #dfe1e6; padding-bottom: 0.5rem; }
  h2 { margin-top: 2rem; color: #253858; }
  h3 { margin-top: 1.25rem; }
  blockquote { border-left: 4px solid #0052cc; margin: 0 0 1rem; padding: 0.5rem 1rem; background: #f4f5f7; }
  pre { background: #f4f5f7; padding: 1rem; overflow-x: auto; border-radius: 4px; white-space: pre-wrap; }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.82rem; }
  th, td { border: 1px solid #dfe1e6; padding: 0.35rem 0.5rem; text-align: left; vertical-align: top; }
  th { background: #ebecf0; position: sticky; top: 0; }
  tr:nth-child(even) { background: #fafbfc; }
  a { color: #0052cc; }
  hr { border: none; border-top: 1px solid #dfe1e6; margin: 2rem 0; }
`;

/**
 * 移除 BOM 並修正表頭欄位數與資料列不一致的表格
 */
function preprocessMarkdown(markdown) {
  let md = markdown;
  if (md.charCodeAt(0) === 0xfeff) md = md.slice(1);
  md = md.replace(
    /\| 頁面 ID \| 標題 \| 原因 \| Confluence 連結 \| 建議動作 \|\r?\n\|--------\|------\|------\|----------------\|---------\|/,
    '| 頁面 ID | 標題 | 類型 | 相關服務 | 關鍵字 | Confluence 連結 | 摘要 | status |\n|--------|------|------|---------|--------|----------------|------|--------|'
  );
  return md;
}

/**
 * 為 table 加上寬度屬性，方便橫向閱讀
 */
function enhanceTables(html) {
  return html.replace(/<table>/g, '<table style="min-width: 1200px;">');
}

/**
 * 調整為嚴格 XHTML（自閉合標籤）
 */
function toStrictXhtml(html) {
  return html
    .replace(/<hr>/g, '<hr />')
    .replace(/<br>/g, '<br />')
    .replace(/<meta([^>]+)>/g, '<meta$1 />');
}

/**
 * 產生含內嵌 CSS 的 XHTML 1.0 文件（瀏覽器可直接開啟預覽）
 */
function wrapStyledXhtml(html) {
  const body = toStrictXhtml(enhanceTables(html));
  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-Hant">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Confluence 文件索引</title>
<style type="text/css"><![CDATA[${PAGE_STYLES}]]></style>
</head>
<body>
${body}
</body>
</html>`;
}

const inputMd = join(dir, '_index.md');
const tempMd = join(dir, '_index.nobom.md');
const rawHtml = join(dir, '_index.raw.html');
const outputXhtml = join(dir, '_index.xhtml');

const markdown = readFileSync(inputMd, 'utf8');
writeFileSync(tempMd, preprocessMarkdown(markdown), 'utf8');

execSync(`npx --yes marked -i "${tempMd}" -o "${rawHtml}" --gfm`, {
  cwd: dir,
  stdio: 'inherit',
});

const htmlRaw = readFileSync(rawHtml, 'utf8');
writeFileSync(outputXhtml, wrapStyledXhtml(htmlRaw), 'utf8');

for (const temp of [tempMd, rawHtml]) {
  try { unlinkSync(temp); } catch { /* ignore */ }
}

console.log(`Wrote ${outputXhtml}`);
