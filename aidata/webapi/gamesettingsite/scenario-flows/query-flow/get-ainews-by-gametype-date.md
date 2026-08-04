# 取得站台賽事AI新聞

## 1. 場景目的

根據球種（gameType）與賽事日期（date）查詢 AI 預測新聞，回傳包括聯盟、隊伍、預測內容、盤口等前台展示所需資訊。此為面向遊戲設定站台（GS 版本）的公開查詢端點。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/ainews/{gameType}/{date}` | 取得指定球種與日期的 AI 新聞（GS 版本） |

參數說明：
- `gameType`：球種代碼，足球（SC）、棒球（BS）、籃球（BK）
- `date`：賽事開賽日期（格式 `yyyy-MM-dd`），對應 `gdate`

---

## 3. 流程總覽

1. 接收 GET 請求，取出路徑參數 `gameType` 與 `date`
2. 將球種代碼直接作為 `gtype`，日期作為 `gdate`，過濾條件加入 `status=1`（僅回傳已回應且無待修正的新聞）
3. 查詢 `news.ainews_gs` 表（Cassandra），使用分區鍵 `gdate` + 集群鍵 `gtype` 進行查詢
4. 取得記錄後，從 `others` map 提取 `league`、`teamA`、`teamH`、`gtime` 等欄位；解析 `anwser` 產生預測物件（predicts）；可能需從其他服務（如 PriceCenter）取得盤口資訊（haSpread / ouSpread）
5. 組裝 `AINewsDTO` 集合並回傳 JSON 陣列

---

## 4. 程式流程

| 順序 | Layer | Class / Method（推測） | 動作 |
|------|-------|----------------------|------|
| 1 | Controller | `AINewsController.GetAINews` | 取得路徑參數，呼叫 Service |
| 2 | Service | `IAINewsService.GetSiteAINews` | 建立查詢條件，調用 Provider 查詢 DB，並進行資料合併 |
| 3 | Provider | `IAINewsProvider.GetAINewsByDateAndType` | 執行 Cassandra 查詢，指定 `gdate=date`, `gtype=gameType`, `status=1` |
| 4 | Service | （同上） | 解析 `others` map；可能呼叫 PriceCenterClient 取得盤口資訊 |
| 5 | Service | （同上） | 組裝 DTO，回傳至 Controller |

> 需人工確認：盤口資料（haSpread、ouSpread）的來源實作細節，目前無證據顯示來自 DB 還是外部服務。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB（Cassandra） | `news.ainews_gs` | Read（SELECT） | 查詢 AI 新聞內容，必須以 `gdate` + `gtype` 過濾，並限定 `status=1` |
| Cache | 無 Redis 使用 | — | 本服務無 Redis，若未來加入快取需注意狀態變更時的主動失效 |
| Queue | 無 Kafka 使用 | — | 本流程無佇列操作 |

---

## 6. 重要規則

- **查詢條件強制**：必須帶 `gdate`（分區鍵）及至少 `gtype`（或 `lid`），不可全表掃描
- **狀態過濾**：前台展示新聞僅回傳 `status=1`（已回應），排除 `status=0`（待處理）與 `status=2`（修正中）
- **不可暴露欄位**：`llmsettings`、`bets`、原始 `anwser`/`reanwser` 內的內部格式不應直接暴露，但此 API 的 `anwser` 欄位回傳的是最終校稿版本（依 OpenAPI 定義）
- **敏感資料**：`others` map 中可能包含內部配置，回傳前需過濾；但 `league`、`teamH` 等可安全回傳
- **日期格式**：`date` 必須為 `yyyy-MM-dd`，服務端應驗證格式
- **TTL 規則**：無 Redis 快取，不適用 TTL
- **Transaction**：僅單表讀取，無跨操作事務需求

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `gameType` 不存在（非 SC/BS/BK） | 回傳 HTTP 200 空陣列（或 400 錯誤，依實作） |
| `date` 格式錯誤 | 回傳 HTTP 400 Bad Request |
| 無符合條件的新聞（該日期該球種無 status=1 記錄） | 回傳 HTTP 200 空陣列 |
| Cassandra 連線失敗或逾時 | 回傳 HTTP 500 Internal Server Error |
| `others` map 中缺少必要欄位（如 league） | 該欄位回傳 null，不影響整體回應結構 |
| `anwser` 為空或格式不正確導致解析 predicts 失敗 | 記錄錯誤日誌，對應記錄可能缺預測物件，但仍回傳其他基本資訊 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 正確 `gameType`（SC）與有效日期，有資料 | 回傳 200，陣列包含符合 status=1 的新聞 |
| T2 | API Test | 正確球種但日期無新聞 | 回傳 200，空陣列 |
| T3 | API Test | 無效 `gameType`（如 "XYZ"） | 回傳 200 空陣列（或 400） |
| T4 | API Test | `date` 格式錯誤（如 "01-01-2025"） | 回傳 400 |
| T5 | Permission Test | 無需認證的公開 API | 直接呼叫成功，無 token 要求 |
| T6 | Flow Test | 確認不返回 status=0 或 status=2 的記錄 | 查詢結果僅有 status=1 資料 |
| T7 | Flow Test | `anwser` 內容包含 JSON 可解析為 predicts | 回應中 `predicts` 物件正確組裝 |
| T8 | DB Test | 查詢條件強制 `gdate` + `gtype` | 檢查 provider 層的產生的 CQL 是否包含必要分區鍵 |

---

## 9. 高風險區域

- **高風險 API**：此 API 無認證，若有敏感訊息洩漏風險，需確保 `anwser`、`others` 不回傳內部金鑰或未過濾內容
- **DB 查詢效能**：Cassandra 必須正確使用分區鍵，若因參數錯誤觸發全表掃描，可能造成效能問題
- **Cache consistency**：目前無快取，風險低；若日後引入快取，需注意新聞狀態變更時失效策略
- **資料洩漏**：`llmsettings`、`bets` 等內部欄位不可在 any 回應中出現，API 實作必須強制排除
- **跨服務依賴**：若盤口（haSpread, ouSpread）來自外部服務（如 PriceCenter），其可用性影響回應完整性；應有降級機制（回傳 null 或預設值）

---

## 10. 常見錯誤

- ❌ 查詢時未帶 `gdate` 或只帶 `gtype`，導致 Cassandra 拒絕或掃描全表 → ✅ 必須同時帶上 `gdate` 與 `gtype`
- ❌ 忘記過濾 `status=1`，回傳了待處理或修正中的新聞 → ✅ 前台只顯示已回應狀態
- ❌ 直接將 `anwser` 原樣暴露，未處理可能包含的 Markdown 或內部標籤 → ✅ 依照業務對 `anwser` 做格式化或清洗（若實作中有此步驟）
- ❌ 誤認為此 API 需要商家認證 → ✅ 此為公開 API，無需 token
- ❌ 將 `gameType` 直接對應到不同表（例如對足球預期查 `ainews_lt`） → ✅ GS 版本固定使用 `ainews_gs`

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `GET /api/ainews/{gameType}/{date}` (OpenAPI) |
| DB Table | `news.ainews_gs` (GameSettingSite 為 GS 版本，對應 `ainews_gs`) |
| DB Query Pattern | Cassandra 查詢須含 `gdate` + `gtype`，過濾 `status=1`（gamesettingsite-detail.md｜讀取規則） |
| Response Model | `AINewsDTO` (OpenAPI) |
| 敏感性欄位限制 | `llmsettings`、`bets` 不可回傳（news-detail.md｜不可回傳欄位） |
| 公開端點 | 無 Security Schema (OpenAPI) |