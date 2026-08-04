# CommunityService WebAPI

- **Git Repository**：https://git.zbdigital.net/CrawlerAgent/communityservice.git

## 職責
負責管理平台的**社群互動**功能，包含體育賽事社群文章（發文、留言、按讚、HashTag）及新彩票討論看板（論壇、主題、留言）。使用 **Python Flask** 框架，以 MeiliSearch 作為主要查詢引擎，Cassandra 作為部分持久化儲存（論壇看板、檢舉記錄）。

## 技術棧
- 框架：Python 3.9 + Flask 3.1.0 + flask-smorest（OpenAPI 3.0）
- 資料庫：Cassandra（Keyspace: `community`，僅用於 `newlottery_forums`、`report_table`）
  （⚠️ 需人工確認：現有 README 及部分場景文件提及 Cassandra `articles` / `comments` 表，但程式碼證據顯示所有文章與留言操作均透過 MeiliSearch 的 `community` 索引進行，並未操作 Cassandra 的對應表。`community` keyspace 目前僅有 `newlottery_forums` 一張表，推測 `articles` 與 `comments` 已移轉或從未設計於 Cassandra，此處修正為與程式碼一致的描述，待資深工程師確認歷史持久化策略）
- 搜尋索引：MeiliSearch（`community`、`hashtag`、`like`、`newlottery_subjects`、`newlottery_comments`、`newlottery_likes`）
- 圖片儲存：NAS（透過 SFTP，路徑依配置）
- 日誌：Kafka（TCZB Logger）
- 其他套件：cassandra-driver 3.29.3、meilisearch 0.33.1、pydantic 2.10.6、kazoo（Zookeeper）、pysftp 0.2.9、shortuuid 1.0.13、bcrypt 4.2.1 等

## 儲存層重要資源

| 儲存層 | Table / Index | 用途 |
|--------|--------------|------|
| MeiliSearch | `community` | 體育社群文章主體（含內嵌留言、按讚統計、競猜預測、HashTag 關聯），支援全文搜尋與條件篩選（**主要查詢與儲存引擎**） |
| MeiliSearch | `hashtag` | HashTag 關聯索引，依 hashtag_type 篩選 |
| MeiliSearch | `like` | 按讚記錄（體育社群共用），依 content_id、user 篩選；同時支援文章與留言按讚 |
| Cassandra | `community.newlottery_forums` | 新彩票論壇看板 |
| Cassandra | `community.report_table` | 檢舉記錄，依 `report_id` 查詢 |
| MeiliSearch | `newlottery_subjects` | 新彩票主題索引，依論壇、帳號、時間排序 |
| MeiliSearch | `newlottery_comments` | 新彩票留言索引，依主題、帳號、時間排序 |
| MeiliSearch | `newlottery_likes` | 新彩票按讚記錄索引，依 subject_id, comment_id, account 篩選 |

> **⚠️ 需人工確認**：原 README 列出 Cassandra `community.articles` 與 `community.comments` 表，但程式碼中未見任何對這些表的讀寫操作。文章與留言的增刪改查全數走 MeiliSearch。若 Cassandra 歷史上設計過這些表但未實作，應從文件中移除；若仍有其他服務使用，需補充說明。

## 對外 API 重點

### 體育社群文章
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/community/{game_type}/articles` | 發布社群文章（支援圖片上傳） | ✅ |
| GET | `/api/community/{game_type}/articles` | 查詢文章列表（分頁/篩選，支援 `index`、`page`、`show_hidden`、`leagues`、`articTopics`、`memberShips`） | ✅ |
| GET | `/api/community/{game_type}/hot_articles` | 查詢熱門文章（根據公式計算並由後台線程每小時更新） | ✅ |
| GET | `/api/community/{game_type}/articles/{article_id}` | 查詢單篇文章 | ✅ |
| PUT | `/api/community/{game_type}/edit_articles` | 編輯文章內容 | ✅ |
| PUT | `/api/community/{game_type}/edit_predict` | 編輯文章競猜內容 | ✅ |
| DELETE | `/api/community/{game_type}/articles/{id}` | 刪除文章 | ✅ |
| PUT | `/api/community/{gameType}/top_articles` | 設定置頂文章 | ✅ |
| GET | `/api/community/{gameType}/get_top_articles` | 查詢置頂文章 | ✅ |
| GET | `/api/community/backend/{game_type}/articles-bytime` | 後台查詢文章（依時間） | ✅ |
| GET | `/api/community/backend/user/{user}/articles` | 後台查詢特定使用者文章（依帳號） | ✅ |

### 體育社群留言
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/community/{game_type}/articles/{id}/comments` | 發布留言（支援圖片上傳） | ✅ |
| GET | `/api/community/{game_type}/articles/{id}/comments` | 查詢文章留言（分頁，支援 `show_hidden`） | ✅ |
| GET | `/api/community/{game_type}/articles/{article_id}/comments/{comment_id}` | 查詢單則留言 | ✅ |
| PUT | `/api/community/{game_type}/edit_comments` | 編輯留言 | ✅ |
| DELETE | `/api/community/{game_type}/articles/{article_id}/comments/{comment_id}` | 刪除留言 | ✅ |

