# zaiservice — DB 操作邊界

> 產出時間：2025-04-10 14:30
> **README**：[./README.md](./README.md) — 職責、技術棧、Table 清單、API 路由、使用場景、服務相依（**本文件不重複**）
> ⚠️ AI 產出，需資深工程師審核後生效

---

## member

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra member keyspace | owner | Schema：[db/member.md](../../db/member.md) · 語意：[db/member-detail.md](../../db/member-detail.md) |

### 寫入限制

- **authkey**：僅註冊時由系統產生（透過 `ConvertToAuth` 對帳號 Hash 並正規化），不可手動修改
- **password**：僅允許透過 `UpdHashPassword` 更新，須經雜湊處理後儲存
- **email**：註冊時須檢查 `forbidden_email_domains` 表，禁止網域之電子郵件不得註冊
- **gameusers.memberships**：會員資格（VIP）僅能由特定系統流程（如付費升級）寫入，不可直接手動修改 `list<text>` 內容
- **gameusers.gamecount**：僅能在使用者完成一場遊戲後由系統遞增，不可直接 UPDATE
- **gamerobots.enabled**：僅管理後台可修改機器人啟用狀態
- **gamesublogs**：訂閱記錄由付費系統寫入，本服務僅 READ
- **gameusers_banned**：封禁記錄僅由管理後台或自動封禁流程寫入，一般 API 不可寫入

### 讀取規則

- **登入驗證**：`WHERE authkey=? AND status=正常` — 封禁/停用帳號（`status≠1` 或存在對應 `gameusers_banned` 記錄）不可登入
- **email 查詢**：`WHERE email=?` 使用索引查詢，但須檢查該 email 網域是否在 `forbidden_email_domains` 中
- **訂閱記錄查詢**：`WHERE authkey=?` 並以 `subtime`、`tradeno`、`addtime` 排序（Clustering Key），時間範圍過濾需指定分區鍵 `authkey`
- **機器人清單**：`WHERE enabled=1`（`gamerobots`）以取得啟用的機器人帳號列表，用於自動遊戲流程
- **封禁帳號判斷**：查詢 `gameusers_banned` 時須指定 `authkey` 以判斷該帳號是否被封禁，不可無分區鍵掃描
- **Apple 遊戲資訊**：`appleinfos_game` 以 `id` 為主鍵做單筆查詢，不可無條件掃描
- **遊戲用戶排行查詢**：`gameusers` 依 `rank` 排序時需注意 Cassandra 無法全域排序，應避免使用 `ALLOW FILTERING`

### 不可回傳欄位

- **password**：密碼雜湊值任何 API 不得回傳
- **authkey**：內部認證金鑰不對外暴露，僅用於 Session/Token 內部驗證
- **gamesublogs.tradeno**：交易編號屬敏感金流資訊，僅供內部對帳
- **gameusers.memberships**：會員資格列表視為內部資料，不對外暴露所有會員身份

---

## predict

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra predict keyspace | writer / reader | Schema：[db/predict.md](../../db/predict.md) · 語意：[db/predict-detail.md](../../db/predict-detail.md) |

### 寫入限制

- **activities_cycles.resultcount**：僅由 AI 計算服務寫入（如 `AIPredictService`），不可手動修改
- **activities_record.winbets**：由活動結算流程寫入（`list<text>`），不允許外部 API 直接寫入；`restday` 由系統自動計算，不可手動更新；`updatedate` 由系統自動設定
- **activities_winneraccounts.rank / profitpoint / winpercentage / predictcount**：由計算服務更新，對外唯讀
- **betpool_bets.betzcoin**：僅透過下注 API 寫入；`profitzcoin` 僅在結算時由系統寫入，不可直接 UPDATE
- **betpool_games.payout**：一旦設為 `true` 不得再修改為 `false`，僅在比賽結算時由系統設定
- **betpool_games.winresult**：僅在比賽結算時由系統寫入，對外唯讀
- **betpool_games.status**：由系統根據比賽生命週期自動變更，外部不可直接 UPDATE
- **betpool_games.hot / viponly / names / betoptions**：由管理後台配置，一般 API 僅讀取
- **calculatelog.done**：由週結算服務設定，記錄該週計算是否完成，不可手動修改
- **killeraccounts_BK.addtime / avgodd**：由預測服務每週計算後寫入；`lid`、`cid`、`account` 為複合主鍵，寫入時須與計算結果對應
- **predictbets_{gtype}（動態表）**：`profitpoint`、`usezcoins`、`ratio`、`status`、`winloss` 由 AI 計算後寫入；`enabled` 控制預測啟用狀態（`0` 時為殺手指南），由系統設定；`strategy_id` 為內部策略識別碼，系統自動分配；`args` 為附加參數，由系統寫入，對外唯讀
- **predictfilterreports**：由系統週期性產生報告時寫入，不可手動修改
- **settings_league**：`lids` 由管理後台配置，控制各遊戲類型下啟用的聯賽；一般 API 僅讀取

