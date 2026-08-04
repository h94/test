# gameliveservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效  
> 最後更新：2026-05-27 12:00  
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### PlayByPlay Name Mapping List

> Confluence 頁面 ID：24092079  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/PlayByPlay+Name+Mapping+List)  
> 摘要檔：[processed/24092079-summary.md](../../confluence/processed/24092079-summary.md)  
> Confluence 最後更新：2022-01-13  
> 摘要最後同步：2026-05-26  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文提供足球、籃球、棒球、冰球、美式足球的 Play-by-Play 事件名稱在不同數據源（B365、1XBET、PESA、ZBDigital）之間的映射關係與中文翻譯。對 AI 開發而言，此表是統一即時事件數據的關鍵參考，可確保從不同來源獲取的事件能被正確識別與展示，避免因名稱差異導致邏輯錯誤。

**關鍵業務規則**：
- 主隊事件名稱標準化時需在前面添加 "Home"，客隊添加 "Away"（例：Away Dangerous Attack）；PESA 數據自身已帶 Home/Away 前綴，但無空格，解析時仍按客隊方式處理
- 當數據源欄位為空，或 B365 源顯示 "Bet365該畫面沒有任何信息" 時，表示該事件無數據，應映射為 None 並對應中文 "無"
- 足球事件：進攻 (B365=Attack, 1XBET=Attacks, PESA=AwayAttacks, ZBDigital=Attack)；角球 (Corner/Corner/AwayCorners/Corner) 等全部事件均需嚴格按照表格中的名稱進行匹配
- 籃球事件分為總體統計與節次統計，如 PESA 的 AwayFirstQuarterFouls 映射到 ZBDigital 的 1stQuarter Foul，其他節次類似，需保持節次維度一致
- 不同數據源可能缺少某些事件（如表內留空），缺失欄位在內部流轉時應保留為空，不得自行填補

**注意事項**：
- ⚠️ 最後更新於 2022-01-13，距今已超過兩年，部分數據源的命名可能已變動，需人工核實當前有效性
- ⚠️ 表格中部分中文列（如 Away Blocked Shot）為空，容易造成欄位含義不清，建議補充完整
- ⚠️ PESA 前綴規則中「沒空格，這邊以客隊方式呈現」可能被誤讀，需確認解析時是否應自動移除 Home/Away 前綴並保留無空格形式
- ⚠️ 美式足球的某些 B365 事件（如 Red Zone Efficiency）中文列為空，可能影響展示，需確認是否需要中文文案

---

### TCZB-708 [CrawlerAgent] - KU 每節比分

> Confluence 頁面 ID：15402278  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=15402278)  
> 摘要檔：[processed/15402278-summary.md](../../confluence/processed/15402278-summary.md)  
> Confluence 最後更新：2021-04-06  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義了取得進行中比賽每節比分的需求。核心規則為：先從 result 頁面儲存分數資料，當顯示 inplay 比分時，若有已儲存的節比分細節（如 [[25,25],[50,75]]），則以此替換總分；若無儲存資料，則以比賽總分作為單一節比分（[[總分,總分]]）。

**關鍵業務規則**：
- 需從 result 頁面取得並儲存分數資料
- 顯示 inplay 比分時，優先使用已儲存的節比分細節（如 [[25,25],[50,75]]）；若無儲存資料，則分數細節僅為 [[總分, 總分]]
- 設計有「節比分 = 現有總分 - 儲存總分」的自動計算方法，但文件中明確標注為「先不做」，暫不實作

**注意事項**：
- ⚠️ 文件標注「先不做」的節比分自動計算功能，需人工確認後續是否已實作或規則變更
- ⚠️ 文件建立於 2021 年 4 月，可能已過時，建議與現有系統行為比對確認

---

## 技術設計類

### TCZB-983[PriceBackendService] - 直播頻道維護

