# 查詢站台資訊

## 1. 場景目的

管理後台查詢所有已註冊運動網站的基本資訊（如站台名稱、遊戲類型、帳號狀態等），用於系統監控儀表板顯示各站台的啟用狀況與摘要數據。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/system/sites/infos` | 查詢所有站台資訊，需要驗證 |

---

## 3. 流程總覽

1. 管理後台發起 GET 請求至 `/api/v1/system/sites/infos`
2. 通過 ECFramework 驗證（驗證 Token 與後台管理員權限）
3. Controller 調用 Service 層查詢 Cassandra `pricecenter` keyspace 的 `agents` 表
4. 查詢條件：依 `site` 分組，並過濾 `gametype`，取得各站台的基本配置
5. 查詢對應 `accounts_{site}` 表，獲取各站台帳號總數和啟用數量
6. 組合站台資訊（SiteName, GameType, TotalAccounts, EnabledAccounts 等）
7. 回傳站台資訊列表

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Middleware | ECFramework.AuthMiddleware | 驗證 JWT Token，確認後台管理權限 |
| 2 | Controller | SystemController.GetSitesInfos | 接收請求，調用 Service |
| 3 | Service | ISysManagerProvider.GetSites | 查詢 Cassandra 取得站台列表與統計 |
| 4 | Provider | SysManagerProvider | 1) SELECT * FROM pricecenter.agents WHERE site = ? AND gametype = ? (依站台與類型讀取) 2) 對每個 site，SELECT count(*) FROM pricecenter."accounts_{site}" WHERE enabled = 1 |
| 5 | Controller | SystemController | 組裝回應，回傳 List<SiteInfo> |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cassandra | pricecenter.agents | Read | 讀取各站台的基本資訊與 game type 設定 |
| Cassandra | pricecenter.accounts_{site} | Read | 統計各站台啟用帳號數量 |
| Redis | 無 | - | 此場景不使用快取 |
| Kafka | 無 | - | 此場景不涉及訊息佇列 |

---

## 6. 重要規則

- **權限限制**：需要後台管理員權限（需驗證），不可對外公開
- **讀取規則**：依 `site` 與 `gametype` 過濾，不可全表掃描（Cassandra 分區鍵限制）
- **不可暴露資料**：`accounts_{site}.password` 絕不可回傳；`phone` 需脫敏或不可回傳
- **跨品牌隔離**：每一個 `accounts_{source}` 表獨立統計，不可混用
- **狀態過濾**：統計帳號數量時，僅計算 `enabled = 1` 的帳號
- **agents 表條件**：查詢時必須同時指定 `site` 與 `gametype`（分區鍵與叢集鍵）

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未帶有效的 JWT Token | 回傳 HTTP 401 Unauthorized |
| Token 無後台管理權限 | 回傳 HTTP 403 Forbidden |
| Cassandra `agents` 表查詢超時 | 回傳 HTTP 500 Internal Server Error |
| `accounts_{site}` 表不存在（站台未註冊） | 跳過該站台，不影響其他站台查詢 |
| 所有站台皆無資料 | 回傳空列表 `[]`，HTTP 200 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| SYS-001 | API Test | 無 Token 發送 GET 請求 | 回傳 401 |
| SYS-002 | Permission Test | 使用一般會員 Token | 回傳 403 |
| SYS-003 | API Test | 管理員 Token，正常查詢 | 回傳 200，列表包含站台資訊 |
| SYS-004 | Flow Test | 驗證回應結構 | 回應包含 SiteName, GameType, TotalAccounts, EnabledAccounts |
| SYS-005 | Error Test | Cassandra 連線失敗 | 回傳 500，不 crash |
| SYS-006 | DB Test | 部分站台無帳號 | 回傳 TotalAccounts=0，反應真實數據 |

---

## 9. 高風險區域

- **高風險 table**：`pricecenter.agents`、`pricecenter.accounts_*`（帳號資訊，不可洩漏 password）
- **跨服務資料同步**：站台資訊來自 Cassandra，若 `agents` 表由多服務寫入（如 pricecenterservice, tradegameservice），可能出現不一致
- **Cache consistency**：此場景未使用快取，每次查詢直接讀取 Cassandra，需考慮效率與連線數
- **全表掃描風險**：查詢 `agents` 時必須帶 `site` 條件，否則可能導致叢集效能問題

---

## 10. 常見錯誤

- ❌ **查詢 `agents` 時未帶 `site` 過濾條件**：導致全 Keyspace 掃描，Cassandra timeout
- ❌ **回傳 accounts 資訊時包含 `password` 或 `phone`**：嚴重資安漏洞
- ❌ **誤將 `accounts_{site}.enabled = 0` 的帳號計入統計**：數據失準
- ❌ **假設站台資訊來自 MySQL sport DB**：此場景僅讀取 Cassandra pricecenter keyspace
- ❌ **未處理站台無帳號的邊界情況**：不應拋出 exception，應回傳 0
- ❌ **直接操作 `accounts_{source}.handler` map 覆蓋其他機器資訊**：跨服務資料不一致（但此場景僅讀取，風險較低）

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由定義 | ReadMe: `GET /api/v1/system/sites/infos` |
| 入口 Controller | 需人工確認（未在 Phase0/1 code semantics 中找到對應檔案） |
| DB 查詢 | `pricecenter-detail.md`: `agents` 表讀取規則 |
| DB 查詢 | `pricecenter-detail.md`: `accounts_{source}` 表查詢條件 |
| 權限驗證 | ReadMe: 需要驗證（✅） |
| 角色權限 | `pricecentermanage-detail.md`: pricecentermanage 對 pricecenter 為 reader / writer |
| 不可暴露欄位 | `pricecenter-detail.md`: `password` 不可回傳、`phone` 隱私限制 |
| 讀取規則 | `pricecenter-detail.md`: 查詢 `agents` 必須指定 `site` 與 `gametype` |

---

## 12. 需人工確認事項

- Controller 與 Service 的實際類別與方法名稱（code evidence 不足，僅依慣例推測）
- 此 API 是否依賴其他外部服務（如透過 `pricecenterservice` 間接讀取資料）
- 回應格式是否包含 `TotalAccounts`, `EnabledAccounts` 或僅有基本配置（需確認 DTO 定義）
- `agents` 表的寫入權責歸屬（多服務標記為 owner，需確認同步策略）