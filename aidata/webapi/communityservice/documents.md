# communityservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

### TCZB-4038 [球王] - 討論區黑名單

> Confluence 頁面 ID：79466166
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79466166)
> 摘要檔：[processed/79466166-summary.md](../../confluence/processed/79466166-summary.md)
> Confluence 最後更新：2025-11-07
> 摘要最後同步：2026-05-27

**摘要**：
本文件定義討論區黑名單功能需求：用戶可在文章右上角將其他用戶加入黑名單，屏蔽後無法瀏覽該用戶文章；關注頁面提供黑名單列表與解除屏蔽；官方帳號不顯示黑名單選項；操作有確認彈窗。明確了屏蔽觸發、提示文案及少數官方帳號排除規則。

**關鍵業務規則**：
- 加入黑名單時彈窗提示：「屏蔽後將無法瀏覽該用戶的文章，確定要將該用戶加入黑名單? (加入後可至關注列表修改)」
- 官方帳號清單（EgD47bFmYzw、ET38BPQkRHd、GtNxh3IOfzz）不顯示「加入黑名單」按鈕
- 確認加入黑名單後刷新當前頁面
- 黑名單可通過關注頁面瀏覽與解除屏蔽

**注意事項**：
- ⚠️ 官方帳號清單為寫死的三個 ID，需確認是否需動態配置或後續維護
- ⚠️ 文件未定義黑名單與現有封鎖/關注功能的互動（如已關注是否自動取消等），需人工確認

### TCZB-4117 [CommunityService] - 熱門文章

> Confluence 頁面 ID：79467202
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79467202)
> 摘要檔：[processed/79467202-summary.md](../../confluence/processed/79467202-summary.md)
> Confluence 最後更新：2025-12-16
> 摘要最後同步：2026-05-27

**摘要**：
文件定義了熱門文章的計算公式，包含時間權重、按讚權重、回文權重及字數權重，並針對一般文章與預測文章設定不同的時間範圍與係數。後台線程每小時批次更新文章熱門分數與狀態，API 則合併置頂文章與熱門文章回傳，每頁最多 20 筆。此文件對 AI 開發社區服務的熱門文章模組提供了完整的業務邏輯與資料流。

**關鍵業務規則**：
- 熱門分數公式：hot_score = (0.1 × (72 - (now - publish)小時) + 1 × (文章按讚數 + 回文按讚數) + 3 × 非本人文章回文數) × 系數 × 字數權重。系數：一般文章或預測文章未結束為 1，預測文章且比賽已結束為 0.5。
- 字數權重：100 字以上 ×1，50~99 字 ×0.8，25~49 字 ×0.5，25 字以下 ×0。
- 熱門時間範圍：一般文章發布後 3 天內，預測文章發布後 2 天內，超出此範圍不列入計算。
- 熱門門檻：分數 >= 15 才算熱門。
- 後台線程每小時：取出 3 天內一般文章及 2 天內預測文章，計算分數並寫入 hot_score，分數達標者設 hot = True；同時將超過時間範圍且 7 天內的文章設 hot = False 並將分數歸零。
- API 取得熱門文章：搜 hot=True 並依 hot_score desc, create_timestamp desc 排序；第一頁時將所有置頂文章加在清單最前面，每頁固定 20 筆。
- API 路由：GET /communityservice/api/community/{gameType}/hot_articles，query 參數 index（發文時間戳，用於遊標分頁）或 page（頁碼），未填傳回第一頁。

**注意事項**：
- ⚠️ 公式中的「非本人文章回文數」在範例中未顯式區分，實作時需確認回文是否排除作者本人。
- ⚠️ 置頂文章之間的排序規則未明確定義，目前推測可能是按置頂時間或原始文章時間，需人工確認。
- ⚠️ API 參數 index 具體用途（可能是時間戳遊標）與 page 的分頁互動需參考實作確認。

---

## 技術設計類

### 新運彩 DB table

> Confluence 頁面 ID：79470707
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470707)
> 摘要檔：[processed/79470707-summary.md](../../confluence/processed/79470707-summary.md)
> Confluence 最後更新：2026-05-22
> 摘要最後同步：2026-05-26

