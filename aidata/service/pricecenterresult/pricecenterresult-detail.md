# pricecenter — DB 操作邊界

> 產出時間：2025-03-25 16:10
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效



---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| pricecenter (Cassandra) | writer / reader | Schema：[db/pricecenter.json](../../db/pricecenter.json) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- `accounts_*` 表群（`accounts_AU8`, `accounts_Fortuna888`, `accounts_HGA`, `accounts_HGA2`, `accounts_KKK`, `accounts_KU`, `accounts_NK`, `accounts_Panda`, `accounts_TG`, `accounts_TG999`）：
  - `password`：僅帳號管理 API 可寫入，須經雜湊，不可直接 UPDATE。
  - `enabled`：僅啟用/停用 API 可變更，嚴禁直接 UPDATE。
  - `handler`：僅系統配置流程可修改，外部服務不可寫。
  - `closetime`：僅帳號關閉流程可設置，不得手動修改。
- `actionlog`：**僅 append**，由 API 層插入，禁止 UPDATE / DELETE。
- `sitegames_*` / `sitegames_result_*`：**pricecenter 為 reader，不具寫權**；這些表由數據採集服務 (fetcher) 寫入。

### 讀取規則

- 帳號查詢：必須加 `WHERE enabled = 1`，避免洩漏已停用帳號。
- 登入驗證：須 `WHERE enabled = 1 AND closetime IS NULL`（未關閉帳號才可登入）。
- 比賽數據查詢 (`sitegames_*`)：
  - 依 `status` 過濾：未開始 (`status='0'`) / 進行中 (`status='1'`) 才提供給賠率計算。
  - 額外可依 `gametype` (BS/BK/SC/HL/FL) 篩選對應表。
- `actionlog`：須帶 `date` 分區過濾，避免全表掃描。
- `moneylineodd` 等 map 欄位：需反序列化後依業務規則取用，不可直接透傳。

### 不可回傳欄位

- `password`：任何對外 API 皆不可包含密碼明文或雜湊值。
- `handler`：內部配置參數，禁止洩漏至客戶端。
- `closetime`：僅後台管理可查，一般 API 不應回傳。
- `account` 表中的 `phone`：若未經當事人同意，不可在非必要場景回傳。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET | `pricecenter:sitegame:{site}:{gid}` | 比賽數據初次查詢後緩存 | 30s (短期緩存) |
| GET | `pricecenter:sitegame:{site}:{gid}` | 頻繁讀取比賽數據時 | 避免重複查 Cassandra，降低延遲 |
| DEL | 對應 Key | 收到數據更新事件（fetcher 更新後） | 主動失效，強制重取新資料 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳號建立與密碼雜湊 | `authservice` | pricecenter 僅讀取帳號資訊進行定價與驗證，不處理註冊邏輯 |
| 比賽數據採集與寫入 | `fetcher` | pricecenter 為 readonly 消費者，不負責爬取或寫入 sitegames 表 |
| 賠率計算與風險控管 | `oddsengine` | pricecenter 提供基礎數據，不直接產出最終賠率 |
| 交易紀錄與結算 | `billing` | 僅記錄操作日誌 (actionlog)，無法處理財務流水 |

---

## 常見錯誤

- ❌ 直接 `SELECT * FROM accounts_*` 無 `enabled=1` 過濾 → ✅ 須加上 `enabled=1` 避免讀取停用帳號。
- ❌ 為了方便一次性回傳 `password` → ✅ 永遠排除，即使管理者呼叫也應遮蔽或拒絕。
- ❌ 忘記對 `actionlog` 查詢加上日期分區鍵 → ✅ 必定帶 `date=?` 條件，否則觸發全表掃描與效能問題。
- ❌ 在 pricecenter 內部直接更新 `sitegames_result_*` 的 `resultinfo` → ✅ 應由 fetcher 負責，亂寫會導致賠率計算錯誤。
- ❌ 緩存比賽數據時未設定 TTL → ✅ 必須設定 30s 以下，防止賠率延遲過時。