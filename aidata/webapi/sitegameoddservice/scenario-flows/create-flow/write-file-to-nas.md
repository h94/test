# 透過 SFTP 寫入檔案至 NAS

## 1. 場景目的
提供內部輔助工具 API，允許其他服務或管理員將指定檔案透過 SFTP 上傳至 NAS 儲存。此功能用於支援運維（如備份配置、落盤日誌）或跨服務資料交換之非核心業務流程。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/write/file` | 接收檔案相關資訊，由服務端透過 SFTP 寫入至 NAS（實際請求參數需人工確認） |

---

## 3. 流程總覽

1. 接收包含 SFTP 連線資訊、目標路徑與檔案內容之 request
2. 驗證請求參數與權限（驗證規則與權杖來源需人工確認）
3. 建立與 NAS 之 SFTP 連線（依賴 pysftp）
4. 執行檔案上傳（Write）
5. 關閉 SFTP 連線
6. 回傳上傳結果（成功或失敗）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | 需人工確認 | 接收請求，初始化 SFTP 連線參數 |
| 2 | Validator | 需人工確認 | 驗證目標路徑合法性，防止路徑遍歷攻擊（推測） |
| 3 | Service / Provider | 需人工確認 | 調用 pysftp 實作檔案傳輸邏輯 |
| 4 | Transfer | pysftp.Connection | 建立連線、切換目錄、上傳檔案 |
| 5 | Controller | 需人工確認 | 封裝回應並返回給調用方 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| 無 | DB (pricecenter / predict) | 無操作 | 此流程為檔案傳輸輔助功能，不涉及業務資料庫讀寫 |
| 無 | Redis / Kafka | 無操作 | 此流程為 sync I/O，未觸發異步 Queue 或 Cache 更新 |

---

## 6. 重要規則

- **權限限制**：
  - 基於 README 描述，此為**輔助工具 API**，可能僅限內部管理網路或特定服務調用（需人工確認）
  - 調用方需提供有效的 SFTP 憑證（帳號/密碼），不可暴露內部服務預設帳號 (Evidence: 技術棧包含 pysftp，推測需外部傳入 Host/Account)
- **欄位限制**：
  - 不可在請求中回傳或嘗試寫入 `accounts_*.password` (Evidence: sitegameoddservice-detail.md)
- **不可暴露資料**：
  - SFTP 密碼在日誌中需脫敏處理（需人工確認實作）
- **TTL 規則**：無
- **Transaction 規則**：無 DB 交易，但 SFTP 寫入為單次 atomic 動作
- **Retry 規則**：需人工確認
- **狀態值限制**：檔案上傳僅為單次動作，無狀態流轉
- **不可修改欄位**：此 API 不可用於修改資料庫中的任一 `accounts_*` 欄位 (Evidence: sitegameoddservice-detail.md)

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| SFTP 主機不可達或拒絕連線 | 回傳連線失敗錯誤，捕捉 ConnectionException |
| 帳號密碼驗證失敗 | 回傳認證錯誤，捕捉 AuthenticationException |
| 目標路徑不存在 | 捕捉 FileNotFound 或權限異常，回傳失敗 |
| NAS 磁碟空間不足 | 捕捉 IOError，回傳儲存空間不足 |
| 檔案傳輸中連線中斷 | 捕捉傳輸異常，避免殘留不完整檔案（需人工確認是否有 TempFile 機制） |
| 請求參數缺漏（Host/Port/Path） | 回傳參數驗證失敗 400 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| SFTP-01 | Integration Test | 正常連線並上傳合法檔案 | 檔案成功寫入 NAS，回傳成功 true |
| SFTP-02 | Permission Test | 使用無效 SFTP 憑證 | 捕捉異常，回傳認證失敗 |
| SFTP-03 | Flow Test | 寫入超大檔案 | 處理正常或觸發 timeout（需人工確認限制） |
| SFTP-04 | API Test | 請求主體包含非法路徑（如 `../../etc/passwd`） | 過濾路徑並拒絕寫入 |

---

## 9. 高風險區域

- **高風險 API**：`/api/write/file` — 若未做好路徑校驗（Path Traversal），攻擊者可覆蓋系統檔案或植入惡意腳本。
- **憑證洩漏**：若 SFTP 帳密記錄在服務端日誌中且未脫敏，可能導致 NAS 資料大面積洩漏。
- **Cache consistency**：不適用。
- **Idempotency**：重複請求可能導致檔案覆蓋（需確認是否有去重或版本號機制）。

---

## 10. 常見錯誤

- **新人容易犯錯**：
  - 直接在 Controller 層組裝路徑，未過濾 `../` 等跳脫字元，造成 Path Traversal。
  - 沒有正確捕捉 pysftp 連線底層的 socket 錯誤，導致 API 無回應或回傳 500。
- **AI 容易誤解**：
  - 誤以為此流程需要驗證 DB 中的 accounts 表。實際上它只是輔助工具，與業務帳號驗證不同（除非需要自定義 API Key）。
- **常見漏檢查項目**：
  - 無人監控 SFTP 連線池洩漏（沒有正確 close connection）。
  - 未判斷目標檔案是否已存在（未定義是「覆蓋」還是「拒絕」）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路徑 | README.md — 輔助工具 API (`/api/write/file`) |
| SFTP Library | README.md — pysftp |
| 服務角色 | sitegameoddservice-detail.md — 僅在特定配置下可寫入 `handler`；不會異動 `password`/`phone`/`enabled` |
| 讀寫限制 | sitegameoddservice-detail.md — `sitegameoddservice` 對 `pricecenter.accounts_*` 僅為 reader，寫入權限嚴格限制 |