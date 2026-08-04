# MergeSite WebAPI

- **Git Repository**：[https://git.zbdigital.net/biz/mergesite.git](https://git.zbdigital.net/biz/mergesite.git)

## 職責

負責賽事合併管理，提供聯盟、站台賽事（SiteGame）、OpenClaw 合併資料的查詢、比對與強制合併操作，並支援 AI 自動比對任務（閘道代理至 openclawservice），作為資料整合的管理後台 API（backend-for-frontend, BFF）。服務本身無直接資料庫，所有資料讀寫均透過 PriceCenterService Gateway 執行。

## 技術棧

- 框架：ASP.NET Core (.NET 8.0)
- 資料庫：無（透過 Gateway 呼叫 PriceCenterService REST API）
- 驗證：ECCore 內建機制
- 其他套件：GameDataModels（賽事資料模型共用）、ECCore、Swashbuckle（API 文件）、相關 CAS Client 套件

## 資料庫邊界與角色

此服務無直接資料庫，但參與下列資料庫的讀寫，實際操作均委派給 PriceCenterService。

> **權限定義**（依據 `mergesite-detail.md`）：
> - `pricecenter`：mergesite 具備 **writer / reader** 權限（合併流程、日誌記錄、站點對照、帳戶驗證）。
> - `sport`：mergesite 具備 **writer / reader** 權限（後台管理用途；可讀寫所有表格，但 **Read Only** 的角色規範見下方「roles 限制」）。
> - `games`：mergesite 僅具備 **reader** 權限，**嚴禁**寫入 `status`、`match_h`、`match_a`、`resultinfo`、`source` 等欄位。

| 資料庫 | 角色 | 備註 |
|--------|------|------|
| pricecenter | writer / reader | 讀取合併結果、站台對照、帳號驗證；寫入合併流程執行結果與操作日誌（`actionlog`）。 |
| sport | writer / reader（後台工具） | 可讀寫所有表格（維護性操作）；**唯讀** roles 見下方限制。 |
| games | reader | **唯讀**，查詢賽事用於合併比對。不可寫入 `status`、`match_h`、`match_a`、`resultinfo`、`source` 等欄位。 |

### 對外暴露的敏感欄位保護原則（不可回傳欄位清單）

依據 `mergesite-detail.md`，以下為需要脫敏或完全遮蔽的關鍵欄位：

| 資料表 | 不可回傳欄位 | 備註 |
|--------|-------------|------|
| accounts_*（pricecenter） | `password`、`handler`、`phone`（對前台） | `phone` 僅後台授權可查；一般列表應遮蔽。 |
| leagues / games / teams（pricecenter） | `Logs` | 內部操作軌跡。 |
| actionlog（pricecenter） | `detail` | 含敏感參數。 |
| openclaw_merge（pricecenter） | `Game` / `MainSiteGame`（整個 JSON） | 合併原始 JSON 不對外暴露。 |
| GameUsers_Wallet（sport） | `AuthKey` | 絕對禁止洩漏。 |
| GameUsers_Wallet_Transactions（sport） | `TypeInfo` | 內部 JSON 含關聯帳號等敏感資訊，前台 API 不可完整回傳。 |
| ChatRoomHistories_Backup（sport） | `Account`（公開聊天） | 遮蔽真實帳號，僅回傳 `UserName`。 |
| Notification_Messages（sport） | `TID`、`ID` | 不應曝露內部模板或訊息 ID。 |
| notification_sitemails（sport） | `Content`（列表查詢） | 信件列表 API 不顯示完整內文。 |

## 對外 API 重點

### 聯盟管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/leagues/{gameType}` | 取得球種聯盟列表。支援查詢參數 `startDate`、`endDate`、`startTime`、`endTime`、`lName`、`lid` | ✅ |
| PUT | `/api/leagues/{gameType}/{id}/name` | 更新聯盟名稱 | ✅ |
| PUT | `/api/leagues/{gameType}/{id}/namemap` | 更新聯盟語系名稱 | ✅ |
| PUT | `/api/leagues/{gameType}/{id}/abbrmap` | 更新聯盟語系簡稱 | ✅ |
| DELETE | `/api/leagues/{gameType}/{lid}` | 刪除聯盟 | ✅ |
| PUT | `/api/leagues/{gameType}/{lid}/locked` | 鎖定／解鎖聯盟 | ✅ |

### 站台聯盟（SiteLeague）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/siteleagues/{gameType}/bytime` | 依時間（`startDate`、`endDate`、`startTime`、`endTime`）取得站台聯盟 | ✅ |
| GET | `/api/siteleagues/{gameType}/bylid` | 依 `lid`（多筆）及 `site` 取得站台聯盟 | ✅ |
| GET | `/api/siteleague/{gameType}` | 依 `site` 及 `siteLID` 取得單筆站台聯盟 | ✅ |
| GET | `/api/siteleagues/{gameType}/bysite` | 依 `site` 取得該站所有站台聯盟 | ✅ |
| PUT | `/api/siteleague/{gameType}/name` | 更新站台聯盟顯示名稱 | ✅ |
| PUT | `/api/siteleague/{gameType}/namemap` | 更新站台聯盟語系名稱對照 | ✅ |
| PUT | `/api/siteleague/split/{gameType}` | 解除站台聯盟與主庫聯盟的合併 | ✅ |

### 站台賽事（SiteGame）與隊伍（SiteTeam）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/sitegames/{gameType}` | 依日期區間、站台代碼取得站台賽事列表 | ✅ |
| GET | `/api/sitegames/{gameType}/{gid}` | 依主庫 GID 取得已合併的站台賽事對照 | ✅ |
| GET | `/api/siteteam/{gameType}` | 依 `site`、`siteLID` 及 `siteTID` 取得單筆站台隊伍 | ✅ |
| GET | `/api/siteteams/{gameType}/bytid` | 依主庫 TID 取得已合併的站台隊伍 | ✅ |
| GET | `/api/siteteams/{gameType}/bysitelid` | 依站台及站台聯盟 ID 取得站台隊伍列表 | ✅ |
| PUT | `/api/siteteam/{gameType}/name` | 更新站台隊伍顯示名稱 | ✅ |
| PUT | `/api/siteteam/{gameType}/namemap` | 更新站台隊伍語系名稱對照 | ✅ |
| PUT | `/api/sitegame/split/{gameType}` | 解除站台賽事與主庫賽事的合併 | ✅ |
| PUT | `/api/siteteam/split/{gameType}` | 解除站台隊伍與主庫隊伍的合併 | ✅ |

### 賽事合併
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/merge/openclawmerge/{gameType}` | 依時間區間（`startQueryTime`、`endQueryTime`、`lid`）取得 OpenClaw 合併資料（列表） | ✅ |
| GET | `/api/merge/openclawmerge/row/{gameType}/{gdate}/{lid}/{id}` | 取得單筆 OpenClaw 合併資料 | ✅ |
| PUT | `/api/merge/games/{gameType}` | 強制合併賽事（目標保留、來源移除） | ✅ |
| PUT | `/api/merge/sitegames/{gameType}` | 合併多筆站台賽事至指定主站賽事 | ✅ |
| POST | `/api/merge/leagues/{gameType}` | 強制合併聯盟（主庫對主庫） | ✅ |
| POST | `/api/merge/leagues/{gameType}/{lid}` | 合併站台聯盟至主庫聯盟 | ✅ |
| POST | `/api/merge/teams/{gameType}` | 強制合併隊伍 | ✅ |

### AI 自動比對（代理 openclawservice）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/aimerge/predictions/pending/{gameType}/{date}` | 查詢待審核／衝突的 AI 比對預測清單。支援 `source`、`type`、`hour`、`mergeStatus` 查詢參數 | ✅ |
| GET | `/api/aimerge/predictions/{predictionId}` | 取得單筆 AI 比對預測明細 | ✅ |
| POST | `/api/aimerge/predictions/{predictionId}/confirm` | 人工確認 AI 比對預測 | ✅ |
| POST | `/api/aimerge/predictions/{predictionId}/reject` | 人工否定 AI 比對預測 | ✅ |
| POST | `/api/aimerge/predictions/batch/confirm` | 批次人工確認 AI 比對預測 | ✅ |
| POST | `/api/aimerge/predictions/batch/reject` | 批次人工否定 AI 比對預測 | ✅ |
| GET | `/api/aimerge/report/daily/{gameType}` | 查詢每日 AI 比對報表（可選 `date`） | ✅ |
| GET | `/api/aimerge/report/daily/{gameType}/range` | 查詢日期區間內（`dateFrom`、`dateTo`）每日 AI 比對報表列表 | ✅ |
| GET | `/api/aimerge/report/daily/{gameType}/{date}/errors` | 查詢每日報表中的否定／錯誤樣本。支援 `module` 過濾（normalizer / feature_builder / threshold / odds_missing） | ✅ |
| POST | `/api/aimerge/report/daily/{gameType}/{date}/errors/{predictionId}/mark-correct` | 將每日報表中的錯誤樣本人工標記為正確 | ✅ |
| POST | `/api/aimerge/backtest` | 執行 AI 比對回測 | ✅ |
| POST | `/api/aimerge/backtest/historical` | 提交歷史資料學習任務（202） | ✅ |
| GET | `/api/aimerge/backtest/historical/{jobId}` | 查詢歷史學習任務狀態 | ✅ |
| GET | `/api/aimerge/backtest/historical/{gameType}/{date}/latest` | 查詢最新歷史學習任務 | ✅ |
| GET | `/api/aimerge/backtest/historical/{gameType}/{date}/runs` | 列出歷史學習任務紀錄（支援 `limit` 參數） | ✅ |
| GET | `/api/aimerge/backtest/{gameType}/latest` | 取得最近一次回測結果。支援 `date` 查詢參數 | ✅ |
| GET | `/api/aimerge/health` | AI 排程 Job 健康檢查 | ✅ |
| POST | `/api/aimerge/jobs/job1` | 手動觸發 Job1 每日自動比對（202）。支援 `gameType` 查詢參數 | ✅ |
| GET | `/api/aimerge/jobs/job1/progress` | 查詢 Job1 即時進度 | ✅ |
| POST | `/api/aimerge/jobs/job2/{date}` | 手動觸發 Job2 對答案與產報表。支援 `gameType` 查詢參數 | ✅ |
| POST | `/api/aimerge/jobs/job3/{date}` | 手動觸發 Job3：pending/conflict 依 gid 補寫訓練標籤 | ✅ |
| POST | `/api/aimerge/jobs/job4` | 手動觸發 Job4：高分 prediction 自動合併站台賽事。支援 `gameType`、`dryRun` 查詢參數 | ✅ |
| POST | `/api/aimerge/tuningPack/export` | 提交調參包匯出任務（202） | ✅ |
| POST | `/api/aimerge/tuningPack/export/{jobId}/retry` | 重試 pending 或 failed 的調參包匯出任務（202） | ✅ |
| GET | `/api/aimerge/tuningPack/export/{jobId}` | 查詢調參包匯出任務狀態 | ✅ |
| GET | `/api/aimerge/tuningPack/export/{gameType}/{date}/runs` | 列出指定球種+日期的調參包匯出任務 | ✅ |
| GET | `/api/aimerge/tuningPack/export/{jobId}/download` | 下載已完成的調參包 JSON | ✅ |

### AI 比對系統配置管理（代理 openclawservice）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/aimerge/runtimeConfig/{gameType}` | 取得單一球種 runtime config（版本化參數集、多語述詞等） | ✅ |
| GET | `/api/aimerge/runtimeConfig/all` | 取得所有 scope 的現行 config | ✅ |
| GET | `/api/aimerge/runtimeConfig/history/{scope}` | 查詢指定 scope 的生效與草稿版本歷史 | ✅ |
| PUT | `/api/aimerge/runtimeConfig` | 建立 config 草稿版本（必要時同時切換至生效） | ✅ |
| POST | `/api/aimerge/runtimeConfig/rollback` | 將 config 回復至先前的正式版本 | ✅ |

### 系統
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/version` | 查詢服務版本與建置資訊 | ❌ |
| POST | `/api/system/logs/action` | 上傳使用者操作紀錄（`UserActionLog`） | ✅ |
| GET | `/api/system/logs/action/{date}` | 取得使用者操作紀錄。支援 `gameType` 查詢參數 | ✅ |
| GET | `/api/system/automapteam/check` | 取得聯盟自動比對錯誤紀錄。支援 `gameType`（必填）及 `status` 篩選 | ✅ |
| POST | `/api/system/automapteam/check/operator/{gameType}` | 設定聯盟自動比對紀錄為正確／錯誤 | ✅ |
| GET | `/api/system/automapteam` | 取得隊伍自動比對紀錄（待人工確認） | ✅ |
| POST | `/api/system/automapteam/operator/{gameType}` | 將隊伍自動比對紀錄標記為失敗／拒絕合併 | ✅ |
| PUT | `/api/system/automapteam/combineteam/{gameType}` | 手動確認隊伍自動比對成功並合併 | ✅ |
| POST | `/api/system/translate` | 翻譯關鍵字至目標語系 | ✅ |
| GET | `/api/config/site/mapping` | 取得站台代碼與顯示名稱對照表 | ✅ |

### 主庫賽事、隊伍維護
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/games/{gameType}/{date}` | 依球種與日期查詢賽程列表。支援 `status` 查詢參數 | ✅ |
| PUT | `/api/games/{gameType}/{lid}/{gDate}/{id}` | 更新主庫賽事時間、比分或狀態 | ✅ |
| DELETE | `/api/game/{gameType}/{lid}/{gDate}/{gid}` | 刪除指定主庫賽事 | ✅ |
| GET | `/api/teams/{gameType}` | 取得主庫隊伍列表。支援 `lids`、`tids`、`tName` 查詢參數 | ✅ |
| DELETE | `/api/teams/{gameType}/{tid}` | 刪除主庫隊伍 | ✅ |
| PUT | `/api/teams/{gameType}/{tid}/name` | 更新主庫隊伍名稱 | ✅ |
| PUT | `/api/teams/{gameType}/{id}/abbrmap` | 更新主庫隊伍語系簡稱對照 | ✅ |
| PUT | `/api/teams/{gameType}/{tid}/{lid}/namemap` | 更新主庫隊伍語系全名對照 | ✅ |
| PUT | `/api/teams/split/{gameType}` | 手動解除主庫隊伍與站台隊伍的合併關係 | ✅ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| PriceCenterService（Gateway） | 取得站台賽事、聯盟、OpenClaw 資料；執行強制合併操作；操作紀錄讀寫 |
| Kafka | 應用程式 Log 寫入（非業務操作紀錄；操作紀錄由 PriceCenterService 儲存） |
| OpenClawService（透過 HTTP API） | AI 自動比對預測、回測、學習任務排程等（由 `AiMergeController` 代理） |

**注意**：此服務無直接資料庫操作，所有資料庫讀寫均透過 PriceCenterService 執行。合併操作可能涉及 Cassandra（pricecenter keyspace）或 MySQL（sport），但不在本服務邊界內。

## 常見使用場景

1.  **管理後台查看待合併賽事**
    -   觸發：運營人員進入賽事合併管理頁面
    -   流程：`GET /api/merge/openclawmerge/{gameType}?startQueryTime=...&endQueryTime=...` 取得待比對的 OpenClaw 合併資料，確認是否需要人工介入

2.  **強制合併比對錯誤的聯盟**
    -   觸發：自動比對失敗，需人工強制配對
    -   流程：`GET /api/system/automapteam/check?gameType=...` 查看比對錯誤列表 → `POST /api/merge/leagues/{gameType}` 強制合併聯盟

3.  **更新聯盟多語系名稱**
    -   觸發：後台編輯人員維護聯盟顯示名稱
    -   流程：`PUT /api/leagues/{gameType}/{id}/namemap` 更新各語系名稱，`PUT /api/leagues/{gameType}/{id}/abbrmap` 更新縮寫

4.  **審核 AI 自動比對預測**
    -   觸發：運營人員查看 AI 比對結果
    -   流程：`GET /api/aimerge/predictions/pending/{gameType}/{date}` 取得待審核清單 → `POST /api/aimerge/predictions/{predictionId}/confirm` 確認或 `POST /api/aimerge/predictions/{predictionId}/reject` 否定

## 架構模式與限制

-   **閘道模式**：作為管理後台的專屬 BFF（Backend for Frontend），將前端請求轉發至 `PriceCenterService` 或 `OpenClawService`。本身無狀態、無本地資料庫。
-   **唯讀限制**：對 `games` 資料庫僅有 SELECT 權限，嚴禁任何寫入操作（如修改賽事狀態、比分）。
-   **使用者操作日誌**：重要操作（合併、刪除等）應在業務邏輯中透過 `POST /api/system/logs/action` 記錄操作行為，確保可審計。
-   **無快取**：本服務無 Redis 快取機制，每次請求皆即時查詢下游服務。

## 使用者操作注意事項

-   **強依賴 PriceCenterService**：所有資料的讀寫皆依賴此服務的可用性。若其發生故障，本服務大部分功能將無法使用。操作時若遇 502/504 錯誤，請稍後重試。
-   **合併為不可逆操作**：執行強制合併前，請務必於 `GET /api/merge/openclawmerge/{gameType}` 或單筆查詢 API 中確認合併對象正確無誤。
-   **AI 比對 Job 觸發**：`job1`、`job2`、`job3` 通常由排程自動執行。手動觸發請謹慎操作，特別是 `job1` 會對所有待處理賽事發起比對，執行時間較長。
-   **調參包匯出**：匯出任務為非同步執行，提交後可透過 job ID 查詢狀態，完成後方可下載。

## AI 判斷關鍵字

合併、賽事合併、聯盟合併、站台賽事、SiteGame、SiteLeague、OpenClaw、比對、merge、league、球種合併、強制合併、AI 比對、AiMerge、自動比對、預測確認、回測、backtest、調參包、tuning-pack、runtimeConfig、翻譯、translate