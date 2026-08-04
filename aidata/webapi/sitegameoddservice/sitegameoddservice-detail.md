# sitegameoddservice — DB 操作邊界

> 產出時間：2025-03-31 10:00
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter (accounts_*, sitegames_{gtype}, games_{gtype}, actionlog) | writer / reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- **accounts_*.password**：僅註冊或密碼變更 API 可寫入；須雜湊儲存，不可明文直接寫入。
- **accounts_*.enabled**：僅管理後台或帳戶啟用/停用 API 可設定；業務邏輯不應直接 UPDATE 此欄位。
- **accounts_*.handler**：僅系統初始化或特定配置管理模組可寫入；一般賠率查詢流程不應修改。
- **accounts_*.phone**：僅使用者個人資料更新 API 可寫入；其他 API 不得異動。
- **accounts_*.closetime**：僅在帳戶關閉操作時寫入，不可由賠率相關邏輯觸發。
- **accounts_*.account**（主鍵）：一旦建立不應更改；僅註冊流程可 INSERT。
- **sitegames_{gtype}** 與 **games_{gtype}**：僅資料餵入（feed）或同步服務（非本服務）可寫入；sitegameoddservice 僅讀取。
- **actionlog**：由操作日誌記錄服務（如管理中心或事件匯流排）寫入；sitegameoddservice 不直接寫入此表。

### 讀取規則

- **帳戶驗證**：查詢 accounts_* 時必須過濾 `enabled=1`，避免對已停用或關閉帳戶進行操作。
- **賽事查詢**：讀取 sitegames_{gtype} 或 games_{gtype} 時，通常會結合 `site`、`gid` 或 `lid` 作為條件；不應回傳所有列。
- **投注歷史**（可能涉及 pricecenter 或 predict）：若使用 accounts_* 記錄帳戶資料，查詢時僅取該帳戶本身，不可跨帳戶掃描。
- **操作日誌查詢**：讀取 actionlog 必須指定分區鍵 `date` 範圍，並配合 `user`、`gametype` 等條件，避免全表掃描；結果應限制筆數。

### 不可回傳欄位

- **accounts_*.password**：任何對外 API（含內部服務間通訊）皆不可回傳；僅用於本地驗證比對。
- **accounts_*.handler**：內部配置細節，對外隱藏。
- **accounts_*.phone**：除非有明確通訊需求，否則不應回傳。
- **actionlog.detail**：操作細節（JSON）可能含有密碼、帳號等敏感資訊，回傳前需過濾或僅提供摘要資訊。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| 無 | 無 | 本服務未使用 Redis 快取帳戶或賽事資料 | N/A |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 帳戶註冊 / 密碼修改 | user / auth service | sitegameoddservice 僅讀取 accounts_* 進行驗證，不處理帳戶生命週期 |
| 賽事資料餵入與同步 | feed service | sitegames_{gtype} 與 games_{gtype} 的寫入由資料源服務負責 |
| 策略投注紀錄（predict 庫） | predict service | sitegameoddservice 僅可能讀取，不負責寫入 strategy_bet_log |
| 站台管理 | admin service | accounts_* 的啟用/停用、電話更新由管理平台處理 |
| 操作日誌記錄 | 事件流 / 管理服務 | actionlog 寫入由對應服務負責；sitegameoddservice 僅讀取 |

---

## 常見錯誤

- ❌ 在賠率查詢流程中直接 UPDATE `accounts_*.password` 或 `accounts_*.enabled` → ✅ 應透過對應管理 API 操作，不可繞過業務邏輯層。
- ❌ 讀取 accounts_* 時未過濾 `enabled=1`，導致已停用帳戶仍可取得賠率 → ✅ 查詢條件必須包含 `enabled=1`。
- ❌ 將 accounts_* 的 password 欄位回傳至前端或外部服務 → ✅ password 僅用於本地雜湊比對，不可回傳。
- ❌ 混淆 pricecenter 與 predict 庫的策略投注紀錄寫入權限 → ✅ 寫入 strategy_bet_log 應由 predict service 負責，sitegameoddservice 不應直接寫入。
- ❌ 未限制 actionlog 查詢的日期範圍，導致全表掃描 → ✅ 查詢 actionlog 必須指定 `date` 條件並搭配 LIMIT。
- ❌ 將 actionlog.detail 欄位直接回傳給前端，可能洩露密碼或帳號資訊 → ✅ detail 應過濾或僅回傳必要摘要。