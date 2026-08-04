# 建立公告

## 1. 場景目的

後台人員在廣告服務(AdvertisingService)中建立一筆新的體育公告(bulletinboard_sport)。公告建立後預設為草稿狀態，後續可進行發佈與下架操作。此流程涉及資料寫入 Cassandra 與 Redis 快取更新。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/sport/bulletinboard/announcenments` | 建立一筆體育公告 |

---

## 3. 流程總覽

1.  後台人員攜帶 AuthKey 透過 `ECFramework.ECService` 進行驗證。
2.  Controller 接收 `Announcement` JSON 請求體。
3.  服務層將 `aid` (Partition Key) 寫入；系統自動生成 `addtime` (伺服器當前 Unix 時間戳，**秒級**) 與 `lastup_time`。
4.  驗證 `announcementmethod` 是否為合法枚舉值。
5.  驗證 `maintopic`, `text1`~`text3` Map 結構：Key 為有效語言代碼，至少一個條目。
6.  驗證 `starttime`, `endtime` 格式為 `yyyy-MM-dd HH:mm:ss` 且時間範圍合法。
7.  `status` 預設為 `0` (草稿)。
8.  寫入 Cassandra `ads.bulletinboard_sport`。
9.  寫入完成後，更新 Redis `SportAdCache` 中的公告列表快取。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `SportBulletinBoardController.CreateAnnouncement` | 接收請求，呼叫 Service |
| 2 | Service | `BulletinBoardService.CreateAsync` (推測) | 驗證輸入、組裝資料物件、呼叫 Provider |
| 3 | Provider | `BulletinBoardProvider.InsertAsync` (推測) | 組裝 CQL，寫入 Cassandra `ads.bulletinboard_sport` |
| 4 | Service | `BulletinBoardService.CreateAsync` (推測) | 呼叫 Redis 快取更新邏輯 |
| 5 | Provider | `CacheProvider.SetAnnouncementsAsync` (推測) | 將最新公告列表寫入 Redis `SportAdCache` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| Cassandra | `ads.bulletinboard_sport` | Write | 寫入公告主體資料 (`status=0`) |
| Redis | `SportAdCache` | Write | 更新公告列表快取，供前台查詢使用 |
| Redis | `SportAdCache` | Read | (推測) 寫入快取前讀取現有公告列表以進行合併 |

---

## 6. 重要規則

- **權限限制**：必須通過 `ECFramework.ECService` 驗證 (`✅`)，確認為後台管理人員。
- **不可修改欄位 (`aid`)**：建立後不可修改，為 Partition Key。
- **自動生成欄位 (`addtime`)**：由系統填入**伺服器當前 Unix 時間戳(秒級)**，API 請求體不允許傳入或傳入後將被覆蓋。
- **枚舉值限制 (`announcementmethod`)**：
    - **需人工確認**：存在兩套枚舉定義。
        - 定義 A (`db-usage`)：`0`=彈窗, `1`=橫幅。
        - 定義 B (`code semantics`)：`1`=Pattern1, `2`=Pattern2, `3`=Pattern3。
    - 系統應驗證傳入值為當前實作所接受的枚舉值。
- **狀態限制 (`status`)**：此階段僅能寫入 `0` (草稿)。後續只能正向流轉 (0→1→2)，不可回退或跳躍。
- **多語言 Map 規則 (`maintopic`, `text1~3`)**：
    - Key 必須為有效語言代碼 (如 `zh`, `en`)。
    - Key 不可重複。
    - Map 不可為空，至少需包含一個語言條目。
- **時間格式 (`starttime`, `endtime`)**：必須為 `yyyy-MM-dd HH:mm:ss` 字串格式。`starttime` 不可晚於 `endtime`。
- **Redis 快取一致性**：建立成功後，**必須**更新 Redis 快取，確保持久層與快取層資料同步。若寫入 Cassandra 成功但更新 Redis 失敗，可能導致前台看不到新建公告，需人工確認是否有重試或補償機制。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過身分驗證或權限不足 | 返回 401 Unauthorized 或對應的權限錯誤碼 |
| `announcementmethod` 傳入非法數值 | 返回參數校驗錯誤 (e.g., 400 Bad Request) |
| `maintopic` 或 `text` 欄位為空 Map | 返回參數校驗錯誤 |
| Map 中的語言 Key 為不支援的代碼 | 返回參數校驗錯誤 |
| `starttime` 晚於 `endtime` | 返回參數校驗錯誤，時間區間無效 |
| `starttime` / `endtime` 格式錯誤 | 返回參數校驗錯誤 |
| Cassandra 連線失敗或寫入超時 | 返回系統錯誤 (5xx) |
| Redis 快取更新失敗 | 寫入 Cassandra 成功，但可能返回系統錯誤或僅記錄 Log；**需人工確認**此情況下的業務處理邏輯 (強一致性 vs 最終一致性)。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| `BB-CREATE-01` | API Test | 傳入合法參數，建立公告 | 成功，DB 出現 status=0 紀錄，Redis 快取更新 |
| `BB-CREATE-02` | Validation Test | 傳入不合法的 `announcementmethod` (如 99) | 失敗，返回驗證錯誤 |
| `BB-CREATE-03` | Validation Test | 傳入空白的 `maintopic` Map | 失敗，返回驗證錯誤 |
| `BB-CREATE-04` | Validation Test | `starttime` > `endtime` | 失敗，返回時間區間錯誤 |
| `BB-CREATE-05` | Validation Test | 未帶合法的 Admin Token | 失敗，返回 401 |
| `BB-CREATE-06` | Integration Test | 建立成功後，使用前台 GET API 查詢 (status=1 公告) | 查詢不到新公告 (因狀態為草稿) |
| `BB-CREATE-07` | Flow Test | 建立成功後，進行發佈操作 (status 0→1) | 發佈成功後，前台可查詢到 |

---

## 9. 高風險區域

- **Redis 快取一致性**：
    - 風險：Cassandra 寫入成功後，Redis 更新失敗，導致快取資料陳舊。
    - 建議：需人工確認此處的處理策略 (如：僅記錄錯誤、重試、或有事務補償)。
- **`announcementmethod` 枚舉定義衝突**：
    - 風險：`db-usage` 文件與 `code semantics` 定義不同，若實作與文件不一致，將導致邏輯錯誤或 API 校驗混亂。
    - 建議：必須澄清並統一文件與程式碼的定義。
- **`addtime` 自動生成**：
    - 風險：若分散式伺服器時間不同步，可能導致 Clustering Column 的排序異常。
    - 建議：依賴 NTP 服務確保伺服器時間準確。

---

## 10. 常見錯誤

- ❌ 前端或 AI 誤傳 `addtime` 欄位，以為可以自訂建立時間。
    - ✅ 系統會無視或覆蓋此欄位，統一使用伺服器時間。
- ❌ 將 `announcementmethod` 定義搞混，API 傳入 `0`，但實作只接受 `1`。
    - ✅ 釐清並使用正確的枚舉值 `1` (Pattern1)。
- ❌ 忘記 `status` 初始值為 `0`，直接期望前台能查到。
    - ✅ 新公告為草稿，需經過**發佈**流程 (status=1) 前台才能查詢。
- ❌ 建立公告後未更新 Redis 快取，導致前台資料不一致。
    - ✅ 建立流程中應包含快取更新步驟。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API Route | `README.md`, `OpenAPI` |
| DB Table | `ads.md` -> `ads.bulletinboard_sport` |
| DB Constraints | `advertisingservice-detail.md`, `ads-detail.md` |
| Code Enum Semantics | `code semantics` -> `AppDefine.AnnouncementMethod` (1,2,3) |
| Redis Usage | `README.md` (SportAdCache, 公告快取) |
| Auth Requirement | `README.md` (需要驗證: ✅) |
| DB No Redis | `advertisingservice-detail.md` (本服務未使用 Redis) |
| Permission Rule | `ads-detail.md` (advertisingservice 為 owner) |