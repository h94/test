# 更新公告

## 1. 場景目的

提供後台管理員更新 `bulletinboard_sport` 公告內容，包含發佈／下架狀態變更、多語系內文全量覆蓋、顯示期間等。確保狀態機遵守 `0→1→2` 順向流轉，且不可直接回退或篡改 `aid`。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| PUT | `/api/v1/sport/bulletinboard/announcenments/{aid}` | 更新指定公告。需驗證身份。 |

- **Request Body**：符合 OpenAPI `Announcement` schema，包含 `status`、`maintopic`、`text1`、`text2`、`text3`、`announcementmethod`、`starttime`、`endtime`、`sequence` 等欄位。
- **Response**：`200 Success` 或錯誤碼。

---

## 3. 流程總覽

1. 接收 PUT 請求，提取 path 參數 `aid` 與 request body。
2. 驗證呼叫者權限（需登入，後台管理角色）。
3. 查詢 `ads.bulletinboard_sport` 確認 `aid` 存在（`aid` 為分割區鍵只限單筆查詢）。
4. 取得現有記錄，檢查 `aid` 不可被修改（request body 中不應含 `aid`，或若包含則須與路徑一致，否則拒絕）。
5. 狀態機校驗：
   - 若新 `status` 與舊 `status` 相同，允許（同狀態欄位更新，如修改內文）。
   - 否則只允許 `0→1`（草稿→發布）或 `1→2`（發布→下架）。
   - 嚴禁 `1→0`、`2→1`、`2→0` 等逆轉。
6. 更新欄位：
   - `maintopic`、`text1`、`text2`、`text3` 為 `map<text,text>`，以全量覆蓋方式寫入（不可增量）。
   - `announcementmethod` 需為合法枚舉值（0 或 1，但需人工確認與 code semantics 的矛盾）。
   - `starttime`、`endtime` 為 `text`（格式 `yyyy-MM-dd HH:mm:ss`），寫入時應驗證格式。
   - `sequence` 直接覆蓋。
   - `lastup_time` 自動填入當前伺服器時間戳（毫秒）。
   - `addtime`、`aid` 不可修改。
7. 更新記錄至 Cassandra。
8. **⚠️ 需人工確認**：是否需更新 Redis 快取。根據 `advertisingservice-detail.md`，本服務未使用 Redis，但 README 提及快取公告，存在矛盾。若實際有快取，則需同步失效或更新 `SportAdCache` 中的對應公告。
9. 回傳成功。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `SportBulletinBoardController.PutAnnouncement` | 接收 HTTP PUT，提取 `aid`，委派 Service |
| 2 | Auth | `ECFramework.ECService` | 驗證 JWT/Token，取得操作者身份 |
| 3 | Service | `BulletinBoardService.Update` | 組裝更新邏輯 |
| 4 | Provider | `CassandraProvider.GetById(aid)` | 查詢 `aid` 是否存在，取得完整記錄 |
| 5 | Validator | `AnnouncementValidator.ValidateStatusTransition` | 檢查狀態轉換合規 |
| 6 | Provider | `CassandraProvider.Update(announcement)` | 全量覆蓋寫入 Cassandra（excluded `aid`, `addtime`） |
| 7 | （若有快取） | `RedisProvider` | 清除或更新對應公告快取 |

> 實作細節依賴實際 codebase，上述為合理推導。需對照原始碼確認。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `ads.bulletinboard_sport` | Read (SELECT) | 取得現有公告記錄供校驗 |
| DB | `ads.bulletinboard_sport` | Update (UPDATE) | 寫入更新後的所有欄位 |
| Cache | Redis `SportAdCache` | **可能** Delete / Set | 使前台公告列表快取失效（若實際有使用） |
| Queue | Kafka | **無** | 無 Queue 參與本案場景 |

- **需人工確認**：Redis 是否有實際使用。若無，可移除本節。

---

## 6. 重要規則

- **權限限制**：必須後台管理員驗證才可呼叫。
- **欄位限制**：
  - `aid`：分割區鍵，建立後不可修改。若 request body 中包含 `aid`，須與路徑 `aid` 完全相同，否則拒絕。
  - `addtime`：建立時自動填入，API 不允許傳入，更新時亦不可變更。
  - `lastup_time`：系統自動更新，不接受外部傳入。
