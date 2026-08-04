# 設定站台停止

## 1. 場景目的

針對指定的 `gameType`，停用該玩法類型下的所有站台設定。此操作會直接更新 `gamesettings.gametype_settings` 中的 `site.stop` 狀態，並透過外部服務 `syncservice` 清除相關的 `Redis BusinessCache`，以確保所有相依的商家與前台下注服務能夠立即讀取到最新的站台停用狀態。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| POST | `/api/v1/system/site/stop/{gameType}` | 設定指定 gameType 的站台為停止狀態 |

---

## 3. 流程總覽

1. 接收請求，取得 `gameType`。
2. 調用 `ConfigService`，執行設定站台停止邏輯。
3. 寫入 `gamesettings.gametype_settings` 資料表，更新 `settings` JSON 欄位，將 `site.stop` 設為 `true`。
4. 透過 `syncservice` 發送通知，清除所有關聯 `businesscode` 的 `Redis BusinessCache`。
5. 回傳操作結果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `GameSettingServiceController.StopSite` | 接收 gameType，調用 Transfer layer。 |
| 2 | Transfer | `SystemSiteConfigTransfer.StopSite` | 調用 `ConfigService.StopSite`。 |
| 3 | Service | `ConfigService.StopSite` | 組合資料，更新 `gamesettings.gametype_settings`。 |
| 4 | Service | `ConfigService.StopSite` | 調用 `syncservice` API 清除 `BusinessCache`。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | gamesettings.gametype_settings | Update | 更新 `settings` JSON，將 `site.stop` 設為 `true`。 |
| Redis | BusinessCache | Delete | 透過 `syncservice` 清除所有關聯 business 的快取。 |

---

## 6. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 請求的 `gameType` 不存在於任何 business 設定 | 需人工確認，目前可能直接成功或拋出業務異常。 |
| `syncservice` 呼叫失敗 | 需人工確認 retry 機制。若無 retry，將導致快取與 DB 不一致。 |

---

## 7. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| SITE-STOP-01 | Integration | 對已存在的 gameType 執行停止。 | DB `settings.site.stop` 為 true，`BusinessCache` 被清除。 |
| SITE-STOP-02 | Cache | 停止後查詢商家設定。 | 回傳的設定中 `site.stop` 為 true。 |

---

## 8. 高風險區域

- **Cache consistency**：若 `syncservice` 呼叫失敗，`Redis` 中的 `BusinessCache` 未清除，將導致其他服務在快取過期前讀到舊的啟用狀態，造成設定不一致。需確認有重試或補償機制。

---

## 9. Evidence

| 類型 | 來源 |
|---|---|
| API | POST /api/v1/system/site/stop/{gameType}（README.md） |
| DB | gamesettings.gametype_settings（DB schema） |
| Redis | BusinessCache, syncservice（README.md 技術棧 / 服務相依） |
| Code | GameSettingServiceController.StopSite → SystemSiteConfigTransfer.StopSite（Source code semantics Phase1） |