### 按讚（體育社群）
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/community/{game_type}/articles/{article_id}/likes` | 文章按讚（支援 emoji） | ✅ |
| POST | `/api/community/{game_type}/articles/{article_id}/comments/{comment_id}/likes` | 留言按讚（支援 emoji） | ✅ |
| GET | `/api/community/{game_type}/articles/{id}/likes` | 查詢文章按讚（根據程式碼 `LikeService.get_like_detail` 支援此功能） | ✅ |
| GET | `/api/community/{game_type}/comments/{id}/likes` | 查詢留言按讚（根據程式碼 `LikeService.get_like_detail` 支援此功能，但 OpenAPI 未獨立定義此路由，需人工確認路由形式） | ✅ |

> **⚠️ 已移除**：原 README 列出 `PUT /api/community/{game_type}/articles/{article_id}/top`，但程式碼中不存在此路由。置頂文章是透過 `PUT /api/community/{gameType}/top_articles` 批次設定，非單篇操作。

### HashTag 管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/community/{game_type}/hashtags/update` | 建立/更新 HashTag | ✅ |
| GET | `/api/community/{game_type}/hashtags` | 查詢 HashTag 列表 | ✅ |
| DELETE | `/api/community/{game_type}/hashtags/{hashtag_type}/{hashtag_id}` | 刪除 HashTag | ✅ |

### 禁言管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| PUT | `/api/community/mute` | 批次隱藏/取消隱藏特定用戶內容（透過設定文章/留言的 `hidden` 欄位） | ✅ |
| PUT | `/api/community/mute_single` | 單一帳號隱藏/取消隱藏（操作方式同上） | ✅ |

### 檢舉管理
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/community/backend/report` | 建立檢舉記錄 | ✅ |
| GET | `/api/community/backend/report/{report_id}` | 查詢檢舉記錄 | ✅ |
| PUT | `/api/community/backend/report/{report_id}` | 更新檢舉狀態 | ✅ |

### 後台統計
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/community/backend/statistics/user/{user}` | 會員統計總計（發文、回文、按讚、被按讚數） | ✅ |
| GET | `/api/community/backend/statistics/user/{user}/detail` | 會員統計細項（文章/回文/按讚細項） | ✅ |
| GET | `/api/community/backend/statistics/article` | 看板統計（發文、回文、按讚數） | ✅ |
| GET | `/api/community/backend/statistics/article/detail` | 看板統計細項（文章及回文明細） | ✅ |