> Confluence 頁面 ID：24086183  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=24086183)  
> 摘要檔：[processed/24086183-summary.md](../../confluence/processed/24086183-summary.md)  
> Confluence 最後更新：2021-09-27  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件提供直播頻道的後台管理功能設計，包含單一頻道的新增、開關、批次查詢與訊號編輯（標記待實作）。定義了 GameLive 資料表結構，並規範查詢 API 支援依球種、日期、頻道開關及訊號狀態過濾。

**關鍵設計決策**：
- 編輯頻道訊號 (PUT channels) 標記為「暫時不做，日後有訊號再說」，顯示該功能在設計階段被延後
- 查詢 API 使用 query string 傳遞篩選參數，而非放在 request body

**影響範圍**：
- 查詢頻道時 channelSwitch 參數 -1 表全部、0 表關閉、1 表開啟；signalStatus 參數 -1 表全部、0 表無訊號、1 表有訊號
- 頻道開關由 Enabled 欄位控制，可透過 PUT channel/open 或 PUT channel/close 單獨操作
- 新增頻道時須提供 ChannelID、Date、Url、Enabled、GameType、League、Team_H、Team_A、GTime 等完整欄位

**注意事項**：
- ⚠️ 文件最後更新於 2021-09-27，部分設計可能已變更或過時，需參照現行實作
- ⚠️ 編輯頻道訊號功能備註「日後有訊號再說」，現況未知，需人工確認是否已實作
- ⚠️ 查詢參數 signalStatus 的 0 對應 'Null'，實際語意（無訊號 vs. 資料為空）需人工確認

---

### TCZB-2441 [SportKing] - 賽果資訊

> Confluence 頁面 ID：44665035  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=44665035)  
> 摘要檔：[processed/44665035-summary.md](../../confluence/processed/44665035-summary.md)  
> Confluence 最後更新：2023-01-18  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義 SportKing 賽果最終列表頁面的功能設計，包含呼叫 GET /game/gameresult 取得最終賽事資料，並在前端以時區加選擇日期與前一天資料過濾的方式顯示，以及將 resultInfo 改以彈跳窗呈現。

**關鍵設計決策**：
- 時區過濾邏輯放在前端處理，以確保顯示結果能正確對應使用者所在時區的日期
- 參考 AiScore 頁面設計，使賽果列表的整體體驗與業界主流一致
- resultInfo 改用彈窗呈現，降低列表的資訊密度，提升可讀性

**影響範圍**：
- 查詢賽果時，前端需同時撈取選擇日期和選擇日期-1 的資料，再依照前端時區轉換後的時間過濾出目標日期的賽事
- 比賽詳細統計資料（resultInfo，包含兩分、三分、罰球）改為彈跳窗顯示，而非直接內嵌在列表

**注意事項**：
- ⚠️ 文件最後更新於 2023-01-18，可能已有後續變更，需確認 API 路徑與回應欄位是否仍有效
- ⚠️ Figma 設計連結可能已失效或變更，如需還原 UI 規則須確認最新設計稿

---

### TCZB-2893 [GameLiveService] - 賽事聊天室功能

> Confluence 頁面 ID：47223081  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47223081)  
> 摘要檔：[processed/47223081-summary.md](../../confluence/processed/47223081-summary.md)  
> Confluence 最後更新：2023-08-23  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文記錄了 GameLiveService 聊天室功能的重構，包括 SignalR Hub 介面的變更與升級至 .NET 6。因應球王聊天室需求，新增了對用戶等級（Rank）的參數處理，並調整了 AddChannel、ReceiveMessage 等方法的傳入傳出參數。

**關鍵設計決策**：
- 重整架構，修改聊天室 SignalR 相關函數，並升級至 .NET 6
- AddChannel 方法新增 UserInfo 參數（JSON），包含 Account、Name、Rank，以支援用戶等級處理
- ReceiveMessage 回傳格式變更，增加 DateTime、UserInfo（JSON）欄位，且回傳資料有順序要求
- 所有聊天室相關 func 新增對用戶等級（Rank）參數的處理，以因應球王聊天室需求

