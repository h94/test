# crawlerservice — DB 操作邊界

> 產出時間：2025-04-09 19:30  
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）  
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter Cassandra | owner | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

> 以下限制適用於 `pricecenter` 下的所有 `accounts_*` 表（如 `accounts_AU8`、`accounts_Fortuna888`、…），這些表結構相同，用於儲存各站點的爬蟲帳號憑證。

### 寫入限制

- **account**：主鍵，僅在帳號註冊 API 建立時可設定，後續不允許直接 UPDATE；變更帳號標識需刪除舊記錄後重建。
- **password**：僅 crawlerservice 內部註冊/更新 API 可寫入；**禁止**明文儲存，必須經服務端雜湊處理後寫入 Cassandra。
- **enabled**：僅爬蟲帳號啟用/停用 API 可修改；不可透過一般更新流程變更。
- **closetime**：僅排程終止任務寫入，不允許手動修改。
- **handler** (`map<text, text>`)：僅系統管理者或爬蟲策略更新 API 能寫入，不可由帳號持有人自行修改；內容可能包含 session cookies 或 tokens，必須確保最小權限。
- **phone**：僅限管理 API（如重置、通知）修改，且修改須記錄操作日誌；不允許前端直接更新。
- **username**：允許管理端透過專用 API 修改，變更不影響登入驗證；建議變更後記錄 audit log（僅限有 `username` 欄位的表，如 `accounts_AU8`、`accounts_Fortuna888`、`accounts_HGA2`、`accounts_Panda`）。

### 讀取規則

- **啟用帳號查詢**：查詢可登入帳號時，必須過濾 `enabled = 1`；`enabled = 0` 或 `closetime` 已過期的帳號不可納入排程。
- **帳號登入驗證**：根據 `account` 與 `password` (雜湊比對) 查詢，且 `enabled = 1`。
- **處理器設定讀取**：`handler` 欄位僅在爬蟲啟動時內部讀取，不對前端 API 暴露。
- **帳號列表讀取**：前台 API 僅能查詢自身帳號；管理端查詢時可依需求過濾 `enabled`、`username` 等條件，但禁止回傳密碼與其他敏感欄位。

### 不可回傳欄位

- **password**：任何對外 API 回應（GET 列表、詳細資訊）皆不可回傳；僅內部登入流程使用。
- **phone**：屬於個人隱私，不應回傳至前端；僅內部密碼重置或通知流程使用。
- **handler**：可能包含 session cookies、tokens 或內部配置，不得暴露於任何對外 API。

---

## Redis

本服務未使用 Redis。

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 爬蟲排程觸發與執行 | scheduler-service | crawlerservice 僅管理帳號憑證與啟用狀態，不負責實際爬蟲任務排程及執行。 |
| 爬蟲結果持久化 | price-result-service | 爬蟲取得的價格資料由獨立服務處理， crawlerservice 不負責寫入價格資料表。 |
| 爬蟲執行日誌記錄（`actionlog`） | logservice | `pricecenter.actionlog` 由日誌服務寫入，crawlerservice 不負責該表的寫入與維護。 |

---

## 常見錯誤

- ❌ 在 API 回應中回傳 `password`、`phone` 或 `handler` 欄位 → ✅ 應過濾後只回傳非敏感欄位（`account`、`username`、`enabled`、`closetime` 等）。
- ❌ 允許前端直接傳遞 `enabled` 值更新狀態（例如 PUT 整份 Account 資料） → ✅ 應透過專用的 enable/disable API，確保業務規則一致性。
- ❌ 未對 `password` 進行雜湊即寫入 Cassandra → ✅ 寫入前必須使用服務端雜湊函數處理，避免明文儲存。
- ❌ 直接 UPDATE `account` 欄位以變更帳號標識 → ✅ 帳號標識不可變更；若需修改，必須刪除原帳號並透過註冊 API 重新建立。