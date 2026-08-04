# 新增公告

## 1. 場景目的
後台管理員透過後台系統新增一筆多語言公告，設定發佈方式（彈窗/橫幅）、有效時間區間，公告內容包含主題與三段多語言文字。此為草稿建立流程，後續可發布。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/v1/advertising/bulletinboard/announcenments` | 新增公告（需驗證） |

---

## 3. 流程總覽

1. 後台前端提交公告資料（包含 `announcementMethod`、`starttime`、`endtime`、`maintopic`、`text1`、`text2`、`text3` 等）。
2. `pricebackendservice` 驗證操作權限（管理後台身分）。
3. 校驗輸入參數：
   - 時間格式與先後順序（`starttime < endtime`）
   - `announcementMethod` 限 0（彈窗）或 1（橫幅）
   - 多語言 map 至少包含一個語言條目，value 不可為空
4. 轉換為下游 `advertisingservice` 接受的 request body。
5. 呼叫 `advertisingservice` 的公告建立 API（REST）進行寫入。
6. `advertisingservice` 寫入 `ads.bulletinboard_sport`，自動產生 `aid` 與 `addtime`，初始 `status = 0`（草稿）。
7. 回傳成功結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `AdvertisingController.CreateAnnouncement` | 接收 request，驗證身分 |
| 2 | Validator | `AnnouncementValidator` (推測) | 檢查必填欄位、時間格式、announcementMethod 範圍、多語言至少一語系 |
| 3 | Service | `IAdvertisingService.CreateBulletinBoardAnnouncement` (推測) | 轉換 DTO，呼叫 Provider |
| 4 | Provider | `AdvertisingProvider.CreateAnnouncementAsync` (推測) | 透過 HTTP client 對 `advertisingservice` 發送 POST |
| 5 | (下游) advertisingservice | 對應的 Controller/Service | 寫入 `ads.bulletinboard_sport`，設定 `status = 0`、`addtime` 為系統時間 |

> ⚠️ 實際層級名稱需人工確認，因缺少程式碼 evidence；但 BFF 層只做轉發，不涉及 DB 操作。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 | 備註 |
|------|------|------|------|------|
| DB | `ads.bulletinboard_sport` | INSERT | 寫入公告資料 | 由 `advertisingservice` 執行；`aid`、`addtime` 自動生成 |
| Redis | 無 | - | - | 此流程不使用快取 |
| Kafka | `applogs` | Publish | 記錄操作日誌 | 由 `pricebackendservice` 本身日誌框架推送，非業務行為 |

---

## 6. 重要規則

- **權限**：僅限管理後台已驗證身分者呼叫；OpenAPI 標記「✅ 需要驗證」。
- **aid**：建立後不可修改，由 `advertisingservice` 自動生成（UUID）。
- **addtime**：不允許前端傳入，由服務器時間寫入。
- **announcementMethod**：只允許 `0`（彈窗）或 `1`（橫幅）。非法值應拒絕。
- **starttime / endtime**：
  - 格式：`yyyy-MM-dd HH:mm:ss`
  - 校驗：`starttime < endtime`
- **多語言欄位**（maintopic, text1, text2, text3）：
  - 型別 `map<text, text>`，key 為語言代碼
  - 至少一個 key，且對應 value 不可為空字串
  - 建立時為全量寫入，無需擔心覆蓋（不同於 UPDATE）
- **status**：建立時強制設為 `0`（草稿），不可由前端直接設定為 `1`；後續透過發布 API 變更狀態。
- **不可修改欄位**：`aid`、`addtime`。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 未通過後台驗證 | 401 或 403 |
| `announcementMethod` = 2 | 400 - 參數無效 |
| `starttime` ≥ `endtime` | 400 - 時間區間不合法 |
| 所有多語言 map 為空或全為空字串 | 400 - 至少一個語系需填入內容 |
| `advertisingservice` 無回應或超時 | 503 / 500，由 BFF 回傳錯誤 |
| `starttime` 格式錯誤 | 400 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|----------|------|------|----------|
| ANN-01 | API | 正常新增公告（英文/繁體中文兩語系） | 200，DB 出現一筆 status=0 的記錄 |
| ANN-02 | Validation | `announcementMethod` 設為 5 | 400 |
| ANN-03 | Validation | `endtime` 早於 `starttime` | 400 |
| ANN-04 | Validation | 多語言 map 為 `{}` | 400 |
| ANN-05 | Permission | 無 auth header 呼叫 | 401/403 |
| ANN-06 | Flow | 新增後查詢公告清單 | 該公告出現在草稿區（過濾 status=0） |

---

## 9. 高風險區域

- **aid 不可控**：前端不可指定 `aid`，避免 UUID 碰撞或惡意偽造。
- **時間區間依賴字串比較**：若下游服務未正確解析時間，可能導致公告在錯誤時間顯示。需確保 `advertisingservice` 與前端的時區與格式一致。
- **多語言 map 結構**：若未來需要增量更新，直接全量覆蓋是安全的；但 UPDATE 時若只提供部分語系會清空其他語系，須特別注意（不在本場景內）。
- **後續狀態流轉**：`status=0` 草稿 → `status=1` 發布，不可跳躍；此規則由 `advertisingservice` 確保，但 `pricebackendservice` 應避免提供直接建立已發布公告的介面。

---

## 10. 常見錯誤

- ❌ 前端試圖傳入 `aid` 或 `addtime` → 應忽略或拒絕這些欄位。
- ❌ 將 `announcementMethod` 誤認為 string 或 布林值 → 必須為整數 0 或 1。
- ❌ 未檢查 `starttime`/`endtime` 格式，直接傳給下游 → 可能產生幽靈公告或無法顯示。
- ❌ 以為 `pricebackendservice` 有權限直接寫入 Cassadra → 本服務為 BFF，完全透過下游 API。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 路由 | README.md：POST `/api/v1/advertising/bulletinboard/announcenments` |
| 需要驗證 | README.md：✅ |
| 公告表結構 | DB schema: `ads.bulletinboard_sport` |
| 欄位規則 | `db/ads-detail.md`：`aid` 不可改、`addtime` 自動產生、`announcementMethod` 枚舉、`starttime`/`endtime` 格式、`status` 狀態流轉 |
| 多語言限制 | `db/ads-detail.md`：至少一個語言條目，不可空 map |
| 不直接存取 DB | README 職責段落：無直接 DB 存取，透過下游微服務 |
| 下游服務 | README 相依服務：`advertisingservice` |
| 日誌 | README 技術棧：Kafka `applogs` |