### 讀取規則

- **活動週期查詢**：`activities_cycles` 使用 `WHERE site=? AND activityevent=?`，並過濾 `enddate` 與 `endtime` 大於當前時間的活躍週期，避免回傳已過期活動
- **活動贏家排行**：`activities_winneraccounts` 使用 `WHERE site=? AND activityevent=? AND cid=?`，依 `rank` 排序（Clustering Key），需提供完整分區鍵
- **活動參與記錄**：`activities_record` 查詢須指定完整複合主鍵 `WHERE site=? AND eventname=? AND account=?`，不可僅以 `account` 掃描
- **可下注獎池比賽**：`betpool_games` 使用 `WHERE status=2 AND payout=false` 過濾賽前且未支付的場次；可搭配 `hot`、`viponly` 過濾
- **投注記錄查詢**：`betpool_bets` 使用 `WHERE gid=? AND account=?` 以利用複合主鍵 `(gid, id)` 精確查詢單一帳號對單一遊戲的下注
- **殺手帳號查詢**：`killeraccounts_BK` 使用 `WHERE lid=? AND cid=?` 查詢特定聯賽週期下的殺手帳號，可進一步過濾 `account`
- **計算日誌**：`calculatelog` 使用 `WHERE weekid=?` 確認該週是否已完成結算，不可無分區鍵掃描
- **預測記錄查詢**：`predictbets_{gtype}` 表動態，查詢時需指定 `lid` 與 `gdate`（或其他分區鍵），常見查詢為 `WHERE lid=? AND gdate=? AND gid=? AND account=?` 或依 `account` 過濾，須根據實際分區鍵進行，避免全表掃描
- **預測過濾報告**：`predictfilterreports` 使用 `WHERE gametype=? AND lid=? AND reportdate=?` 查詢特定遊戲類型的報告，不可無分區鍵掃描
- **聯賽設定查詢**：`settings_league` 使用 `WHERE gametype=?` 讀取該遊戲類型下的所有啟用聯賽 (`lids`)

### 不可回傳欄位

- **betpool_bets.id**：內部下注記錄 ID，不對外公開
- **betpool_games.winresult**：比賽結果在未結算前不得對玩家提前揭露
- **predictbets_{gtype}.args**：內部附加參數，可能包含配置細節，不對外回傳
- **predictbets_{gtype}.strategy_id**：內部策略識別碼，僅供內部使用

---

## news

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra news keyspace | owner | Schema：[db/news.md](../../db/news.md) · 語意：[db/news-detail.md](../../db/news-detail.md) |

### 寫入限制

- **llmhashkey**：`ainews` / `ainews_gs` / `ainews_lt` 中的 `llmhashkey` 由系統根據 `llmsettings` 自動計算哈希後寫入，不得手動指定或修改
- **status**：狀態欄位 (`2`=賽前, `0`=實況, `1`=賽後, `>2`=生成中)，僅由 `GenGameService` 或 `NewsBuilder` 依比賽狀態轉換寫入，外部 API 不可直接 UPDATE
- **used**：由 `IWriteNewsService.FixNewsUsed` 在文章發布後標記為已使用 (`1`)，不可手動改回 `0`
- **anwser / reanwser**：由 AI Provider（`AIProvider`）寫入的生成內容，手動操作僅能透過管理後台（`EditorArticleService`）修改
- **question**：由系統根據比賽資訊構造的 LLM 問題，不應由外部 API 直接寫入
- **createtime**：由系統生成（格式 `yyyy-MM-dd HH:mm`），不可手動設定
- **articleid**：由社區發布 API（`APIProvider`）寫入，寫入後不可修改
- **bets**：由 `IAIPredictService.WriteBetInfoToNews` 寫入，內容為 `SimpleBet` JSON 串接列表，不允許其他途徑修改
- **llmsettings**：僅由 `AIProvider` 設定 LLM 調用參數（model、temperature 等），不可外部更新
- **aifunshits.funsname**：主鍵，新增後不可修改
- **aireports.results**：由 `IAIPredictService.CalcuteAIPredicts` 計算後寫入，不可手動改寫

### 讀取規則

- **賽前新聞查詢**：`WHERE gdate=? AND gtype=? AND lid=? AND gid=? AND status=2` — 僅回傳 status=2（賽前）的新聞，避免將實況或賽後新聞顯示為賽前分析
- **歷史新聞查詢**：`WHERE gdate=? AND gtype=? AND lid=?` — 需指定分區鍵 `gdate`，可搭配 `gtype`、`lid` 等 clustering key 進行範圍查詢，不可無分區鍵掃描
- **新聞使用頻率統計**：`SELECT used FROM ... WHERE gdate IN ?` — 因 Cassandra 不支援跨分區聚合，批次統計須在應用層合併，不可使用 `ALLOW FILTERING`
- **AI 回答內容過濾**：若有審核機制，應過濾 `anwser` 不為空且 `status` 已達發布條件（如 `status=1` 賽後）的記錄才對外提供
- **工作區 hints 讀取**：`aifunshits` 全量查詢時，因 `funsname` 為 partition key，需使用 List 或指定 `funsname`，避免無條件掃描