### 新彩票論壇
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/newlottery/forums` | 查詢所有論壇看板 | ✅ |
| POST | `/api/newlottery/forums` | 建立論壇看板 | ✅ |
| PUT | `/api/newlottery/forums/{forum_id}` | 更新論壇看板 | ✅ |
| DELETE | `/api/newlottery/forums/{forum_id}` | 刪除論壇看板 | ✅ |
| GET | `/api/newlottery/forums/{forum_id}/subjects` | 查詢論壇主題列表（分頁） | ✅ |
| POST | `/api/newlottery/forums/{forum_id}/subjects` | 發布論壇主題 | ✅ |
| GET | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}` | 查詢單一主題 | ✅ |
| PUT | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}` | 編輯主題內容 | ✅ |
| PUT | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}/status` | 切換主題狀態 | ✅ |
| DELETE | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}` | 刪除主題 | ✅ |
| GET | `/api/newlottery/subjects/{subject_id}/comments` | 查詢主題留言列表 | ✅ |
| POST | `/api/newlottery/subjects/{subject_id}/comments` | 發布主題留言 | ✅ |
| GET | `/api/newlottery/subjects/{subject_id}/comments/{comment_id}` | 查詢單一留言 | ✅ |
| PUT | `/api/newlottery/subjects/{subject_id}/comments/{comment_id}` | 編輯留言內容 | ✅ |
| PUT | `/api/newlottery/subjects/{subject_id}/comments/{comment_id}/status` | 切換留言狀態 | ✅ |
| DELETE | `/api/newlottery/subjects/{subject_id}/comments/{comment_id}` | 刪除留言 | ✅ |

### 新彩票按讚
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}/likes` | 主題按讚 | ✅ |
| DELETE | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}/likes` | 取消主題按讚 | ✅ |
| POST | `/api/newlottery/subjects/{subject_id}/comments/{comment_id}/likes` | 留言按讚 | ✅ |
| DELETE | `/api/newlottery/subjects/{subject_id}/comments/{comment_id}/likes` | 取消留言按讚 | ✅ |
| GET | `/api/newlottery/forums/{forum_id}/subjects/{subject_id}/likes` | 查詢主題按讚 | ✅ |
| GET | `/api/newlottery/subjects/{subject_id}/comments/{comment_id}/likes` | 查詢留言按讚 | ✅ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| MeiliSearch | 社群文章 / HashTag / 按讚 / 新彩票主題 / 新彩票留言 / 新彩票按讚全文搜尋與篩選 |
| NAS（SFTP） | 社群圖片儲存（路徑由 `service_config` 定義，`image_nas_folder` 和 `image_save_folder`） |
| Cassandra | 論壇看板 (`community.newlottery_forums`)、檢舉記錄 (`community.report_table`) |
| `mq`（Kafka） | 服務日誌傳送（`send_msg` 於程式中用於記錄 Info/Error/Trace 層級訊息） |
| auth / member service | 使用者 authkey 驗證（communityservice 不自行處理登入）；狀態檢查（`gameusers.status = 1`） |

## 常見使用場景

1. **會員發布賽事競猜文章**
   - 觸發：前台會員在社群頁面發文
   - 流程：POST `/api/community/{game_type}/articles` → 驗證 authkey 及會員狀態 → 可選上傳圖片至 SFTP → 寫入 MeiliSearch `community` 索引（文章與內嵌留言皆存於此）

2. **前台查詢社群文章列表**
   - 觸發：使用者瀏覽社群頁面
   - 流程：GET `/api/community/{game_type}/articles` → MeiliSearch 依 game_type / 聯賽 / 熱門分數篩選排序，預設每頁 20 篇

3. **後台刪除違規文章**
   - 觸發：客服人員處理檢舉
   - 流程：POST `/api/community/backend/report` 建立檢舉（寫入 Cassandra `report_table`） → 審核後 DELETE 文章（從 MeiliSearch 刪除，並異步清理 SFTP 圖片） → PUT 更新檢舉狀態

4. **後台設定 HashTag**
   - 觸發：後台管理員為聯賽設定 HashTag
   - 流程：POST `/api/community/{game_type}/hashtags/update` → 更新 MeiliSearch `hashtag` 索引

5. **新彩票用戶在論壇討論**
   - 觸發：新彩票前台使用者進入討論看板
   - 流程：GET `/api/newlottery/forums` 從 Cassandra 查詢看板 → GET `/api/newlottery/forums/{forum_id}/subjects` 從 MeiliSearch 取得主題列表 → POST `/api/newlottery/subjects/{subject_id}/comments` 發布留言至 MeiliSearch `newlottery_comments`

## 禁言與隱藏機制

本服務的禁言功能透過修改 MeiliSearch 社群文件（文章或留言）的 `hidden` 屬性來實現，並無獨立的禁言資料表。`PUT /api/community/mute` 與 `PUT /api/community/mute_single` 可依條件（如 `user`、`article_id`、`comment_id`、`game_type`、時間範圍）批次或單筆設定 `hidden`，達到隱藏內容的效果；解除禁言則將 `hidden` 設回 `false`。同時，`hot` 和 `hot_score` 會設為 `False` 及 `0`。此操作記錄於 Trace 日誌。

> **實作細節（根據 `mute_services.py`）**：禁言 API 接收 `action` 參數（`mute` 或 `unmute`），支援三種隱藏範圍：
> 1. **指定文章**（`article_id` 傳入）：隱藏整篇文章。
> 2. **指定留言**（同時傳入 `article_id` 與 `comment_id`）：隱藏單一留言，並更新文章的 `commentCount`。
> 3. **指定使用者與時間範圍**（傳入 `user`、`start`、`end`、`game_type`）：隱藏該使用者在此時間內的所有文章與留言。
>
> 所有文章與留言的 `hidden` 狀態全數儲存於 MeiliSearch `community` 索引內，無 Cassandra 對應表。

## AI 判斷關鍵字

社群, 文章, 發文, 留言, 按讚, HashTag, 置頂, 隱藏, 檢舉, 熱門文章, 新彩票論壇, 看板, 主題, 社群互動, 遊戲社群, Flask, MeiliSearch