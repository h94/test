# 刪除賠率閥值設定

## 1. 場景目的
移除特定層級（運動／聯盟／遊戲）的賠率閥值設定，並確保下游同步服務能感知變更，實現監控規則的即時撤除。

---

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| DELETE | /api/oddthreshold/{layer}/{key} | 根據層級與唯一鍵刪除閥值。**註：確切路徑需人工確認，OpenAPI 片段未完整呈現** |

根據 README 賠率閥值支援「新增、修改、刪除與同步」，以及 DB 中包含三張設定表，推測可能路徑如：
- 運動層級：`DELETE /api/oddthreshold/sport/{game_type}`
- 聯盟層級：`DELETE /api/oddthreshold/league/{sitelid}/{source}`
- 遊戲層級：`DELETE /api/oddthreshold/game/{sitegid}/{source}`

需人工確認實際路由定義。

---

## 3. 流程總覽
1. 接收 DELETE 請求，含層級參數與唯一鍵。
2. 驗證請求參數（層級是否存在、鍵值格式）。
3. 查詢對應的 `oddthreshold_*_setting` 表，確認記錄存在。
4. 執行 `DELETE` 移除記錄。
5. 將舊值寫入 `threshold_changelog`（記錄 `old_value`，`new_value` 為 `NULL`）。
6. 插入一筆 `threshold_sync_pending`（table_name、record_key），狀態為 `pending`。
7. 回傳成功訊息（200 或 204）。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `OddThresholdController.delete` | 解析路徑參數，呼叫 Service |
| 2 | Validator | `OddThresholdValidator.validate_delete` | 參數格式、層級合法性檢查 |
| 3 | Service | `OddThresholdService.delete` | 組合刪除邏輯，控管交易 |
| 4 | Provider | `OddThresholdProvider.get_record` | 查詢目標記錄是否存在 |
| 5 | Provider | `OddThresholdProvider.delete_record` | 執行 DELETE SQL |
| 6 | Provider | `ThresholdChangelogProvider.insert` | 寫入 changelog |
| 7 | Provider | `ThresholdSyncPendingProvider.enqueue` | 寫入 pending sync 記錄 |
| 8 | Transfer | 回應物件組裝 | 回傳刪除結果 |

（部分類別名稱乃基於命名慣例推斷，實際以原始碼為準）

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `oddthreshold_sport_setting` | Delete | 移除運動層級閥值 |
| DB | `oddthreshold_league_setting` | Delete | 移除聯盟層級閥值 |
| DB | `oddthreshold_game_setting` | Delete | 移除遊戲層級閥值 |
| DB | `threshold_changelog` | Insert | 稽核記錄（old_value 為被刪除的內容） |
| DB | `threshold_sync_pending` | Insert | 排入同步佇列等待 workers 消費 |
| Queue | (間接) Kafka | Publish | Workers 讀取 sync_pending 後發送到 Kafka，供下游同步 |

Redis 於此刪除流程無直接使用。

---