**影響範圍**：
- SignalR Hub 介面變更，與舊版不兼容，開發時需確認客戶端是否已更新

**注意事項**：
- ⚠️ 文檔標註「更改 Parameter」「更改回傳格式」，意味著與舊版不兼容，開發時需確認客戶端是否已更新

---

### TCZB-2910 [GameLiveService] - 球王社群聊天室

> Confluence 頁面 ID：47223385  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=47223385)  
> 摘要檔：[processed/47223385-summary.md](../../confluence/processed/47223385-summary.md)  
> Confluence 最後更新：2023-10-06  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件定義在 GameLiveService 中新增社群聊天室模組的技術設計。內容包含 RESTful API 用於群組管理（新增、上傳圖片、取得群組及最近訊息、取得對話紀錄等），以及基於 SignalR 的即時通訊互動（加入頻道、收發訊息、按讚、取消讚、心跳、人數統計等）。資料庫使用 MySQL，歷史訊息採雙引擎策略（MEMORY 快取 + ndbcluster 持久化），僅保留近 7 天訊息。

**關鍵設計決策**：
- 歷史訊息儲存採用雙儲存引擎：MEMORY 引擎用於高效能快取，ndbcluster 用於持久化與災備還原，避免資料全丟失
- 對話紀錄只保留 7 天，以控制儲存與查詢成本
- 採用 SignalR 實現即時通訊，定義對應的 Hub 方法來處理加入/離開頻道、收發訊息、按讚互動與人數同步，並有心跳維持連線
- 按讚與取消讚透過獨立 SignalR 方法實現，並區分操作成功回傳（ReceiveLikeMessageResult）與通知其他人（ReceiveNotificationLikeMessage），解耦操作結果與廣播
- 社群群組的圖示採用上傳 API 取得路徑，再存入 IconPath，而非直接儲存圖片 Binary
- 群組資訊可透過 ?cacheData=false 控制是否讀取快取，提供即時查詢選項

**影響範圍**：
- 社群聊天室必須登入後才能使用（SignalR 連線時需傳遞 userKey = user authKey）
- 對話紀錄僅保留近 7 天的訊息
- 社群群組權限由 GType 欄位定義：official 無法使用（可能保留給公告），normal 為一般會員使用，vip 為訂閱會員專用
- 快取用 MEMORY 引擎，持久化用 ndbcluster，若 MEMORY 重啟後資料遺失，則透過 ndbcluster 還原
- 圖片訊息透過 ChatType = 'image' 發送，圖片檔案需先透過群組圖片上傳 API 取得路徑

**注意事項**：
- ⚠️ 文件更新時間為 2023-10-06，可能已過時，需人工確認是否仍適用於現行 GameLiveService 實作
- ⚠️ Invoke Function 表中的「ReceiveAddGroupChatRoom」(接收加入頻道事件) 已被劃線廢棄，表示此方法已不再使用
- ⚠️ ChatRoomHistories 與 ChatRoomHistories_Backup 表結構相同，但未說明 Backup 表的清除或同步策略，需人工確認備份機制
- ⚠️ 問題清單為空（無已知問題），可能未更新實際開發中的待解決事項

---

### TCZB-2973 [GameLiveService] - 社群API

> Confluence 頁面 ID：55574638  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55574638)  
> 摘要檔：[processed/55574638-summary.md](../../confluence/processed/55574638-summary.md)  
> Confluence 最後更新：2023-10-03  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這份文件定義了 GameLiveService 中社群相關的 API 雛形，包含管理社群群組的 REST 端點（新增、查詢、更新）以及管理員 WebSocket 操作（加入/離開聊天室、訊息接收與刪除等）。許多功能僅有骨架，部分欄位空白，顯示設計尚未完成。

