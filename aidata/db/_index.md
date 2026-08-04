# DB Schema 參考

此目錄包含各資料庫的 Markdown Schema 定義檔，供開發時查閱資料表結構、欄位定義與樣本資料。

## 資料庫一覽

| 資料庫類型 | Keyspace / Database | 說明 | Schema | 使用脈絡 |
|-----------|-------------------|------|--------|----------|
| PostgreSQL | `aireviews` | AI Review 系統（9 表） | [aireviews.md](./aireviews.md) | [詳](./aireviews-detail.md) |
| MySQL | `newlottery` | 新運彩資料庫（4 表） | [newlottery.md](./newlottery.md) | [詳](./newlottery-detail.md) |
| MySQL | `sport` | 運動賽事資料庫（7 表） | [sport.md](./sport.md) | [詳](./sport-detail.md) |
| MySQL | `stock` | 股票資料庫（8 表） | [stock.md](./stock.md) | [詳](./stock-detail.md) |
| MySQL | `tokens` | Token / Licence 管理資料庫（2 表） | [tokens.md](./tokens.md) | [詳](./tokens-detail.md) |
| Cassandra | `ads` | 廣告管理（3 表） | [ads.md](./ads.md) | [詳](./ads-detail.md) |
| Cassandra | `community` | 社群討論版（1 表） | [community.md](./community.md) | [詳](./community-detail.md) |
| Cassandra | `feedback` | 回饋與問答，分運動博彩與股票兩條業務線（7 表） | [feedback.md](./feedback.md) | [詳](./feedback-detail.md) |
| Cassandra | `gamesettings` | 遊戲設定（19 表） | [gamesettings.md](./gamesettings.md) | [詳](./gamesettings-detail.md) |
| Cassandra | `member` | 會員管理（21 表） | [member.md](./member.md) | [詳](./member-detail.md) |
| Cassandra | `news` | 新聞與 AI 內容（17 表） | [news.md](./news.md) | [詳](./news-detail.md) |
| Cassandra | `payment` | 金流與報表（17 表） | [payment.md](./payment.md) | [詳](./payment-detail.md) |
| Cassandra | `predict` | 預測投注與活動（84 表） | [predict.md](./predict.md) | [詳](./predict-detail.md) |
| Cassandra | `pricecenter` | 價格中心（825 表，規模最大） | [pricecenter.md](./pricecenter.md) | [詳](./pricecenter-detail.md) |
| Cassandra | `product` | 產品商店（6 表） | [product.md](./product.md) | [詳](./product-detail.md) |
| Cassandra | `tradegame` | 賽事交易（8 表） | [tradegame.md](./tradegame.md) | [詳](./tradegame-detail.md) |

## 套用原則

處理 DB 操作任務時，先確認使用的資料庫類型：

- **PostgreSQL** → 查 `./db/aireviews.md`
- **MySQL** → 查 `./db/{database_name}.md`，Database 名稱即檔名（如股票相關查 `stock.md`）
- **Cassandra** → 查 `./db/{keyspace_name}.md`，Keyspace 名稱即檔名（如價格中心相關查 `pricecenter.md`）

若需查閱特定資料表欄位定義，在對應檔案中搜尋 `## Table: {table_name}`、`完整名稱` 或欄位名稱即可找到完整結構。

> 查閱 Schema 後，應優先閱讀同列的 **使用脈絡** detail 檔，其中包含欄位限制、讀寫規則、不可回傳欄位與常見錯誤等業務細節。

## 業務線說明

系統同時服務兩條業務線，表名後綴加以區分：

- `_sport`：運動博彩
- `_stock`：股票交易

## 運動種類代碼對照

表名後綴的運動縮寫（如 `games_BK`、`odds_SC`）：

| 代碼 | 英文 | 中文 |
|------|------|------|
| BS | Baseball | 棒球 |
| BK | Basketball | 籃球 |
| HL | Ice Hockey | 冰上曲棍球 |
| SC | Soccer | 足球 |
| FL | Football | 美式足球／橄欖球 |
| ES | E-Sports | 電競 |
| TN | Tennis | 網球 |
| VB | Volleyball | 排球 |
| BM | Badminton | 羽毛球 |
| SQ | Squash | 壁球 |
| HB | Handball | 手球 |
| FB | Floorball | 星地冰球 |
| FS | Futsal | 室內五人制足球 |
| MA | Boxing / MMA | 綜合格鬥 |
| RU | Rugby Union | 聯合式橄欖球 |
| DT | Darts | 飛鏢 |
| SN | Snooker | 撞球 |
| TB | Table Tennis | 桌球 |
| RL | Rugby League | 聯盟式橄欖球 |
| WP | Water Polo | 水球 |
| BD | Bandy | 俄式冰球 |
| BV | Beach Volleyball | 沙灘排球 |
| BW | Bowls | 草地滾球 |
| GS | Gaelic Sports | 蓋爾式運動 |
| PL | Pool | 花式撞球 |
| BL | Bowls | 草地滾球 |
| CK | Cricket | 板球 |
| BC | Baccarat | 百家樂 |
| BG | Bowling | 保齡球 |
| GF | Golf | 高爾夫 |
| RC | Racing | 賽車 |
