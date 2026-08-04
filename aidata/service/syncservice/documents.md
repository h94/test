# syncservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-26 22:28
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

<!--
文件類型說明：
  business_rule    業務規範（功能應該怎麼運作）← 最重要，AI 開發時必讀
  technical_design 技術設計（如何實作）
  decision_record  歷史決策（為什麼這樣做）
  operation_guide  操作手冊（怎麼操作）

優先順序：business_rule > decision_record > technical_design > 其他
當此文件和 service-detail.md 有衝突時，以此文件為準。
-->

## 業務規範類

> **文件類型**：decision_record（從中提取業務規則）
>
> 本節業務規則來自「Cursor使用心得-1.直接開始」，原始目的為記錄開發過程，
> 但內容包含明確的業務規則，供 AI 開發參照。

### 核心業務規則提取

> Confluence 頁面 ID：79469243
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469243)
> Confluence 最後更新：2026-04-15
> 摘要產出時間：2026-05-26

**摘要**：
記錄使用 Cursor 開發 zsyncservice 的完整流程與經驗。核心業務為從 Kafka 取得 GameData，根據 MySQL 的 Game Mapping 更新 odds。涵蓋資料流設計、框架限制、重構方向與完整的業務處理邏輯。

**關鍵業務規則**：
- Kafka 訊息需用正規表達式判斷是否包含 AppSetting 中 GameTypes 的值（對應 BS/BK/SC）
- 依 AIData 的 game.json 將訊息字串反序列化為 Game Model
- 每 5 分鐘檢查 MySQL 昨天/今天/明天中 result_h != -1 的所有比賽，將 gameid 與 mapping 快取在跨 thread 可用的記憶體中
- Mapping 欄位格式為 Game.Site + '_' + GameID
- Queue 中的資料若無命中 mapping 則拋棄，命中則解析 Game.Odds 並更新對應 {gameType}_param 表（如 bs_param）
- Update cache 與 DB 時需依 gameType 判斷對應的表：BS 對 bs_games、BK 對 bk_games、SC 對 sc_games
- 所有 Debug 日誌必須改用 IKafkaLogger 記錄
- 所有 MySQL 查詢功能必須集中於 GameProvider
- Odd 更新邏輯須透過 GameOddsParamWriter 並以 DI 注入方式使用
- 資料庫存取必須使用 EC Core 的 IMySQLManager，不可使用原生 MySQL 套件

---

## 歷史決策類

<!--
說明為什麼當時這樣做，避免未來重複踩坑或誤改。
-->

### Cursor使用心得-1.直接開始

> Confluence 頁面 ID：79469243
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79469243)
> Confluence 最後更新：2026-04-15
> 摘要產出時間：2026-05-26
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**決策背景**：
開始使用 Cursor 開發 zsyncservice，需要面對 EC Core 框架內部庫的限制，以及建立完整的資料同步流程。

**決策結論**：
- 採用 Visual Studio + Cursor 組合：Cursor 生成程式碼，VS 編譯與除錯
- 準備一個空但有 zb ecframework 架構的專案作為起點，而非直接引入完整 EC Core，因為 Cursor 引用內部庫時會崩潰（即使是 Premium 版）
- 放棄使用 EC Core 的 KafkaLogger 與 MySQL Manager，改為手動實現後再逐步遷移至符合框架的 GameProvider 與 IMySQLManager
- 後期重構：將散落的 MySQL 程式碼集中至 GameProvider，odd 更新改由 DI 注入的 GameOddsParamWriter 處理，並強制使用 IMySQLManager

**影響**：
- 架構上必須採用 DI 注入方式使用 GameProvider 和 GameOddsParamWriter
- 不可使用原生 MySQL 套件，必須透過 IMySQLManager
- 所有日誌必須使用 IKafkaLogger
- Cursor 使用內部庫的崩潰問題在記錄時點仍存在，後續使用需注意

---

## 注意事項

<!--
所有文件相關的注意事項統一整理在此。
-->

- ⚠️ **Cursor 框架限制**：Cursor 無法正確使用內部 EC Core 框架的 Library（如 KafkaLogger、MySQL Manager），嘗試要求使用會造成崩潰。此限制在記錄時（2026-04-15）仍存在，需人工確認最新版 Cursor 是否已改善
- ⚠️ **param 表名確認**：步驟 7 提到 param 表參考 bk_param，但依 gameType 應對應 bs_param、bk_param、sc_param，實際表名需人工確認
- ⚠️ **資料庫 schema 來源**：描述中 AIData 內的 dbschema.sql 是從 pricecenter keyspace 匯出的，但後續開發應依實際同步服務的目標資料庫為準
- ⚠️ **文件類型判定**：所有 summary 均來自同一份 Confluence 文件（pageId=79469243），原始類型為 decision_record。此處依內容將其業務規則提取至業務規範類，開發決策與背景歸入歷史決策類。若有多份不同文件需整合，請確認分類正確性。