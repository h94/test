# 查詢活動兌換紀錄（全站）

## 1. 場景目的
供後台管理員查詢指定站點活動（site/activityEvent）下所有使用者的兌換紀錄，用於監控、審核或統計。

## 2. 入口 API
| Method | Path | 說明 |
|--------|------|------|
| GET | `/api/v1/activity/productredeemlogs/{site}/{activityEvent}` | 取得該活動所有兌換紀錄（需驗證） |

## 3. 流程總覽
1. 驗證使用者身份（需有效 Token，推測需後台權限）
2. 查詢 `product.products_activity_redeem_logs` 表，依 Partition Key `site` 與 `activityevent` 讀取全部記錄（無 account 過濾）
3. 回傳結果時排除敏感欄位 `account`
4. 返回 JSON 陣列，包含所有狀態（0:審核中，1:成功，2:失敗）

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|------|-------|----------------|------|
| 1 | Controller | `ActivityController.GetProductRedeemLogs(site, activityEvent)` | 接收請求，調用 Service |
| 2 | Service | `ActivityService.GetRedeemLogs(site, activityEvent)` | 傳遞參數至 DataProvider |
| 3 | DataProvider | `ActivityDataProvider.QueryRedeemLogs(site, activityEvent)` | 組裝 CQL 查詢並執行 |

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB (Cassandra) | `product.products_activity_redeem_logs` | Read | 查詢符合 `site` 與 `activityevent` 的所有兌換紀錄 |
| Redis | 無 | - | 此場景不使用快取 |
| Queue | 無 | - | - |

## 6. 重要規則
- **權限限制**：需後台管理角色（需人工確認具體權限設定）
- **欄位隱藏**：不可回傳 `account` 欄位（依 `product-detail.md` 規定）
- **狀態範圍**：後台查詢可取得所有狀態（含審核中），不應過濾 `status=0`
- **無分頁**：API 定義中無分頁參數，可能回傳全量資料（高風險）

## 7. 錯誤情境
| 情境 | 預期結果 |
|------|----------|
| 未攜帶 Token 或 Token 無效 | 401 Unauthorized |
| 使用者不具後台權限 | 403 Forbidden |
| site 或 activityEvent 不存在 | 回傳空陣列或 404（依實作） |
| Cassandra 查詢逾時 | 500 Internal Server Error |

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| T1 | Permission | 一般使用者請求 | 403 Forbidden |
| T2 | Data | 查詢含有 status=0 的記錄 | 回傳列表包含審核中記錄 |
| T3 | Privacy | 檢查回傳欄位 | 不應包含 `account` |
| T4 | Exact | 查詢特定 site/activityEvent | 僅回傳該活動的記錄 |

## 9. 高風險區域
- **大資料量**：無分頁機制，若該活動兌換紀錄極多，可能造成回應過大或超時，需實作強制分頁或上限
- **DB 壓力**：全表掃描受限於 partition 設計，`site` 作為 partition key 可避免跨節點掃描，但仍需關注 single partition 規模

## 10. 常見錯誤
- 未驗證後台權限，導致所有登入用戶皆可查詢全站紀錄  
- 回傳時包含 `account` 欄位，違反隱私規則  
- 錯誤套用一般前端過濾（隱藏 status=0），導致後台無法查看待審核項目

## 11. Evidence
| 類型 | 來源 |
|------|------|
| API | OpenAPI: `GET /api/v1/activity/productredeemlogs/{site}/{activityEvent}` |
| DB Table | `product.products_activity_redeem_logs` (定義於 `product.md`) |
| 讀取規則 | `product-detail.md`: 「後台可依 site + activityevent 查詢全部」 |
| 不可回傳欄位 | `product-detail.md`: `products_activity_redeem_logs.account` 對前端不可回傳 |
| 程式推測 | 依命名慣例推測 `ActivityController` 與 `ActivityDataProvider` 對應的 class |