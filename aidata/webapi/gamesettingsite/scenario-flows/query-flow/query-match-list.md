# 取得賽事與盤口資訊

## 1. 場景目的
根據「站點」及「日期」查詢指定球種的聯賽與賽事列表，並在查詢時整合各賽事的盤口編修日誌；本流程旨在提供管理後台賽事即時概覽，僅查詢無寫入，且依賴下游 Provider 取得核心資料。

---

## 2. 入口 API
| Method | Path | 說明 |
|---|---|---|
| GET | `/api/ainews/{gameType}/{date}` | 獲得指定球種、日期的 AI 新聞列表（含賽事基本資訊與盤口 meta） |

---

## 3. 流程總覽
1. 接收 GET 請求，從路徑提取 `gameType` 與 `date`
2. 驗證請求參數格式（需人工確認：驗證邏輯位於 Controller 或 Middleware）
3. 透過 PriceCenter / BusinessProvider 查詢賽事主資料（聯賽、隊伍、時間）
4. 讀取 `news.ainews_gs` 中已發布（status=1）的 AI 新聞關聯資料
5. 讀取 `gamesettings.game_settings` 中當日對應之盤口編修配置
6. 結合（3）、（4）、（5）結果，組裝 DTO
7. 回傳組裝後的賽事與盤口資訊列表

---

## 4. 程式流程
| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | AINewsController.GetAINews | 接收 `gameType`, `date`，呼叫 Service |
| 2 | Service | (推測) AINewsService.GetByDate | 調用 Provider 組合資料 |
| 3 | Provider | (需人工確認) BusinessProvider / PriceCenter | 透過外部服務取得賽事原始資料 |
| 4 | DB | news.ainews_gs SELECT | 以 `gdate` + `gtype` 查詢已發布新聞 |
| 5 | DB | gamesettings.game_settings SELECT | 以 `company`, `game`, `gdate` 過濾啟用設定 |
| 6 | Service | (推測) AINewsService | 合併賽事、AI 預測、盤口配置 |
| 7 | Controller | AINewsController | 回傳 `List<AINewsDTO>` |

---

## 5. DB / Cache / Queue 使用
| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | news.ainews_gs | Read | 查詢已發布且需前台展示之 AI 新聞 |
| DB | gamesettings.game_settings | Read | 獲取盤口編修日誌或設定 |
| Cache | 未啟用 | — | gamesettingsite 目前未使用 Redis |
| Queue | 未使用 | — | 本流程為查詢流，無 Kafka 操作 |

---

## 6. 重要規則
- **僅讀取已發布新聞**：`news.ainews_gs` 查詢時必須指定 `status = 1`；`status=0` (待處理) 或 `status=2` (修正中) 的記錄不應回傳 (*evidence: news-detail.md, status 欄位說明*)
- **分區鍵強制**：查詢 `ainews_gs` 必須帶入 `gdate`（分區鍵），否則觸發全表掃描 (*evidence: gamesettingsite-detail.md, news 讀取規則*)
- **不可回傳敏感欄位**：`anwser`, `reanwser`, `bets`, `llmsettings` 對外 API 一律隱藏，僅回傳組裝後的最終內容 (*evidence: news-detail.md, 不可回傳欄位*)
- **JSON 校驗**：`game_settings.settings` 讀取後需反序列化為合法 JSON，服務端不可假定其為有效結構 (*evidence: gamesettings-detail.md, settings 欄位*)
- **遊戲設定啟用過濾**：查詢 `game_settings` 時必須過濾 `enabled=1`，停用的設定不應回傳 (*evidence: gamesettings-detail.md, enabled 欄位*)

---

## 7. 錯誤情境
| 情境 | 預期結果 |
|---|---|
| `gameType` 參數非法 | 回傳 400 Bad Request (需人工確認) |
| `date` 格式不符 `yyyy-MM-dd` | 回傳 400 Bad Request (需人工確認) |
| 查詢 `ainews_gs` 未帶 `gdate` | Cassandra 拒絕或觸發高延遲掃描，內部拋出例外並記錄錯誤 (*evidence: gamesettingsite-detail.md, 常見錯誤*) |
| 查詢 `game_settings` 未帶 `company` | 同上，Cassandra 全表掃描風險 |
| PriceCenter / BusinessProvider 呼叫失敗 | 依 Provider 設計進行重試或回傳 502 Bad Gateway（需人工確認重試策略） |
| 無符合條件的賽事資料 | 回傳空陣列 `[]` 並附 200 OK |

---

## 8. 測試重點
| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| FT-01 | API Test | 傳入有效 `gameType=SC` 與 `date=2026-05-21` | 返回 200 與比賽列表 |
| FT-02 | API Test | 傳入無效 `gameType` | 返回 400 |
| FT-03 | API Test | 傳入無效日期格式 | 返回 400 |
| FT-04 | Flow Test | 模擬 `ainews_gs` 僅有 `status=0` 記錄 | 返回空列表 |
| FT-05 | Permission Test | 未驗證請求（若需） | 返回 401 (需人工確認 API 是否強制驗證) |
| FT-06 | Flow Test | PriceCenter Provider 逾時 | 日誌記錄錯誤並返回 502 |

---

## 9. 高風險區域
- **跨服務依賴**：賽事核心資料由 PriceCenter 提供，`gamesettingsite` 無法自行生成；該服務不可用時功能全毀
- **Cassandra 查詢**：`ainews_gs` 與 `game_settings` 若未正確傳遞分區鍵，將引發全表掃描，顯著降低效能
- **Cache Consistency**：目前未使用 Redis，無一致姓問題，但無法透過快取降低外部服務延遲
- **敏感資訊洩漏**：`ainews` 中的 `anwser`, `bets` 等為內部機敏資料，須嚴格在 DTO 組裝時排除

---

## 10. 常見錯誤
- ❌ 查詢 `ainews` 系列表時未帶 `gdate` → 必須強制帶入 `gdate` 作為分區鍵
- ❌ 前台 API 回傳 `status=0` 的記錄 → 對外僅可見 `status=1` 的 AI 新聞
- ❌ 組裝回應時暴露 `anwser`, `bets`, `llmsettings` → 應使用 `AINewsDTO` 模型過濾欄位
- ❌ 誤解 `date` 參數為文章生成時間 → 此為賽事開賽日期，非新聞時間戳
- ❌ 直接將 `game_settings.settings` 視為純文字回傳 → 應解析 JSON 結構後僅暴露必要配置

---

## 11. Evidence
| 類型 | 來源 |
|---|---|
| API | `OpenAPI: /api/ainews/{gameType}/{date}` |
| DB | `news.ainews_gs` (Cassandra) |
| DB | `gamesettings.game_settings` (Cassandra) |
| DB Rule | `gamesettingsite-detail.md` — news 讀取規則 (必須指定 gdate) |
| DB Rule | `news-detail.md` — status 欄位定義與不可回傳欄位 |
| Provider | `README.md` — 資料來源：PriceCenter, BusinessProvider |
| Model | `AINewsDTO` (from OpenAPI components/schemas) |