### 不可回傳欄位

- **question**：AI 生成的原始問題可能包含內部提示（prompt）模板或敏感參數，對外介面不應回傳
- **llmsettings**：包含 LLM 模型名稱、溫度設定等內部配置參數，不對外暴露
- **llmhashkey**：用於內部去重與哈希比對，不對外提供

---

## pricecenter

### 資料來源與角色

| 資料來源 | 角色 | 定義 |
|---------|------|------|
| Cassandra pricecenter keyspace | reader | Schema：[db/pricecenter.md](../../db/pricecenter.md) · 語意：[db/pricecenter-detail.md](../../db/pricecenter-detail.md) |

### 寫入限制

- 本服務對 pricecenter keyspace 僅有讀取權限，不寫入任何表。所有資料寫入由 **pricecenter-service** 負責。

### 讀取規則

- **帳號啟用檢查**：`WHERE account=? AND enabled=1` — 查詢特定站台帳號（如 `accounts_AU8`、`accounts_TG` 等）時，需同時確認 `closetime` 為 `null` 或尚未到達（`closetime` 有值且小於當前時間表示帳號已關閉），才允許相關操作（如遊戲登入或投注）。
- **操作日誌查詢**：`WHERE date=? AND addtime>=? AND addtime<=?` — 查詢 `actionlog` 必須指定日期分區鍵 `date`，可搭配 `addtime`、`user`、`gametype` 等 clustering key 進行範圍過濾與排序，禁止跨分區全表掃描。

### 不可回傳欄位

- **password**：任何站台帳號表（`accounts_*`）的密碼欄位，無論雜湊與否，均不對外回傳。
- **handler**：內部處理器配置（`map<text, text>`），可能包含敏感路由或權限資訊，不對外暴露。
- **phone**：電話號碼屬個人隱私，除非必要（如內部帳號驗證），不對外直接回傳。

---

## Redis

| 操作 | Key | 時機 | TTL / 說明 |
|------|-----|------|-----------|
| SET / GET | `session:{authkey}` | 登入成功後 | TTL 30分鐘，滑動續期 |
| DEL | `session:{authkey}` | 登出或 Token 失效 | 主動刪除 |
| SET | `robot:check:{account}` | 機器人檢查 API | TTL 5分鐘，快取機器人啟用狀態（`chkRobotAPI`） |
| SET | `predict:activemsg:{site}:{activityevent}:{cid}` | 活動訊息更新時 | TTL 配合活動週期 `enddate` ＋ `endtime`，期間內快取活動狀態 |

---

## 本服務不負責

| 事項 | 負責服務 | 說明 |
|------|---------|------|
| 預測投注結算 | predict-service | `predictbets` 由預測服務寫入，本服務僅讀取用於顯示用戶戰績 |
| 比賽資料維護 | pricecenter-service | `games` / `leagues` / `teams` 由賽事服務管理 |
| 成員資金管理 | member-service | 玩家 `zcoin` 餘額、點數等由 member 服務維護 |
| AI 新聞內容生成 | news-service | `ainews` / `aireports` 由 AI 新聞服務產生，本服務僅讀取展示 |

---

## 常見錯誤

- ❌ 直接 `UPDATE betpool_bets SET profitzcoin=?` 未經結算邏輯 → ✅ 必須經由 `BetPoolSettlement` 服務流程處理
- ❌ 讀取 `activities_cycles` 未過濾已結束週期，導致玩家仍可對已結束活動操作 → ✅ 查詢時加上 `WHERE enddate >= currentDate AND endtime >= currentTime`
- ❌ 對 `betpool_games` 使用 `ALLOW FILTERING` 大量掃描 → ✅ 利用 `id`（Partition Key）精確查詢，或搭配 `status` 與 `payout` 的正確認知
- ❌ 將 `betpool_games.betoptions` 或 `names` map 欄位在未處理語言環境時直接回傳 → ✅ 應先比對 `names` 中的語言 key（如 `en`、`zh`）再回傳對應顯示文字
- ❌ 使用非分區鍵條件查詢 `gameusers` 表（如 `WHERE email=?`）時忽略索引限制，可能導致全表掃描 → ✅ 需使用 `CREATE INDEX` 建立的索引（如 `email` 欄位）進行查詢
- ❌ 查詢 `actionlog` 不帶 `date`，僅依 `user` 或 `addtime` 過濾 → ✅ 必須包含 `date` 分區鍵；若需要跨日期查詢，應拆分多次查詢或由應用層合併結果
- ❌ 只依賴 `enabled=1` 判斷帳號可用，未檢查 `closetime` → ✅ 帳號啟用檢查應同時確認 `closetime IS NULL OR closetime > toTimestamp(now())`，避免已排程關閉的帳號仍被放行