# 前端設計範本索引（DESIGN.md）

> 來源：[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)（MIT）。已 vendor 至 `aidata/templates/design-md/{slug}/DESIGN.md`。
> **repo-init 僅讀此目錄**，不依賴 `_refs/`。

---

## 使用方式（repo-init）

1. 使用者選 `frontend-nuxt-tools` 後，詢問**設計大類**（下方 8 類選 1）。
2. 列出該類 `slugs`，請使用者選站台或「跳過」。
3. 複製 `aidata/templates/design-md/{slug}/DESIGN.md` → 目標 repo 根目錄 `./DESIGN.md`。
4. 於目標 repo `.rules.md` 追加本專案設計範本紀錄（見 `repo-init.mdc`）。

檔案路徑規則：`aidata/templates/design-md/{slug}/DESIGN.md`

---

## 設計大類

### 1. `devtools-infra` — 開發者工具與基礎設施後台

適合：內部 admin、API 管理、監控儀表板、深色 devtools、技術文件站。

| slug | 簡述 |
|------|------|
| `cursor` | AI 程式編輯器、深色漸層 |
| `vercel` | 黑白極簡、開發者平台 |
| `raycast` | 緊湊 launcher / 命令列感 |
| `warp` | 終端機、區塊式指令 UI |
| `expo` | React Native 開發者文件感 |
| `supabase` | 深色 emerald、資料庫後台 |
| `mongodb` | 綠葉、技術文件網站 |
| `hashicorp` | 企業 infra、黑白乾淨 |
| `clickhouse` | 黃色 accent、分析型 DB |
| `sentry` | 錯誤監控、資料密集 dashboard |
| `posthog` | 產品分析、開發者友善深色 UI |
| `composio` | 整合平台、工具圖示牆 |
| `resend` | 郵件 API、極簡深色 |
| `mintlify` | 文件站、閱讀優化 |
| `sanity` | 深色編輯型 CMS 行銷面 |
| `ollama` | 終端機優先、單色極簡 |
| `opencode.ai` | AI coding 深色主題 |
| `linear.app` | 極簡深色、工程師工具感 |

**亦常出現於其他類**：`cursor`/`ollama`/`opencode.ai` → `ai-llm`；`hashicorp` → `enterprise-hardware`；`linear.app` → `productivity-saas`

---

### 2. `ai-llm` — AI 與 LLM 產品介面

適合：AI 功能頁、模型平台、生成式工具 landing。

| slug | 簡述 |
|------|------|
| `claude` | 暖色 terracotta、編輯感 |
| `cohere` | 企業 AI、漸層 dashboard |
| `elevenlabs` | 深色電影感、語音波形 |
| `minimax` | 深色霓虹 accent |
| `mistral.ai` | 紫色極簡、歐洲工程感 |
| `replicate` | 白底、程式碼優先 API |
| `runwayml` | 電影節、創意生成工具 |
| `together.ai` | 藍圖式技術 infra |
| `voltagent` | 黑底 emerald、agent 框架 |
| `x.ai` | 極簡黑白、未來感 |
| `lovable` | 漸層、友善 AI 建站 |
| `cursor` | AI 程式編輯器 |
| `ollama` | 本機 LLM、終端風 |
| `opencode.ai` | AI coding 平台 |

---

### 3. `enterprise-hardware` — 企業科技與硬體供應商

適合：B2B 企業官網、硬體/電信大廠、Carbon 藍色系統。

| slug | 簡述 |
|------|------|
| `ibm` | Carbon Design、結構化藍色 |
| `hp` | 白底、HP 藍 CTA、幾何裝飾 |
| `apple` | 大留白、產品攝影 |
| `nvidia` | 綠黑、GPU 算力科技感 |
| `vodafone` | 電信紅、大寫標題帶 |
| `slack` | 企業協作、紫色工作區 |
| `spacex` | 太空科技、全幅影像黑白 |
| `hashicorp` | 企業 infra、黑白乾淨 |
| `dell-1996` | 1996 企業 catalog 懷舊 |

**亦常出現於其他類**：`slack` → `productivity-saas`；`spacex` → `media-retro`；`dell-1996` → `media-retro`

---

### 4. `fintech` — 金融科技與支付

適合：錢包、交易、支付後台、信任感 UI。

| slug | 簡述 |
|------|------|
| `stripe` | 紫色漸層、支付 infra |
| `wise` | 綠色、跨境匯款清晰 |
| `revolut` | 深色、漸層卡片 fintech |
| `coinbase` | 藍色、機構信任感 |
| `kraken` | 紫色深色、交易所 dashboard |
| `binance` | 黃黑、交易緊迫感 |
| `mastercard` | 暖奶油色、軌道 pill 形狀 |

---

### 5. `retail-consumer` — 零售、旅遊與生活消費

適合：商品列表、會員、訂單、生活服務、遊戲零售。

| slug | 簡述 |
|------|------|
| `nike` | 黑白、大寫運動攝影 |
| `shopify` | 深色電影感、neon 綠電商 |
| `starbucks` | 大地綠、奶油色餐飲 |
| `airbnb` | 珊瑚色、攝影驅動 |
| `meta` | 產品攝影、Meta 藍 CTA |
| `pinterest` | 紅色、masonry 圖牆 |
| `uber` | 黑白、都市移動能量 |
| `playstation` | 遊戲主機零售、青色互動 |
| `spotify` | 綠色深色、專輯封面驅動 |
| `nintendo-2001` | Y2K 遊戲主機懷舊 |