**關鍵設計決策**：
- 採用 REST API 與 WebSocket 並行的架構，管理端透過 WebSocket 收發即時事件，資料管理經由 REST 端點
- 新增與更新社群群組共用相同的 CommunityGroupDTO 結構，簡化資料模型
- 部分 WebSocket 事件（如禁止訪問、刪除訊息）尚未定義實際的函數名稱與參數，表明此階段僅先列出預期功能

**影響範圍**：
- 此為草稿文件，API 合約尚未完整定義，實作時需與 PO 確認細節

**注意事項**：
- ⚠️ 文件明顯為草稿狀態：API #3「取得聊天室會員」整列空白，Invoke Function #4、#5、#6 只有功能描述而無具體方法與參數，最終 #8 也是空列
- ⚠️ 更新社群組的路由誤植為 /gameliveservice/api/communitiesapi/groups/{id}（多了一個 'api'），應確認是否為筆誤
- ⚠️「禁止訪問」與「接收禁止訪問」功能完全空白，無從判斷是雙向事件還是管理端發起，實作時需與 PO 確認

---

### TCZB-3152 [GameLiveService] - 社群功能

> Confluence 頁面 ID：55577209  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577209)  
> 摘要檔：[processed/55577209-summary.md](../../confluence/processed/55577209-summary.md)  
> Confluence 最後更新：2024-03-06  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件描述 GameLiveService 社群功能的擴充設計，包括：將公開、賽事、個人聊天室拆分至不同 SignalR Hub 連線；會員加入社群時將記錄寫入 Redis 與 Hub Group；新增/修改社群 API（POST/PUT/GET）以支援個人群組類型，群組資料結構加入版主（owner）與簡介（description）；DB 新增 community_groups.owner、community_groups.description 以及聊天紀錄表的大頭貼路徑欄位；SignalR 調用增加 HeadShotPath 與 LeaveGroupChatRoom 的 account 參數。

**關鍵設計決策**：
- 不同類型的聊天室（個人、公用、賽事頻道）拆分到不同 Hub 連線，以隔離負載與權限控制
- 會員加入社群聊天室時，同時寫入 Redis（快取）與 Hub Group（即時通訊群組），確保持續連線管理與快取一致性
- DB 聊天紀錄表增加 HeadShotPath 欄位，以在歷史訊息中保留大頭貼路徑，避免會員更換頭像後歷史訊息圖片失效
- API 查詢群組時支援 cacheData 參數，提供 Redis（快取）與 Cassandra（持久層）兩種讀取路徑，平衡效能與資料可靠性

**影響範圍**：
- 建立或更新社群群組時，若 gType = 'personal'，owner 欄位不可為空
- community_groups.owner 欄位為空表示公開群組無擁有者，值 'admin' 代表管理者，否則為擁有者帳號
- 查詢群組列表時，參數 cacheData=true 從 Redis 讀取，cacheData=false 從 Cassandra 讀取
- SignalR 傳送聊天訊息時，message json 須包含 'HeadShotPath' 欄位，ChatType predict 表示預測單
- SignalR 離開聊天室需傳入 account 參數

**注意事項**：
- ⚠️ 文件出自 TCZB Sprint 153（舊項目），後續可能有變更，需人工確認後續版本是否有改動
- ⚠️ 文件僅描述擴充設計，未提及原有功能的向下相容處理方式，開發時需確認舊版 API 與 SignalR 用戶端的相容性

---

### TCZB-3187 [GameLiveService] - 社群版主推薦預測

> Confluence 頁面 ID：55577750  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55577750)  
> 摘要檔：[processed/55577750-summary.md](../../confluence/processed/55577750-summary.md)  
> Confluence 最後更新：2024-03-18  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文檔描述了 GameLiveService 中社群版主推薦預測的功能實現：在聊天室顯示版主預測注單，並擴展了消息推送機制。當每個群組發送消息後，新增對 ReceiveGroupChatRoomLastMessage 的調用，用於推送該群組的最後一條消息（含 gid 和 groupLastMessage 字段）。

