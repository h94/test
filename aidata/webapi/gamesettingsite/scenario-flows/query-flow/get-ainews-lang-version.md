# 取得AI新聞多語版本

## 1. 場景目的

根據特定賽事日期 (`date`) 與賽事系統編號 (`gid`)，查詢 AI 新聞的其他語言版本，回傳一個 key-value 物件，其中 key 為語言代碼、value 為對應的 AI 新聞內容。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| GET | /api/ainews/lang/{date}/{gid} | 取得 AI 新聞的多語版本 |

---

## 3. 流程總覽

1. 接收請求，擷取路徑參數 `date` 與 `gid`。
2. (需人工確認) 驗證呼叫來源權限 (business validation)。
3. 查詢 `news.ainews`、`news.ainews_gs` 或 `news.ainews_lt` 中，符合 `gdate` = `date` 且 `gid` = `gid` 且 `status` = 1 的記錄。
4. 從查詢結果中的 `others` map 欄位提取各語言版本的新聞內容。
5. 組裝 key-value 物件回傳 (key 為語言，value 為內容)。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | AINewsController.GetNewsLang | 接收 GET 請求，呼叫 Service |
| 2 | Service | AINewsService.GetNewsLang | 協調查詢邏輯，決定查詢目標表 |
| 3 | Provider | AINewsProvider.GetByDateAndGid | 執行 Cassandra 查詢 |
| 4 | Transfer | (DTO Mapping) | 從 `others` map 轉為 API 回傳格式 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | news.ainews | Read | 查詢指定日期與賽事的 AI 新聞資料 |
| DB | news.ainews_gs | Read | 同上 (針對 GS 站台版本) |
| DB | news.ainews_lt | Read | 同上 (針對 LT 站台版本) |
| Queue | N/A | N/A | 本流程未使用 Queue |

---

## 6. 重要規則

- **查詢條件限制**：必須帶入 `gdate` (分區鍵) + `gid` 進行查詢，以避免全表掃描 (Cassandra 禁止，會導致效能問題或錯誤)。
- **狀態過濾**：只查詢 `status = 1` 的記錄，確保只回傳已由 LLM 生成完成且未被修正的內容。
- **不可回傳欄位**：
  - `anwser` / `reanwser`: 原始 AI 生成內容，對外不直接暴露。
  - `llmsettings`: LLM 內部設定，不可回傳。
  - `bets`: 內部投注數據，不可回傳。
- **路徑參數驗證**：
  - `date` 格式必須為 `yyyy-MM-dd`。
  - `gid` 不可為空。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| `date` 格式錯誤 | 回傳 HTTP 400 Bad Request |
| `gid` 為空 | 回傳 HTTP 400 Bad Request |
| DB 查詢無符合記錄 (無此賽事或無此語系) | 回傳空物件 `{}` |
| 查詢時未帶入 `gdate` (Cassandra 限制) | 可能觸發服務端內部錯誤或因全表掃描被禁止 |
| 查詢到的記錄 `status` 不為 1 | 該記錄不應被回傳，視為查無資料 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TC-ANL-01 | API Test | 提供有效 `date` 與 `gid`，且存在 `status=1` 的多語系 AI 新聞 | 回傳 200 OK，內容為多語系 key-value |
| TC-ANL-02 | API Test | 提供有效 `date` 與 `gid`，但無任何 AI 新聞 | 回傳 200 OK，內容為空物件 `{}` |
| TC-ANL-03 | API Test | 提供有效 `date` 與 `gid`，但記錄 `status=0` | 回傳 200 OK，內容為空物件 `{}` |
| TC-ANL-04 | API Test | `date` 格式錯誤 (e.g., `2025/04/10`) | 回傳 400 Bad Request |
| TC-ANL-05 | API Test | `gid` 為空 | 回傳 400 Bad Request |
| TC-ANL-06 | Integration Test | 確認回傳的內容中，不包含 `anwser`, `reanwser`, `llmsettings`, `bets` | 回傳物件的所有 value 均為純內容，無內部數據 |
| TC-ANL-07 | Flow Test | 資料庫中存在多筆同 `gid` 但不同 `gtype` 或 `lid` 的 ainews (跨球種賽事) | 需確認查詢是否能正確定位到該 `gid` 的所有多語新聞 |
| TC-ANL-08 | API Test | 權限不足 or 未登入 | 需人工確認，依照系統權限機制預期應為 401 或 403 |

---

## 9. 高風險區域

- **高風險 DB**：`news.ainews` 系列表，特別是查詢條件未包含分區鍵 `gdate` 時，會導致 Cassandra 節點高負載或查詢直接被拒。
- **Cache consistency**：本服務目前**未使用 Redis** 快取 AI 新聞。若未來加入快取，需確保 LLM 回調或後台修正 (`status` 變更) 時，能主動清除相關快取，避免提供過時或未修正的新聞。根據 `news-detail.md`，目前 news DB 未使用 Redis。
- **資料結構**：
  - `others` (map<text, text>) 的結構由業務協定約束，若上游服務 (如 LLM 回調服務) 寫入了非預期的鍵值對，可能導致回傳內容異常或缺失。
  - `anwser` / `reanwser` 即使未直接回傳，在服務內部流轉時也應注意避免誤洩漏至日誌或其他中介層。

---

## 10. 常見錯誤

- ❌ 查詢 `ainews` 或相關表時，未帶入 `gdate` 條件，只使用 `gid` 查詢。這會導致 Cassandra 全表掃描，是常見且嚴重的錯誤。
- ❌ 忘記過濾 `status` 欄位，將 `status=0` (待處理) 或 `status=2` (修正中) 的記錄一併回傳，導致前台顯示未完成或錯誤的內容。
- ❌ 直接將 `anwser` 或 `reanwser` 欄位的值回傳給前端，違反了資訊遮蔽的規則。
- ❌ 假設一個 `gid` 只對應唯一一條記錄。由於 `gtype` 和 `lid` 也是主鍵的一部分，同一個 `gid` 可能在不同球種或聯賽下存在，查詢時需考量此情況。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | AINewsController.GetNewsLang |
| DB | news.ainews (Schema) |
| DB 規則 | gamesettingsite-detail.md / news-detail.md |
| Code | AINewsService / AINewsProvider |
| Schema | ainews.others (map<text, text>) |

---

## 12. 需人工確認

- 此 API 的具體目標查詢表 (`ainews` / `ainews_gs` / `ainews_lt`) 是如何根據 `gid` 或來源服務 (`gamesettingsite`) 決定的？可能由 `IAINewsProvider` 的實作決定。
- 回傳的 key-value 結構中，key 是語系代碼 (e.g., `zh-TW`, `en`)，還是 `gtype` 或 `lid`？從 API 規格中 `additionalProperties` 無法確定確切語意，需由程式碼或實際呼叫確認。
- 此 API 是否需要驗證？從 OpenAPI 規格中未看到 Authorization header。