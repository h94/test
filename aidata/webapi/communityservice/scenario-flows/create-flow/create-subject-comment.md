# 發布主題留言

## 1. 場景目的
會員在已啟用的新彩票論壇主題下發布留言，內容寫入 MeiliSearch `newlottery_comments` 索引，並更新主題的最後留言時間。

---

## 2. 入口 API

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/newlottery/subjects/{subject_id}/comments` | 發布主題留言 |

---

## 3. 流程總覽

1. 接收 HTTP 請求，驗證 AuthKey（由上游 auth/member service 處理）
2. 驗證 `subject_id` 對應的主題存在且狀態為公開（status=1）
3. 驗證留言內容不為空、長度合規
4. 建立留言文件，寫入 MeiliSearch `newlottery_comments` 索引
5. 更新 Cassandra `newlottery_subjects_index` 的 `last_comment_timestamp`
6. 回傳新建留言資料

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `NewLotteryController.post_subject_comment` | 接收請求，提取 `subject_id`、留言內容、AuthKey |
| 2 | Service | `NewLotteryCommentServices.create_comment` | 驗證主題狀態、內容合規，寫入 MeiliSearch，更新主題時間戳 |
| 3 | Provider | `CommunityDataProvider` | 封裝對 MeiliSearch 與 Cassandra 的操作 |
| 4 | Validator | `NewLotteryValidator` | 驗證請求參數（內容非空、長度限制） |

需人工確認：實際 Controller / Service class 名稱因 code evidence 中未明確擷取完整檔案，以 `NewLotteryController` 與 `NewLotteryCommentServices` 為推測名稱。

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| MeiliSearch | newlottery_subjects | Read | 查詢主題是否存在、檢查 status=1 |
| MeiliSearch | newlottery_comments | Write | 寫入新建留言文件 |
| Cassandra | community.newlottery_forums | Read | 驗證所屬論壇 status=1（供 Service 內部判斷） |

**注意**：communityservice 無使用 Redis 快取（依 `communityservice-detail.md` 明確記錄），無 Kafka / Queue 業務操作。

---

## 6. 重要規則

- **主題狀態限制**：僅 `status=1`（公開）的主題可發布留言；隱藏或刪除主題拒絕寫入（依 `communityservice-detail.md` 讀取規則）
- **留言狀態預設值**：`status` 預設為 1（公開），僅作者或管理員可修改（依 `communityservice-detail.md` 寫入限制）
- **內容限制**：留言不可為空，需人工確認字數上限
- **帳號遮蔽**：對外 API 回傳留言列表時必須遮蔽 `account` 欄位（如 `name***`），不可暴露完整帳號（依 `communityservice-detail.md` 不可回傳欄位規則）
- **時間戳**：`create_timestamp` 由服務端產生，不可由客戶端傳入
- **不可修改欄位**：`comment_id`（寫入後不可變）、`subject_id`、`account`
- **Transaction**：無跨資源 transaction；MeiliSearch 寫入為非同步最終一致性

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|---------|
| 主題不存在 | 回傳 404 或自訂錯誤碼 |
| 主題 status=0（隱藏） | 拒絕寫入，回傳權限不足或主題不可用 |
| 留言內容為空 | 回傳 422 驗證失敗 |
| 留言內容超過長度限制 | 回傳 422，提示內容過長 |
| 未帶 AuthKey 或驗證失敗 | 回傳 401，由上游 auth service 攔截 |
| MeiliSearch 寫入失敗 | 回傳 500，記錄錯誤日誌 |
| Cassandra 更新失敗 | 留言已寫入 MeiliSearch，主題時間戳未更新為不一致狀態（需人工確認是否有補償機制） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|---------|
| TC01 | API Test | 正常發布留言 | 201，回傳留言資料，MeiliSearch 可查 |
| TC02 | Flow Test | 主題不存在時發布 | 404 或特定錯誤碼 |
| TC03 | Permission Test | 無 AuthKey 呼叫 | 401 |
| TC04 | Flow Test | 留言內容為空 | 422 |
| TC05 | API Test | 留言後查詢該主題 | 留言出現在留言列表中（status=1） |
| TC06 | Flow Test | 留言成功後主題 `last_comment_timestamp` 更新 | 時間戳更新為近 1 分鐘內 |
| TC07 | Integration Test | MeiliSearch 不可用 | 500，服務正確處理異常 |

---

## 9. 高風險區域

- **高風險 table**：`newlottery_subjects_index` 的 `last_comment_timestamp` 更新與留言寫入非原子操作，留言成功但時間戳未更新將導致列表排序異常
- **Cache consistency**：無 Redis 快取，暫無快取一致性風險
- **Queue retry**：無使用 Queue，若寫入失敗需依賴客戶端重試
- **Idempotency**：無冪等設計，重複 POST 將產生多則相同內容留言
- **跨服務資料同步**：`account` 欄位僅儲存 authkey，需避免直接暴露

---

## 10. 常見錯誤

- ❌ 未檢查主題 `status` 即寫入留言 → 正確應確認 `status=1`
- ❌ 回傳留言時直接暴露 `account` 完整值 → 正確應遮蔽或轉換為顯示名稱
- ❌ 未驗證留言內容長度（例如過長導致索引效能問題）→ 需確認並設定上限
- ❌ 忽略 MeiliSearch 非同步寫入延遲 → 寫入後立即查詢可能暫時查不到，需考量 UX 或等待策略
- ❌ AI 可能誤解此流程需要寫入 Cassandra table → 實際留言本體僅存在 MeiliSearch，Cassandra 僅更新主題時間戳

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API | `POST /api/newlottery/subjects/{subject_id}/comments` |
| 索引 | MeiliSearch `newlottery_comments` |
| 寫入限制 | `communityservice-detail.md`「寫入限制」`newlottery_comments_index.status` |
| 讀取規則 | `communityservice-detail.md`「讀取規則」留言列表查詢 |
| 不可回傳欄位 | `communityservice-detail.md`「不可回傳欄位」`account` |
| 常見錯誤 | `communityservice-detail.md`「常見錯誤」帳號暴露 |
| Service 語意 | Source code semantics Phase1：`NewLotteryCommentServices.create_comments` |