**摘要**：
定義新運彩社群功能的資料庫結構：看板（Forums）使用 Cassandra 儲存，討論標題（Subjects）與留言（Comments）使用 Meilisearch 索引。詳細列出各資料表的欄位名稱、型別、描述與索引屬性，可幫助 AI 開發時快速了解數據模型、查詢過濾與排序規則。

**關鍵設計決策**：
- 看板採用 Cassandra 作為儲存，因其結構單純，以 id 為 partition key 直接查詢。
- 討論與留言採用 Meilisearch 儲存，以支援全文檢索、屬性過濾（filterable）與排序（sortable），滿足社群搜尋場景。

**注意事項**：
- ⚠️ country_code 欄位標註「暫留」，實際可能尚未使用，需人工確認是否已移除。
- ⚠️ 文件中的連線 IP（192.168.55.80 等）可能為開發環境，正式環境位置需另行確認。
- ⚠️ Meilisearch 版本與連線資訊可能已過時，建議核對最新的部署設定。

### 球王社群 DB table

> Confluence 頁面 ID：79470702
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470702)
> 摘要檔：[processed/79470702-summary.md](../../confluence/processed/79470702-summary.md)
> Confluence 最後更新：2026-04-24
> 摘要最後同步：2026-05-26

**摘要**：
這份文件定義了球王社群系統使用的資料儲存結構，包含文章、hashtag、按讚及檢舉等主要資料表。文章與相關元數據主要存放於 Meilisearch 的 community index，點讚記錄獨立存放在 like index，檢舉資料則使用 Cassandra 資料庫的 report table。對於 AI 開發者，可以快速掌握社群內容的資料模型、索引設計及關聯關係，便於設計查詢、寫入與資料同步邏輯。

**關鍵設計決策**：
- 選擇 Meilisearch 作為文章、hashtag 及點讚的儲存，以支援高效全文搜尋與多條件過濾（如按遊戲種類、聯盟、會員等）
- 將按讚總數與按讚明細分離，文章 JSON 僅保留總數，細部記錄放在獨立 index，既可減少文章資料量，又保留查詢明細的彈性

**注意事項**：
- ⚠️ 文件最後更新時間為 2026-04-24，明顯晚於當前時間，可能是筆誤或測試資料，實際結構可能已變更，使用前需人工確認版本
- ⚠️ like index 的 content_type 欄位範例只列出 'comment'，但說明含文章按讚，實際可取值需從程式碼確認

---

## 歷史決策類

### 球王社群API

> Confluence 頁面 ID：79470699
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=79470699)
> 摘要檔：[processed/79470699-summary.md](../../confluence/processed/79470699-summary.md)
> Confluence 最後更新：2026-05-22
> 摘要最後同步：2026-05-26

**決策背景**：
此文件详细定义了球王社群系统的所有 RESTful API 端点，涵盖文章/回文的 CRUD、图片上传、Hashtag 管理、点赞、检举、文章置顶、热门文章获取、内容隐藏/解除隐藏以及统计报表等功能。

**決策結論**：
提供了完整的接口契约和数据结构参考，为 AI 开发 communityservice 提供了标准化的接口设计。

**影響**：
接口定义直接影响到前后端的开发规范和测试用例，确保了社群功能的一致性和扩展性。

---

## 操作手冊類

### ForumService WordPress 檔案位置

> Confluence 頁面 ID：20873349
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/pages/viewpage.action?pageId=20873349)
> 摘要檔：[processed/20873349-summary.md](../../confluence/processed/20873349-summary.md)
> Confluence 最後更新：2021-06-17
> 摘要最後同步：2026-05-26

**摘要**：
本文件提供 ForumService 在 WordPress 中的各功能頁面和模板的檔案位置圖解，涵蓋導航、主頁、訂閱、麵包屑、動態瀏覽、阻擋外部訪問、登入註冊、個人檔案設定、訊息等功能。對 AI 開發的幫助在於了解論壇前端的檔案結構，利於進行論壇介面客製化或維護。

**注意事項**：
- ⚠️ 文件僅包含截圖，缺乏文字說明，可能不易準確解析
- ⚠️ 截圖日期為 2021 年，可能已過時，目前的 WordPress 論壇結構可能已有變更