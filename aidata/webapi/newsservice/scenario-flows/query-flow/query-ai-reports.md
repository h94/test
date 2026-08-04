# 查詢 AI 分析報告

## 1. 場景目的
提供查詢 `aireports` 表的功能，支持以日期（startDate/endDate）、遊戲類型（gtype）、聯賽ID（lid）為條件，獲取 AI 分析後的彙總報告摘要，而非完整原始數據。

---

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| 需人工確認 | 需人工確認 | OpenAPI 中未包含 aireports 的直接端點。根據代碼，實際入口為 `IAINewsService.GetAIReports`。 |

---

## 3. 流程總覽
1. 服務接收查詢請求，包含選填的 `startDate`, `endDate`, `gtype`, `lid` 參數。
2. 根據 `startDate` 和 `endDate` 參數決定查詢的 partition key (`gdate`) 範圍。
3. 調用 Provider 向 Cassandra 的 `news.aireports` 表發起查詢。
4. 根據 `gtype` 和 `lid` 過濾。
5. 將查詢結果中的 `bets` 和 `results` 等原始數據進行屏蔽，只返回彙總摘要資訊。
6. 回傳處理後的報告摘要列表。

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | 需人工確認 | 接收並校驗請求參數。 |
| 2 | Service | IAINewsService.GetAIReports(startDate, endDate, gtype, lid) | 核心商業邏輯，組合查詢條件。 |
| 3 | Provider | IAINewsDataProvider.GetAIReports() | 執行對 Cassandra `aireports` 表的查詢。 |
| 4 | Transfer | (未知) | 將 DB 查詢結果映射為 API 回傳的 DTO，過濾掉 `bets`, `results` 等敏感欄位。 |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | Cassandra `news.aireports` | Read | 根據傳入參數查詢 AI 分析報告，獲取 `bets`, `others`, `results`。 |

---

## 6. 重要規則
- **查詢限制**：必須至少提供 `gdate` (partition key) 範圍（即 startDate/endDate）進行查詢，禁止全表掃描。僅以 `lid` 或 `gtype` 查詢會導致跨分區掃描，不被允許。
- **欄位過濾**：`aireports` 表中的 `bets` 和 `results` 欄位屬於內部分析數據，對外 API 必須被屏蔽，只允許回傳摘要或統計值。
- **gtype驗證**：傳入的 `gtype` 參數需經過 `IValidator.ValidateGameType(gameType)` 驗證，確保其為有效的球種代碼 (如 SC, BK, BS, HL, FL)。
- **權限限制**：所有請求應由 API Gateway 預先鑑權。newsservice 不負責用戶認證與授權。
- **寫入保護**：此 API 為查詢流程，不可寫入或修改 `aireports` 的任何記錄。`results` 欄位僅由內部 AI 分析完成後寫入，外部不可主動填充。

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| 未提供 `startDate` 或等效的日期查詢條件 | 查詢失敗或返回錯誤，提示必須提供日期範圍以避免全表掃描。 |
| 傳入的 `gtype` 不在白名單內 | `ValidateGameType` 驗證失敗，返回參數錯誤。 |
| 查詢結果為空 | 返回空列表或成功訊息，而非錯誤。 |
| Cassandra 查詢超時或失敗 | 返回服務內部錯誤。 |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| AIREPORT-01 | API Test | 提供有效的 `startDate`, `endDate`, `gtype` 組合 | 成功返回該時段對應球種的報告摘要列表。 |
| AIREPORT-02 | API Test | 只提供 `lid` 而不提供日期 | 失敗，返回參數錯誤或查詢被拒絕。 |
| AIREPORT-03 | Flow Test | 查詢結果中包含 `bets` 或 `results` 欄位 | 回傳的 DTO 中不應包含這些原始欄位，僅有摘要數據。 |
| AIREPORT-04 | API Test | 傳入無效的 `gtype` (例如 "INVALID") | 失敗，返回參數驗證錯誤。 |

---

## 9. 高風險區域
- **高風險 API**：此 API（假設為 `GET /api/v1/aireports`）屬於高風險 API，因其直接訪問內部分析數據。
- **全表掃描風險**：若未強制要求日期範圍，可能因查詢邏輯疏漏導致 Cassandra 全表掃描，嚴重影響數據庫性能。
- **跨服務資料同步**：`aireports` 的 `results` 欄位由 AI 分析服務（可能非 newsservice）寫入，讀取時可能存在資料延遲或不一致。

---

## 10. 常見錯誤
- ❌ 誤以為可以僅憑 `lid` 或 `gtype` 查詢 `aireports`，忽略了 `gdate` 是 partition key，必須包含在查詢條件中。
- ❌ AI/新人可能在回傳結果時不小心序列化了 `bets` 或 `results` 的原始內容，違反數據安全規則。
- ❌ 誤將 `anwser` 或 `reanwser` 的處理邏輯應用於 `aireports` 的 `results`，但兩者的讀取和屏蔽規則不同。

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API Endpoint | (需人工確認，OpenAPI 未明確定義) |
| 核心邏輯 | IAINewsService.GetAIReports(startDate, endDate, gtype, lid) |
| DB | Cassandra `news.aireports` |
| 讀取規則 | `newsservice-detail.md` - aireports 讀取規則 |
| 不可回傳欄位 | `newsservice-detail.md` - aireports 不可回傳欄位 (`bets`, `results`) |
| 查詢限制 | `newsservice-detail.md` - 常見錯誤："認為 `aireports` 可依 `lid` 單獨查詢" |
| 讀取規則 | `news-detail.md` - Table：aireports，跨服務查詢規則 |
| 數據語意 | Phase0/1 Code Semantics: `bets` (投注信息), `results` (AI報告摘要), `gdate` (分區鍵) |