- **不可暴露資料**：無（公告為公開資訊）。
- **狀態值限制**：狀態機僅允許 `0→1`、`1→2`，同狀態更新允許。
- **不可修改欄位**：`aid`、`addtime`。
- **全量覆蓋規則**：`maintopic`、`text1`、`text2`、`text3`（Map 型態）更新時需傳入完整 Map，不可只傳單一語系鍵值。
- **announcementmethod 枚舉**：`advertisingservice-detail.md` 定義 0=彈窗, 1=橫幅；但 `code semantics` 提到 `AppDefine.AnnouncementMethod` 定義 1=Pattern1,2=Pattern2,3=Pattern3。**需人工確認**以程式碼實際定義為準。
- **Transaction 規則**：Cassandra 單行寫入不支援跨鍵 ACID，無分散式交易需求。
- **Retry 規則**：若寫入失敗，可返回 500，無特殊 retry 機制（由客戶端決定）。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 帳號無權限 | 回傳 401/403，拒絕請求 |
| `{aid}` 不存在於 Cassandra | 回傳 404 Not Found |
| 請求 body 中包含 `aid` 且與路徑不一致 | 回傳 400 Bad Request "aid不可修改" |
| 狀態轉換非法（如 1→0、2→1） | 回傳 400 "Invalid status transition" |
| `announcementmethod` 為非法值（非 0/1 或非 1/2/3） | 回傳 400 "Invalid announcementmethod" |
| `maintopic` 為空 Map 或缺少必要語言鍵 | 回傳 400 "至少要有一個語言條目" |
| `starttime` / `endtime` 格式錯誤 | 回傳 400 |
| Cassandra 寫入失敗 | 回傳 500 Internal Server Error |
| Redis 更新/清除失敗（若使用） | 可能影響前台顯示，需記錄告警，但 API 仍可回傳成功 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| UT-01 | API Test | 正常更新草稿公告內容（status 同為 0） | 200，資料庫內容更新 |
| UT-02 | Flow Test | 草稿（0）→發布（1） | 200，狀態變為 1 |
| UT-03 | Flow Test | 發布（1）→下架（2） | 200，狀態變為 2 |
| UT-04 | Permission Test | 未帶 token 或 token 無效 | 401 |
| UT-05 | Validation Test | 嘗試從 1 設為 0 | 400 |
| UT-06 | Validation Test | 請求 body 中 `aid` 與路徑不同 | 400 |
| UT-07 | Validation Test | `maintopic` 只傳 `{"zh":"..."}`，未傳其他語系，但原有 `en` | 寫入後原 `en` 消失（全量覆蓋）→ 200（符合設計） |
| UT-08 | DB Test | 更新後 `addtime` 未被修改 | 與更新前一致 |

---

## 9. 高風險區域

- **高風險 table**：`ads.bulletinboard_sport`（直接影響前台公告顯示）
- **高風險 API**：`PUT /api/v1/sport/bulletinboard/announcenments/{aid}`（改變公告狀態與內容，可能瞬間影響大量使用者）
- **跨服務資料同步**：若其他服務（如 `productservice`、`livechatservice`）亦讀取此表，需注意狀態變更後的影響（如僅回傳 `status=1` 的公告）
- **Cache consistency**：若 Redis 快取存在，更新後未能即時失效會導致前台顯示舊資料
- **Queue retry**：無佇列參與，暫無
- **Idempotency**：PUT 操作為冪等，同狀態重複請求不會產生副作用

---

## 10. 常見錯誤

- 新人忽略狀態機，直接用 API 設定 `status=0` 嘗試下架已發布公告，觸發後台報錯。
- AI 可能誤以為可以增量更新 `maintopic` Map，實際上 Cassandra Map 操作（若使用 `UPDATE` 語法）可增量，但系統設計意圖為全量覆蓋，若程式使用全量覆蓋，則需對齊。
- 未檢查 `aid` 不可變更，導致 API 允許篡改公告 ID 造成資料錯亂。
- 忘記 `announcementmethod` 枚舉值矛盾，寫入錯誤值導致後續讀取異常。
- 未在更新後清理快取（若有），導致前台仍顯示舊公告。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `PUT /api/v1/sport/bulletinboard/announcenments/{aid}` (OpenAPI) |
| DB | `ads.bulletinboard_sport` (Cassandra schema) |
| 規則 | `advertisingservice-detail.md` — 寫入限制、狀態轉換、Map 全量覆蓋 |
| 規則 | `db/ads-detail.md` — `status` 狀態流轉 |
| 規則 | `code semantics` — `AppDefine.AnnouncementStatus` 定義 0/1/2，`AppDefine.AnnouncementMethod` 矛盾 |
| Redis 矛盾 | `advertisingservice-detail.md` 宣稱未使用 Redis vs `README.md` 提及 `SportAdCache` |
| 全量覆蓋 | `advertisingservice-detail.md` 明確指出 `supportlangs` 需全量覆蓋，推斷 `maintopic` 等 map 亦同（需程式碼確認） |

> 建議人工確認事項：  
> - `announcementmethod` 實際接受值（0/1 或 1/2/3）  
> - Redis 快取是否有實際維護，若無則需更新文件  
> - 寫入操作是否真的有全量覆蓋 map 欄位（查看 CQL 語句）