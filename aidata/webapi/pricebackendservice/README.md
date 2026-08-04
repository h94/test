# PriceBackendService WebAPI

- **Git Repository**：[https://git.zbdigital.net/biz/pricebackendservice.git](https://git.zbdigital.net/biz/pricebackendservice.git)

## 職責
負責作為體育競猜平台的**管理後台 API 聚合層（BFF）**，整合後端各微服務的呼叫，提供後台管理介面所需的會員、支付、廣告、競猜、社群、新聞、商品等完整管理功能。本服務**不直接存取資料庫**，所有資料操作均透過下游微服務 REST API 完成。

## 技術棧
- 框架：ASP.NET Core (.NET 8.0)
- 資料庫：無直接 DB 存取（透過下游 REST 微服務，操作 Cassandra 與 MySQL）
- 驗證：ECFramework.ECService（內部統一驗證框架）
- 配置中心：Zookeeper（路徑 `/demo`）（需人工確認）
- 日誌：Kafka（Topic: `applogs`）+ Cassandra（Keyspace: `logs`）
- 其他套件：ECCore 3.0.3、MemberModels 1.1.5、PaymentModels 3.0.1、AdvertisingModels 0.0.6、SixLabors.ImageSharp 3.1.5、GameDataModels（版本需人工確認）

## 資料庫重要 Table

| Table 名稱 | 用途 | 重要欄位 |
|-----------|------|---------|
| _(無直接存取，資料由下游微服務管理)_ | 本服務不直接操作資料庫，所有持久化操作均透過下游如 `memberservice`、`paymentservice`、`productservice` 等完成。 | — |

## 對外 API 重點

> 以下路由均需透過 `ECFramework.ECService` 進行後台管理員身份驗證（驗證標記：✅）。

### 活動管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/activity/{site}/{activityEvent}/products` | 新增站台活動商品 | ✅ |
| GET | `/api/v1/activity/{site}/{activityEvent}/products` | 取得站台活動商品 | ✅ |
| GET | `/api/v1/activity/{site}/{activityEvent}/redeemlogs` | 取得站台活動兌換紀錄 | ✅ |
| PUT | `/api/v1/activity/{site}/{activityEvent}/products/{id}` | 更新站台活動商品 | ✅ |
| PUT | `/api/v1/activity/{site}/{activityEvent}/redeemlogs/status` | 更新站台活動商品會員兌換紀錄狀態 | ✅ |
| DELETE | `/api/v1/activity/{site}/{activityEvent}/products/{id}` | 刪除站台活動商品 | ✅ |

### 廣告與公告管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/advertising/ads` | 新增廣告（含圖片上傳） | ✅ |
| POST | `/api/v1/advertising/bulletinboard/announcenments` | 新增公告 | ✅ |
| GET | `/api/v1/advertising/ads/{adArea}` | 查詢區域廣告 | ✅ |
| GET | `/api/v1/advertising/bulletinboard/announcenments` | 取得所有公告 | ✅ |
| PUT | `/api/v1/advertising/ads/{adArea}/{id}` | 更新區域廣告 | ✅ |
| PUT | `/api/v1/advertising/bulletinboard/announcenments/{aid}` | 更新公告 | ✅ |
| DELETE | `/api/v1/advertising/bulletinboard/announcenments/{aid}` | 刪除公告 | ✅ |

### 社群管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/community/hashtags/leagues/{gameType}/{lid}` | 創建聯盟標籤 | ✅ |
| GET | `/api/v1/community/hashtags/{gameType}` | 取得球種所有身分與聯盟標籤 | ✅ |
| GET | `/api/v1/community/articles/{gameType}` | 分頁查詢社群文章 | ✅ |
| GET | `/api/v1/community/articles/{gameType}/pinned` | 取得球種所有置頂文章 | ✅ |
| GET | `/api/v1/community/articles/{gameType}/{id}/comments` | 取得文章回文分頁 | ✅ |
| GET | `/api/v1/community/report/allreport` | 取得全部討論版統計總數 | ✅ |
| GET | `/api/v1/community/report/gametypereport` | 取得討論版文章統計 | ✅ |
| GET | `/api/v1/community/report/gametypereport/{gameType}` | 取得特定討論版文章細項統計 | ✅ |
| GET | `/api/v1/community/report/usereport` | 取得用戶文章統計 | ✅ |
| GET | `/api/v1/community/report/usereport/{account}` | 取得特定用戶細項文章統計 | ✅ |
| POST | `/api/v1/community/articles/comments/delete` | 批次移除文章的回文 | ✅ |
| PUT | `/api/v1/community/hashtags/memberships` | 更新身分標籤 | ✅ |
| PUT | `/api/v1/community/hashtags/leagues/{gameType}` | 更新聯盟標籤 | ✅ |
| PUT | `/api/v1/community/articles/{gameType}/pinned` | 置頂/取消置頂文章 | ✅ |
| DELETE | `/api/v1/community/hashtags/leagues/{gameType}/{id}` | 刪除聯盟標籤 | ✅ |
| DELETE | `/api/v1/community/hashtags/memberships/{id}` | 刪除身分標籤 | ✅ |
| DELETE | `/api/v1/community/articles/{gameType}/{id}` | 刪除會員文章 | ✅ |
| DELETE | `/api/v1/community/articles/{gameType}/{id}/comments/{commentId}` | 刪除文章單一回文 | ✅ |
| DELETE | `/api/v1/community/articles/user/{authKey}` | 刪除會員全部文章與回文與按讚數 | ✅ |

### 客服回饋管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/feedback/sport/topics` | 新增運動站台反饋種類 | ✅ |
| POST | `/api/v1/feedback/sport/messages/{tid}/{dateTime}/{account}/{id}/respImage` | 更新運動站台反饋回覆訊息管理者圖片 | ✅ |
| GET | `/api/v1/feedback/sport/topics` | 取得運動站台反饋種類 | ✅ |
| GET | `/api/v1/feedback/sport/messages/accounts` | 查詢會員客服訊息 | ✅ |
| GET | `/api/v1/feedback/sport/messages/visitors` | 查詢訪客客服訊息 | ✅ |
| GET | `/api/v1/feedback/sport/bussiness/messages` | 查詢商務訊息 | ✅ |
| PUT | `/api/v1/feedback/sport/topics/{id}` | 更新運動站台反饋種類 | ✅ |
| PUT | `/api/v1/feedback/sport/messages/{tid}/{dateTime}/{account}/{id}/respcontent` | 回覆客服訊息 | ✅ |
| PUT | `/api/v1/feedback/sport/messages/{tid}/{dateTime}/{account}/{id}/status` | 更新反饋狀態 | ✅ |
| PUT | `/api/v1/feedback/sport/bussiness/messages/{dateTime}/{id}/respcontent` | 更新商業訊息回覆內容 | ✅ |
| PUT | `/api/v1/feedback/sport/messages/{tid}/{dateTime}/{account}/{id}/respImage` | 更新反饋回覆訊息管理者圖片路徑 | ✅ |

### 直播社群群組管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/gamelive/communities/groups` | 新增社群群組 | ✅ |
| GET | `/api/v1/gamelive/communities/groups` | 查詢所有群組 | ✅ |
| GET | `/api/v1/gamelive/communities/groups/{id}/predictgames` | 查詢群組競猜賽事 | ✅ |
| PUT | `/api/v1/gamelive/communities/groups/{id}` | 更新群組 | ✅ |

### 頻道與遊戲設定管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/gamelive/channel` | 新增/編輯頻道 | ✅ |
| PUT | `/api/v1/gamelive/channels` | 編輯頻道列表 | ✅ |
| PUT | `/api/v1/gamelive/channel/open` | 開啟頻道 | ✅ |
| PUT | `/api/v1/gamelive/channel/close` | 關閉頻道 | ✅ |
| GET | `/api/v1/gamelive/channels` | 取得所有頻道資訊 | ✅ |
| POST | `/api/v1/gamesetting/subscriber/register` | 新增訂閱者 | ✅ |
| GET | `/api/v1/gamesetting/subscriber` | 取得所有訂閱者 | ✅ |
| PATCH | `/api/v1/gamesetting/subscriber` | 更新訂閱者 | ✅ |
| POST | `/api/v1/gamesetting/subscriber/users/register` | 新增使用者 | ✅ |
| GET | `/api/v1/gamesetting/subscriber/users` | 取得訂閱者所有使用者 | ✅ |
| PATCH | `/api/v1/gamesetting/subscriber/users` | 更新使用者 | ✅ |
| POST | `/api/v1/gamesetting/system/{gameType}` | 新增系統設定值 | ✅ |
| GET | `/api/v1/gamesetting/system/{company}/{gameType}` | 取得公司系統設定值 | ✅ |
| GET | `/api/v1/gamesetting/site` | 取得全部球種支援站台 | ✅ |
| GET | `/api/v1/gamesetting/playmodes` | 取得全部賽事的玩法 | ✅ |
| GET | `/api/v1/gamesetting/playmodes/{gameType}` | 取得賽事全部玩法 | ✅ |
| GET | `/api/v1/gamesetting/site/notenabled` | 取得尚未開通的支援站台 | ✅ |
| PATCH | `/api/v1/gamesetting/system/playmode/add/{gameType}` | 新增設定值 playmode | ✅ |
| PATCH | `/api/v1/gamesetting/system/playmode/edit/{gameType}` | 修改設定值 playmode | ✅ |
| PATCH | `/api/v1/gamesetting/system/playmode/delete/{gameType}` | 刪除設定值 playmode | ✅ |
| PATCH | `/api/v1/gamesetting/playmodes/site/add` | playmode 新增支援站台 | ✅ |
| PATCH | `/api/v1/gamesetting/playmode/alarm/add/{gameType}` | 球種所有設定值 playmode 新增定時變更偏移量設定 | ✅ |

### 通知與 App 管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/manage/notifications/topics` | 新增通知項目 | ✅ |
| POST | `/api/v1/manage/notifications/messages/{tid}` | 新增通知項目訊息 | ✅ |
| POST | `/api/v1/manage/notifications/sitemails` | 新增通知站內信 | ✅ |
| POST | `/api/v1/manage/appdevices` | 設定 App 系統版本 | ✅ |
| GET | `/api/v1/manage/notifications/topics` | 取得通知項目 | ✅ |
| GET | `/api/v1/manage/notifications/messages/{tid}` | 取得通知項目訊息 | ✅ |
| GET | `/api/v1/manage/notifications/sitemails` | 取得通知站內信 | ✅ |
| GET | `/api/v1/manage/appdevices` | 取得 App 系統版本 | ✅ |
| GET | `/api/v1/manage/report/generate` | 產生每日報表資料 | ✅ |
| GET | `/api/v1/manage/report` | 取得每日報表 | ✅ |
| PUT | `/api/v1/manage/notifications/topics/{id}` | 更新通知項目 | ✅ |
| PUT | `/api/v1/manage/notifications/messages/{tid}/{id}` | 更新通知項目訊息 | ✅ |

### 會員管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/member/forbidden/email/domains` | 新增禁用 email 網域 | ✅ |
| POST | `/api/v1/member/game/users/{authKey}/sublogs` | 新增賽事會員訂閱紀錄 | ✅ |
| POST | `/api/v1/member/game/editors/{authKey}` | 新增賽事小編 | ✅ |
| POST | `/api/v1/member/game/editors/{authKey}/login` | 賽事小編登入 | ✅ |
| POST | `/api/v1/member/game/users/banned` | 新增 Ban 單（封禁會員） | ✅ |
| POST | `/api/v1/member/game/users/banned/deduction` | 預定執行 Banner 扣款排程 | ✅ |
| POST | `/api/v1/member/supreme/cycles` | 新增至尊球王週期 | ✅ |
| POST | `/api/v1/member/supreme/leaderboards` | 設定至尊球王榜單（寫檔） | ✅ |
| POST | `/api/v1/member/supreme/winners` | 結算至尊球王（系統自動） | ✅ |
| POST | `/api/v1/member/supreme/winners/{gameType}/{lid}/{cid}/resettle` | 重新結算至尊球王（手動） | ✅ |
| POST | `/api/v1/member/supreme/records` | 設定進行中至尊球王週期所有參與者活動資料 | ✅ |
| POST | `/api/v1/member/supreme/records/{gameType}/{lid}/{cid}/{type}/{date}` | 修復至尊球王參與者日期活動資料（手動） | ✅ |
| POST | `/api/v1/member/supreme/records/autorepair/{type}` | 自動修復至尊球王參與者近 7 天紀錄 | ✅ |
| POST | `/api/v1/member/zcoin/rank` | 建立 Z 幣排行 | ✅ |
| GET | `/api/v1/member/forbidden/email/domains` | 取得禁用 email 網域 | ✅ |
| GET | `/api/v1/member/game/pages/{pageIndex}/users` | 分頁查詢遊戲會員 | ✅ |
| GET | `/api/v1/member/game/users` | 依 email/account 查詢賽事站台會員 | ✅ |
| GET | `/api/v1/member/game/verifyusers` | 取得驗證賽事會員 | ✅ |
| GET | `/api/v1/member/game/users/{authKey}/sublogs` | 取得賽事會員訂閱紀錄 | ✅ |
| GET | `/api/v1/member/game/editors` | 取得所有賽事小編 | ✅ |
| GET | `/api/v1/member/game/users/email/domains` | 取得賽事會員 email 網域數量 | ✅ |
| GET | `/api/v1/member/game/wallet` | 取得錢包資訊（依條件） | ✅ |
| GET | `/api/v1/member/game/wallet/users/{authKey}` | 取得會員錢包 | ✅ |
| GET | `/api/v1/member/game/wallet/users/{authKey}/transactions` | 取得會員錢包交易紀錄 | ✅ |
| GET | `/api/v1/member/zcoinreports/byothers` | Z 幣報表（他人／非 Robot） | ✅ |
| GET | `/api/v1/member/game/wallet/gametransactions/{gameType}/{lid}/{gdate}/{gid}` | 賽事 Z 幣交易紀錄 | ✅ |
| GET | `/api/v1/member/game/users/banned/{authKey}` | 取得單筆 Ban 單 | ✅ |
| GET | `/api/v1/member/game/users/banned` | 取得所有 Ban 單 | ✅ |
| GET | `/api/v1/member/game/users/status` | 取得凍結會員帳號 | ✅ |
| GET | `/api/v1/member/supreme/cycles/items` | 取得至尊球王所有球種聯盟清單 | ✅ |
| GET | `/api/v1/member/supreme/cycles/{gameType}/{lid}` | 取得球種聯盟所有至尊球王週期 | ✅ |
| GET | `/api/v1/member/supreme/cycles/{gameType}/{lid}/{cid}` | 取得至尊球王週期獲勝者 | ✅ |
| GET | `/api/v1/member/supreme/analysis/unlock/{gameType}/{lid}` | 取得帳號解鎖分析 | ✅ |
| PUT/PATCH | 多個更新路由（會員資料、密碼、會員等級、小編設定、Ban 單結束時間、股票會員等） | — | ✅ |
| GET | `/api/v1/member/game/editors/logs` | 查詢小編操作日誌 | ✅ |

> 會員管理 API 數量較多，部分更新／修補類路由基於 `MemberController` 內的 `Update*` 方法提供，完整列表請參考原始碼。

### 新聞與 AI 資訊管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/news/sportarticles` | 設定運動站台文章 | ✅ |
| POST | `/api/v1/news/ai/hotdiscussiongames` | 設定 AI 熱門討論賽事 | ✅ |
| POST | `/api/v1/news/ainews` | 修改 AI 文章，寫入 Meilisearch | ✅ |
| GET | `/api/v1/news/ai/hotdiscussiongames/{gameType}/{gdate}` | 取得 AI 熱門討論賽事 | ✅ |
| GET | `/api/v1/news/sportarticles` | 取得運動站台文章 | ✅ |
| GET | `/api/v1/news/ainews/{gtype}/{gdate}` | 取得 AI 文章 | ✅ |
| DELETE | `/api/v1/news/sportarticles/{id}` | 刪除運動站台文章 | ✅ |
| DELETE | `/api/v1/news/ai/hotdiscussiongames/{gameType}/{lid}/{gdate}/{gid}` | 刪除 AI 熱門討論賽事 | ✅ |

### 支付管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/payment/sport/paymethods` | 新增運動站台付費方式 | ✅ |
| POST | `/api/v1/payment/sport/subplans` | 新增運動站台訂閱方案 | ✅ |
| POST | `/api/v1/payment/sport/tradeorders` | 新增運動站台交易紀錄 | ✅ |
| POST | `/api/v1/payment/sport/reports` | 生成年月份報表（xxl-job） | ✅ |
| POST | `/api/v1/payment/sport/recommendreports` | 生成年月推薦報表（xxl-job） | ✅ |
| GET | `/api/v1/payment/sport/paymethods` | 取得運動站台付費方式 | ✅ |
| GET | `/api/v1/payment/sport/subplans` | 取得運動站台訂閱方案 | ✅ |
| GET | `/api/v1/payment/sport/tradeorders` | 取得運動站台交易紀錄 | ✅ |
| GET | `/api/v1/payment/sport/reports/{year}` | 取得運動站台年度報表 | ✅ |
| GET | `/api/v1/payment/sport/reportlist/{year}/{month}` | 取得運動站台報表明細 | ✅ |
| GET | `/api/v1/payment/sport/shareinfos/{account}` | 取得運動站台會員分潤收支紀錄 | ✅ |
| PUT | `/api/v1/payment/sport/paymethods/{payType}/{mode}` | 更新運動站台付費方式 | ✅ |
| PUT | `/api/v1/payment/sport/subplans/{id}` | 更新運動站台訂閱方案 | ✅ |
| PUT | `/api/v1/payment/sport/tradeorders/{year}/{dateTime}/{account}/{id}` | 更新運動站台交易紀錄 | ✅ |
| PUT | `/api/v1/payment/sport/reports` | 結束運動站台年月報表結果（xxl-job） | ✅ |
| PUT | `/api/v1/payment/sport/recommendreports` | 結束運動站台年月推薦報表結果（xxl-job） | ✅ |

### 競猜管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/predict/settings/{gameType}` | 新增球種預測設定 | ✅ |
| POST | `/api/v1/predict/killer/cycles/{gameType}` | 新增莊家殺手週期設定 | ✅ |
| POST | `/api/v1/predict/killer/conditions/{gameType}/{lid}/{cid}` | 新增莊家殺手某期條件設定 | ✅ |
| POST | `/api/v1/predict/mergepredicts/{gameType}` | 合併球種賽事預測 | ✅ |
| POST | `/api/v1/predict/payout/{gameType}/{lid}/{gdate}/{gid}` | 派彩賽事預測 | ✅ |
| POST | `/api/v1/predict/betpool/games` | 新增彩池遊戲 | ✅ |
| POST | `/api/v1/predict/betpool/games/{id}/bets/transactions` | 派發彩池注單 Z 幣 | ✅ |
| POST | `/api/v1/predict/betpool/games/{gid}/robots/placebets` | 機器人彩池下注 | ✅ |
| POST | `/api/v1/predict/flashmob/settlement` | 派發快閃活動 Z 幣 | ✅ |
| GET | `/api/v1/predict/settings` | 取得預測聯盟設定 | ✅ |
| GET | `/api/v1/predict/allplaymodes` | 取得全部玩法設定 | ✅ |
| GET | `/api/v1/predict/bets/zcoinReports/{gtype}/byUser` | Z 幣報表（依會員） | ✅ |
| GET | `/api/v1/predict/bets/zcoinReports/{gtype}/byGame` | Z 幣報表（依賽事） | ✅ |
| GET | `/api/v1/predict/playmodes/{gameType}` | 取得球種已開啟玩法設定 | ✅ |
| GET | `/api/v1/predict/settings/gametypes` | 取得全部球種設定 | ✅ |
| GET | `/api/v1/predict/killer/cycles/{gameType}/{lid}` | 取得球種聯盟莊家殺手週期設定 | ✅ |
| GET | `/api/v1/predict/killer/{gameType}/{lid}/{cid}/notkillers` | 取得非殺手資訊 | ✅ |
| GET | `/api/v1/predict/killer/conditions/{gameType}/{lid}/{cid}` | 取得球種聯盟莊家殺手期數條件 | ✅ |
| GET | `/api/v1/predict/bets/{gameType}/{lid}` | 取得球種聯盟日期範圍預測注單 | ✅ |
| GET | 多個路由（賽事結果狀態、排行榜、彩池查詢等） | — | ✅ |
| PUT/PATCH | 多個更新路由（設定、玩法、派彩、彩池遊戲等） | — | ✅ |

> 競猜管理包含自動排程任務，如殺手週期派彩、生成排行榜等。完整 API 列表請參考 `PredictController` 和相關接口定義。

### 賽事與賠率中心管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/v1/pricecenter/leagues/{gameType}/namemap/{lang}` | 取得球種聯盟名稱對照表 | ✅ |
| GET | `/api/v1/pricecenter/games/{gameType}` | 取得球種日期賽事 | ✅ |
| GET | `/api/v1/pricecenter/games/{gameType}/{lid}/{gDate}` | 取得球種聯盟日期賽事 | ✅ |
| GET | `/api/v1/pricecenter/games/{gameType}/{lid}/{gDate}/{id}/siteinfos` | 取得賽事合併站台資訊 | ✅ |
| PUT | `/api/v1/pricecenter/games/{gameType}/score-status` | 更新賽事比分和狀態 | ✅ |
| PUT | `/api/v1/pricecenter/games/{gameType}/{lid}/{gDate}/{id}/resultinfo` | 更新賽事結束資訊 | ✅ |
| POST | `/api/v1/pricecenter/games/inplay/hot/{gameType}/{lid}/{gDate}/{gid}` | 設定熱門場中競猜賽事 | ✅ |
| GET | `/api/v1/pricecenter/games/inplay/hot` | 取得熱門場中競猜賽事 | ✅ |

### 交易所管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/tradegame/settings/gametype/{gtype}` | 新增交易所球種聯盟設定 | ✅ |
| POST | `/api/v1/tradegame/settings/stock` | 儲存股票上限設定 | ✅ |
| POST | `/api/v1/tradegame/settings/score` | 儲存分數防禦設定 | ✅ |
| GET | `/api/v1/tradegame/report/byuser/{gtype}` | 交易報表（依會員） | ✅ |
| GET | `/api/v1/tradegame/report/bygame/{gtype}` | 交易報表（依賽事） | ✅ |
| GET | `/api/v1/tradegame/game/{gameType}/{date}` | 取得球種日期交易所賽事資訊 | ✅ |
| GET | `/api/v1/tradegame/tradehistory/{gtype}/{date}/{lid}/{gid}/{playMode}` | 取得單場比賽玩法交易紀錄 | ✅ |
| GET | `/api/v1/tradegame/resultlogs/{gtype}/{date}` | 取得日期球種賽事結算結果狀態 | ✅ |
| GET | `/api/v1/tradegame/settings/gametype` | 取得交易所全部球種聯盟設定 | ✅ |
| GET | `/api/v1/tradegame/settings/gametype/{gtype}/leaguenamemap` | 取得交易所球種聯盟名稱對照表 | ✅ |
| GET | `/api/v1/tradegame/settings/stock/{gtype}` | 取得球種股票上限設定 | ✅ |
| GET | `/api/v1/tradegame/settings/stock/{gtype}/{lid}` | 取得聯盟股票上限設定 | ✅ |
| GET | `/api/v1/tradegame/settings/stock/{gtype}/{lid}/{gdate}` | 取得賽事股票上限設定 | ✅ |
| GET | `/api/v1/tradegame/settings/score/{gtype}` | 取得球種分數防禦設定 | ✅ |
| GET | `/api/v1/tradegame/settings/score/{gtype}/{lid}` | 取得聯盟分數防禦設定 | ✅ |
| PUT | `/api/v1/tradegame/recalculate/{gtype}/{gdate}/{lid}/{gid}` | 重新計算日期球種賽事結算結果狀態 | ✅ |
| PUT | `/api/v1/tradegame/settings/gametype/{gtype}` | 更新交易所球種聯盟設定 | ✅ |
| DELETE | 多個路由（刪除股票上限及分數防禦設定） | — | ✅ |

### 商城商品管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/store/products` | 新增商城商品 | ✅ |
| POST | `/api/v1/store/productstocklogs` | 新增商品庫存紀錄 | ✅ |
| GET | `/api/v1/store/products` | 取得所有商城商品 | ✅ |
| GET | `/api/v1/store/productredeemlogs/{pclass}/{pid}` | 取得單一商品所有兌換紀錄 | ✅ |
| GET | `/api/v1/store/productredeemlogs` | 取得所有商品兌換紀錄 | ✅ |
| GET | `/api/v1/store/productstocklogs/{pclass}/{pid}` | 取得單一商品所有庫存紀錄 | ✅ |
| PUT | `/api/v1/store/products` | 更新商城商品 | ✅ |
| PUT | `/api/v1/store/productredeemlogs` | 更新商品兌換紀錄(狀態、配送時間) | ✅ |
| DELETE | `/api/v1/store/products/{pclass}/{pid}` | 刪除商城商品 | ✅ |

### 系統工具
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/upload/img` | 上傳圖片 | ✅ |
| POST | `/api/v1/system/upload/img/product` | 上傳商品圖片 | ✅ |
| GET | `/api/v1/system/gametypes` | 取得支援的球種代碼清單 | ✅ |
| GET | `/heart` | 服務心跳檢查 | ❌ |
| GET | `/version` | 取得服務版本與建置資訊 | ❌ |