**關鍵設計決策**：
- 新增 ReceiveGroupChatRoomLastMessage 作為獨立的接收器，與原有的 ReceiveGroupChatRoomMessage 分離，專注於推送群組最後一條消息
- SendGroupChatRoomMessage 的參數保持不變，但在內部邏輯中增加向 ReceiveGroupChatRoomLastMessage 發送消息的步驟，實現全頻道最後消息的同步更新
- ReceiveGroupChatRoomLastMessage 的回傳格式定義為包含 gid（群組ID）和 groupLastMessage（最後消息內容）的對象

**影響範圍**：
- 每當群組發送消息，必須向 ReceiveGroupChatRoomLastMessage 推送該群組的最後一條消息，消息格式為 { gid, groupLastMessage }

**注意事項**：
- ⚠️ 本文檔依賴 TCZB-3152 [GameLiveService] - 社群功能的實現，需確認其詳細定義

---

### TCZB-3295 [GameLiveService] - 社群功能

> Confluence 頁面 ID：55579148  
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=55579148)  
> 摘要檔：[processed/55579148-summary.md](../../confluence/processed/55579148-summary.md)  
> Confluence 最後更新：2024-06-05  
> 摘要最後同步：2026-05-27  
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
本文件設計 GameLiveService 的社群推薦預測功能，定義了五個 REST API 用於新增、查詢、更新預測注單與推薦說明。預測資料使用 Redis 儲存，並透過 SignalR Invoke 通知前端重整，另有定時清理前天以前資料的機制。

**關鍵設計決策**：
- 選用 Redis 作為社群推薦預測注單的儲存空間，推測是為了低延遲讀取與方便設定生命週期（TTL/定時清理）
- 採用 SignalR Invoke 而非輪詢來通知前端更新，以達到即時響應並減少伺服器負載
- 透過內部 Thread 實現定時清理，避免依賴外部調度服務，簡化部署架構

**影響範圍**：
- 社群推薦預測只記錄賽事欄位(LID, GDate, GID)、注單 ID 與說明(Description)，不儲存完整注單內容
- 收到賽事預測結果通知後，若該賽事存在於社群 Redis 中，則對該群組發送 SignalR Invoke(SendGroupChatRoomReloadSignal)，前端收到後需重新請求預測資料
- 使用內建 Thread 定時清除社群前天以前的推薦預測注單，確保 Redis 只保留近期數據
- 透過 DeleteCommunityGroupChatRoomMessage 刪除 predict 類型的聊天訊息時，前端須將該訊息替換為「此對話已經被移除」，且重新進入聊天室時不再顯示該訊息

**注意事項**：
- ⚠️ 文件為單一 Sprint 任務設計，未說明 Redis key 結構與 SignalR Hub 具體設定，實際實作可能與此不同，需人工確認
- ⚠️ 注單狀態 (Status)、勝負 (WinLoss) 等欄位語意僅透過範例展示，無明文定義，對 AI 解析時可能產生歧義

---

## 歷史決策類

_（無相關文件）_

---

## 操作手冊類

_（無相關文件）_

---

## 注意事項

- ⚠️ 所有 Confluence 文檔更新時間集中在 2021-2024 年，明顯缺乏最新文檔，AI 開發時必須參照現行實際程式碼與資料庫結構
- ⚠️ 業務規則類文檔（PlayByPlay Name Mapping List）的權威性有限，因更新於 2022-01-13，數據源名稱可能有變動
- ⚠️ 早期設計文檔（如 TCZB-708 每節比分）標注「先不做」的部分，需人工確認後續是否已有實作或已被廢棄
- ⚠️ 聊天室相關設計（特別是 TCZB-2893、TCZB-3152）涉及 SignalR Hub 介面變更與向後相容性問題，AI 開發時需特別注意
- ⚠️ 部分設計文檔（如 TCZB-2973 社群API）明顯為草稿狀態，API 合約不完整，不可直接用於生產環境