**亦常出現於其他類**：`spotify` → `media-retro`；`nintendo-2001` → `media-retro`

---

### 6. `productivity-saas` — 生產力與協作 SaaS

適合：內部工具、表單、看板、協作、自動化後台（**最接近 toolstemplate**）。

| slug | 簡述 |
|------|------|
| `linear.app` | 極簡深色、工程師 PM |
| `notion` | 暖色、serif 標題、軟表面 |
| `intercom` | 藍色、對話式客服 UI |
| `airtable` | 彩色、友善資料表 |
| `miro` | 黃色 accent、無限畫布 |
| `figma` | 多彩、設計協作 |
| `framer` | 黑藍、動效優先 |
| `webflow` | 藍色、精緻行銷站 |
| `zapier` | 橘色、插畫自動化 |
| `cal` | 中性、排程開發者風 |
| `clay` | 有機形狀、agency 藝術感 |
| `superhuman` | 深色 premium、鍵盤優先 |
| `slack` | 企業協作、紫色工作區 |

**toolstemplate 預設推薦**：`linear.app`、`notion`、`airtable`、`intercom`

---

### 7. `automotive-luxury` — 汽車與奢華製造

適合：高端品牌形象、全幅影像、奢華深色。

| slug | 簡述 |
|------|------|
| `bmw` | 深色德系精準 |
| `bmw-m` | 賽道 M 色、性能對比 |
| `ferrari` | 紅黑編輯、法拉利紅 |
| `lamborghini` | 黑底金 accent、超跑 |
| `bugatti` | 電影黑、紀念碑式字體 |
| `renault` | 極光漸層、法系車廠 |
| `tesla` | 減法、全視窗攝影、電動車 |

---

### 8. `media-retro` — 媒體編輯與復古網頁

適合：內容站、科技媒體排版、90s/2000s 懷舊主題。

| slug | 簡述 |
|------|------|
| `wired` | 報紙白底、serif、科技雜誌 |
| `theverge` | 酸綠/紫 accent、編輯標題 |
| `spacex` | 太空敘事、全幅影像 |
| `runwayml` | 創意媒體、電影節感 |
| `spotify` | 音樂媒體、專輯驅動 |
| `dell-1996` | 1996 企業 catalog 框線 |
| `nintendo-2001` | Y2K 金屬面板、像素瑪利歐 |

---

## slug 跨類對照（查詢用）

| slug | 所屬大類（主類優先） |
|------|----------------------|
| `airbnb` | retail-consumer |
| `airtable` | productivity-saas |
| `apple` | enterprise-hardware |
| `binance` | fintech |
| `bmw` | automotive-luxury |
| `bmw-m` | automotive-luxury |
| `bugatti` | automotive-luxury |
| `cal` | productivity-saas |
| `claude` | ai-llm |
| `clay` | productivity-saas |
| `clickhouse` | devtools-infra |
| `cohere` | ai-llm |
| `coinbase` | fintech |
| `composio` | devtools-infra |
| `cursor` | devtools-infra, ai-llm |
| `dell-1996` | enterprise-hardware, media-retro |
| `elevenlabs` | ai-llm |
| `expo` | devtools-infra |
| `ferrari` | automotive-luxury |
| `figma` | productivity-saas |
| `framer` | productivity-saas |
| `hashicorp` | devtools-infra, enterprise-hardware |
| `hp` | enterprise-hardware |
| `ibm` | enterprise-hardware |
| `intercom` | productivity-saas |
| `kraken` | fintech |
| `lamborghini` | automotive-luxury |
| `linear.app` | productivity-saas, devtools-infra |
| `lovable` | ai-llm |
| `mastercard` | fintech |
| `meta` | retail-consumer |
| `minimax` | ai-llm |
| `mintlify` | devtools-infra |
| `miro` | productivity-saas |
| `mistral.ai` | ai-llm |
| `mongodb` | devtools-infra |
| `nike` | retail-consumer |
| `nintendo-2001` | retail-consumer, media-retro |
| `notion` | productivity-saas |
| `nvidia` | enterprise-hardware |
| `ollama` | devtools-infra, ai-llm |
| `opencode.ai` | devtools-infra, ai-llm |
| `pinterest` | retail-consumer |
| `playstation` | retail-consumer |
| `posthog` | devtools-infra |
| `raycast` | devtools-infra |
| `renault` | automotive-luxury |
| `replicate` | ai-llm |
| `resend` | devtools-infra |
| `revolut` | fintech |
| `runwayml` | ai-llm, media-retro |
| `sanity` | devtools-infra |
| `sentry` | devtools-infra |
| `shopify` | retail-consumer |
| `slack` | productivity-saas, enterprise-hardware |
| `spacex` | enterprise-hardware, media-retro |
| `spotify` | retail-consumer, media-retro |
| `starbucks` | retail-consumer |
| `stripe` | fintech |
| `superhuman` | productivity-saas |
| `supabase` | devtools-infra |
| `tesla` | automotive-luxury |
| `theverge` | media-retro |
| `together.ai` | ai-llm |
| `uber` | retail-consumer |
| `vercel` | devtools-infra |
| `vodafone` | enterprise-hardware |
| `voltagent` | ai-llm |
| `warp` | devtools-infra |
| `webflow` | productivity-saas |
| `wise` | fintech |
| `wired` | media-retro |
| `x.ai` | ai-llm |
| `zapier` | productivity-saas |