## 6. 重要規則
- **權限限制**：需具備後台操作權限的 `operator_account`（從 request payload 或 token 解析），記錄於 changelog。
- **層級對應**：運動層級唯一鍵為 `game_type`；聯盟層級為 `sitelid + source`；遊戲層級為 `sitegid + source`（依表結構推斷）。
- **不可暴露欄位**：`threshold_changelog` 僅記錄 id、table_name、record_key、play_mode、old_value、new_value(NULL)、operator_account、changed_at，不應洩漏額外敏感資料。
- **Transaction 規則**：刪除記錄、寫 changelog、插入 sync_pending 應在同一資料庫交易中完成，確保一致性。
- **TTL 規則**：`threshold_sync_pending` 記錄由排程每日清理，無強制處理期限（僅標記 done 後清理）。
- **同步通知**：不直接在此 API 發送 Kafka，而是寫入佇列表，由背景 Worker (`Tasks.py`) 排程處理（需人工確認 worker 實作細節）。
- **不可修改欄位**：`created_at`、`updated_at` 由資料庫自動維護。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| 目標記錄不存在 | 回傳 404，錯誤訊息說明 record not found |
| 傳入不存在或無效的層級 | 回傳 400，參數錯誤 |
| 缺少 operator_account | 回傳 401 或 403 |
| 資料庫寫入 changelog 失敗 | 交易 rollback，回傳 500 |
| 資料庫寫入 sync_pending 失敗 | 交易 rollback，回傳 500 |
| 同時有重複刪除請求 | 第二次請求應得到 404（或 409，依設計），不應殘留孤兒 changelog |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | API Test | 合法刪除既有運動層級閥值 | 200／204，記錄消失，changelog 與 sync 寫入 |
| T2 | API Test | 刪除非存在記錄 | 404 |
| T3 | Permission Test | 未攜帶有效 operator_account | 401 或 403 |
| T4 | Flow Test | 驗證 changelog 內容（old_value 等於原始值） | 正確寫入 |
| T5 | Flow Test | 驗證 sync_pending 記錄被排程消費 | 背景 worker 處理後狀態變更／發送 Kafka |
| T6 | API Test | 刪除聯盟層級閥值 | 正確識別 sitelid + source |
| T7 | API Test | 刪除遊戲層級閥值 | 正確識別 sitegid + source |

---

## 9. 高風險區域
- **高風險 table**：`oddthreshold_*_setting`（直接刪除可能影響監控，需謹慎授權）
- **跨服務資料同步**：刪除後若 sync 失敗，下游仍保留舊閥值，導致不一致
- **Transaction**：delete、changelog、sync enqueue 必須 atomic，否則遺漏變更追蹤
- **Cache consistency**（若有）：若其他服務快取閥值，刪除後快取未失效會導致誤判（需人工確認是否有快取設計）
- **Queue retry**：`threshold_sync_pending` 若 worker 處理失敗應有 retry 或死信機制（需人工確認 Tasks.py 邏輯）
- **Idempotency**：重複刪除不應導致重複 changelog 或多餘 sync 記錄

---

## 10. 常見錯誤
- **新人容易犯錯**：弄錯不同層級的刪除路徑與鍵值組合（例如誤用 game_type 刪除聯盟設定）。
- **AI 容易誤解**：誤以為刪除會直接呼叫 Kafka，實則透過資料表佇列非同步傳遞。
- **常見漏檢查項目**：刪除後未確認 changelog 與 sync_pending 是否成功寫入，或未處理交易 rollback。
- **常見錯誤流程**：先刪除再寫 changelog（若 DB error 將遺失 audit trail）；正確應在交易內依序刪除、寫 changelog、寫佇列。

---

## 11. Evidence
| 類型 | 來源 |
|------|------|
| 需求功能 | README.md: 「賠率閥值（oddthreshold）：支援遊戲層級監控玩法的新增、修改、刪除與同步」 |
| DB 表結構 | `oddthreshold_sport_setting`, `oddthreshold_league_setting`, `oddthreshold_game_setting` 來自 `migrations/001_create_core_tables.sql` |
| 稽核表結構 | `threshold_changelog` (table_name, record_key, old_value, new_value ...) |
| 同步佇列表 | `threshold_sync_pending` (table_name, record_key, status) |
| 變更排入佇列 | README.md: 「閥值異動皆寫入 changelog，並將變更排入同步佇列供下游消費」 |
| 程式流程推斷基於 | Python FastAPI 慣用分層（Resources/Service/Provider），`oddthreshold_setting.py` 存在 upsert，推測存在 delete（需人工確認） |

---

### 建議待確認事項
- **確切 API 路徑**：目前 OpenAPI 文件不完整，需人工確認刪除端的路由與 request 結構。
- **operator_account 傳遞方式**：來自 token 還是 request body？需確認。
- **同步 worker 實作**：需查閱 `Tasks.py` 確認讀取 `threshold_sync_pending` 並發送 Kafka 的細節，才能補足 Queue 環節。
- **是否有快取失效**：若有 Redis 快取閥值，刪除流程必須包含快取清除，目前無資料佐證，建議新增相關規則。