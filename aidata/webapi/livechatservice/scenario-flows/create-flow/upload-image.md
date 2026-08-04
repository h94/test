# 上傳圖片（JPG/PNG/GIF/BMP）

## 1. 場景目的
讓客服人員或使用者透過 API 上傳圖片檔案（JPG、PNG、GIF、BMP），服務端將檔案儲存至指定目錄並回傳可存取的路徑，供後續聊天訊息或其他功能使用。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/channel/upload` | 上傳一個或多個圖片檔案 |

---

## 3. 流程總覽

1. 接收 HTTP POST 請求，Content-Type 為 multipart/form-data。
2. 解析表單欄位 `files`（檔案陣列）與可選的 `fields`（額外參數）。
3. 對每個上傳的檔案執行副檔名檢查（僅允許 `.jpg`、`.jpeg`、`.png`、`.gif`、`.bmp`，不區分大小寫）。
4. 依當前日期（`yyyyMMdd`）建構目標儲存路徑：`wwwroot/downloads/{yyyyMMdd}/livechat/`。
5. 若目標目錄不存在則建立。
6. 為每個檔案產生唯一檔名（例如 GUID 或時間戳後綴），保留原始副檔名。
7. 將檔案寫入磁碟。
8. 透過 KafkaLogger 記錄上傳事件（供日誌與監控）。
9. 成功後回傳每個檔案的公開存取 URL（或相對路徑）；若失敗則回傳錯誤訊息。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `LiveChatController.Upload` | 接收 multipart/form-data 請求，取得 `IFormFileCollection` 與 `fields` |
| 2 | Controller | 同 | 呼叫驗證函式檢查檔名副檔名是否在白名單內 |
| 3 | Service（推測） | `ImageService.SaveFiles` 或 Controller 內直接處理 | 依 `yyyyMMdd` 組合路徑，呼叫 `Directory.CreateDirectory` 確保目錄存在 |
| 4 | Service | 同 | 為每個檔案產生唯一檔名（例：`Guid.NewGuid() + 副檔名`），使用 `FileStream` 寫入磁碟 |
| 5 | Service | 同 | 呼叫 `IKafkaLogger.LogInformation` 寫入上傳成功紀錄（含檔名、時間、操作者等） |
| 6 | Controller | 同 | 組建回傳 JSON，包含檔案相對路徑或完整 URL；若過程中發生例外，回傳 HTTP 500 或 400 |

> **注意**：上述 Service 層為合理推測，實際可能直接於 Controller 實現；需人工確認實際類別與方法名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Kafka | KafkaLogger | Publish | 記錄上傳事件的稽核日誌 |
| - | - | - | 本流程不使用 DB、Redis、或其他外部儲存 |

---

## 6. 重要規則

- **副檔名白名單**：僅接受 `.jpg`、`.jpeg`、`.png`、`.gif`、`.bmp` (大小寫不敏感)；其他副檔名一律拒絕。
- **檔案儲存路徑**：固定為 `wwwroot/downloads/{yyyyMMdd}/livechat/`，其中 `yyyyMMdd` 為伺服器本地時間（容器時區 `Asia/Taipei`）。
- **檔名唯一性**：必須使用唯一識別碼（如 GUID）加上原始副檔名，禁止直接使用原始上傳檔名，防止覆蓋與路徑遍歷攻擊。
- **目錄權限**：容器內 `wwwroot/downloads` 目錄必須具有寫入權限；生產環境建議掛載外部 Volume 以持久化檔案，避免容器重建時遺失。
- **檔案內容校驗**（需人工確認）：程式可能進一步檢查檔案內容的魔術位元組（magic bytes），確保副檔名與實際內容相符，但此規則未在現有文件中載明。
- **請求大小限制**：未在 OpenAPI 中明確定義，需人工確認是否有 `MaxRequestBodySize` 或 `RequestSizeLimit` 設定。
- **回傳格式**：回傳內容推測為 JSON 字串陣列（每個檔案一個 URL），具體格式需人工確認。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 檔案副檔名不在白名單 | 回傳 HTTP 400 Bad Request，錯誤訊息說明副檔名不符 |
| 未上傳任何檔案（files 為空） | 回傳 HTTP 400 Bad Request |
| 檔案大小為 0 | 回傳 HTTP 400 Bad Request |
| 目標目錄無法建立或寫入 | 回傳 HTTP 500 Internal Server Error，並記錄例外 |
| 磁碟空間不足 | 回傳 HTTP 500 Internal Server Error，並記錄例外 |
| 檔案名稱包含非法字元（如 `..` 路徑遍歷） | 服務應先過濾或拒絕，若未處理可能導致安全性問題；需人工確認保護機制 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UP-01 | API Test | 上傳一張正常 JPG 圖片 | 成功回傳 200，並可於目標路徑下找到檔案 |
| UP-02 | API Test | 上傳一張 PNG 圖片 | 成功回傳 200 |
| UP-03 | Validation | 上傳副檔名為 .exe 的檔案（模擬惡意檔案） | 回傳 400 錯誤，明確指出副檔名不被允許 |
| UP-04 | Flow Test | 上傳時目標日期目錄不存在 | 自動建立目錄，檔案正確儲存 |
| UP-05 | Permission Test | 容器內 `wwwroot` 目錄設為唯讀 | 回傳 500，錯誤訊息反映寫入失敗 |
| UP-06 | API Test | 上傳多個檔案（混合有效與無效副檔名） | 有效檔案上傳成功，無效檔案個別回報錯誤（或全部拒絕，需確認實作） |
| UP-07 | Security | 檔案名稱包含 `../` 試圖逃逸目錄 | 應被拒絕或自動清除非法字元，最終檔案仍位於預期目錄內 |
| UP-08 | Kafka Log | 上傳成功後檢查 Kafka 日誌 | 可觀察到包含檔名、時間的記錄 |

---

## 9. 高風險區域

- **檔案系統寫入權限**：容器化環境若未正確掛載 Volume 或未設定寫入權限，將直接導致功能無法使用。
- **磁碟空間耗盡**：長期上傳可能填滿磁碟，需搭配監控與定期清理機制（本服務未實作，應由維運端處理）。
- **路徑遍歷攻擊**：若未過濾檔名中的特殊字元（如 `..`、`/`），攻擊者可將檔案寫入任意目錄。
- **禁止上傳惡意腳本**：僅依靠副檔名過濾不完全安全，若程式未檢查檔案內容（魔術數值），攻擊者可能上傳包含 script 的「圖片」造成儲存型 XSS 等風險（如 SVG）。**需人工確認是否有內容驗證**。
- **持久化**：若未掛載 Volume，容器重建後所有上傳檔案將遺失。
- **請求大小**：未明確設定大小限制可能造成服務因巨量檔案而崩潰。實際設定需人工確認。

---

## 10. 常見錯誤

- **副檔名比對不嚴謹**：只比對 `.jpg` 但忽略 `.jpeg` 或大小寫差異，導致合法檔案被拒絕。
- **未建立目錄**：直接寫入檔案而不先呼叫 `Directory.CreateDirectory()`，導致 `DirectoryNotFoundException`。
- **使用原始檔名**：直接儲存使用者提供的檔名，可能覆蓋同名舊檔或引發路徑遍歷漏洞。
- **時區錯誤**：路徑中的日期若取自 UTC 時間而非容器時區，在某些時段會產生錯誤的日期目錄。
- **回傳 URL 格式錯誤**：可能不小心回傳了內部容器路徑而非對外 URL，導致前端無法正確載入圖片。
- **忽略 Kafka 寫入失敗**：若 Kafka 寫入失敗但檔案已儲存，可能失去稽核紀錄；需確認是否採用非同步記錄與容錯機制。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | OpenAPI: `POST /api/v1/channel/upload` |
| 功能說明 | README.md 主要功能「圖片上傳」段落 |
| 儲存路徑 | README.md：「存放於 wwwroot/downloads/{日期}/livechat 目錄」 |
| 副檔名限制 | README.md：「驗證副檔名（僅允許 JPG、PNG、GIF、BMP）」 |
| 容器時區 | README.md：「Dockerfile 已設定 TZ=Asia/Taipei」 |
| Kafka 記錄 | README.md 技術棧：Kafka (KafkaLogger)；來源原始碼中推測會使用 IKafkaLogger |
| 目錄權限 | README.md 組態與部署注意：「需確保容器內該目錄可寫入；若需持久化，建議掛載外部 Volume」 |
| 具體邏輯實作 | 需人工確認 Controller/Service 類別與名稱，以及檔案內容驗證、請求大小限制等細節 |

**需人工確認項目**：
- 是否對檔案內容進行魔術位元組檢查
- 是否限制上傳檔案大小（`MaxRequestBodySize` 或 Attribute）
- 失敗時對部分成功（多檔案上傳中部分失敗）的處理策略
- 回傳的 URL 格式（相對路徑 vs 完整 URL）
- 實際的 Controller 類別名稱與 Service 層劃分