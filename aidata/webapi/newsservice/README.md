# NewsService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/newsservice.git

## 職責

負責管理運動新聞與站台文章，包含多球種新聞的新增、查詢、刪除，以及 AI 生成新聞（ainews）的儲存與查詢。

## 技術棧

- 框架：ASP.NET Core 8（.NET 8.0）
- 資料庫：Cassandra（透過 ECFramework.ECService）
- 驗證：ECCore 3.0.3 內建機制
- 其他套件：Microsoft.VisualStudio.Azure.Containers.Tools.Targets 1.10.8（Docker 支援）

## 資料庫重要 Table

| Table 名稱 | 用途 | 重要欄位 |
|-----------|------|---------|
| `sports_{game}` | 各球種運動新聞（動態建表，依球種命名） | id, date, title, content, link, sourcesite, tag, lang, addtime |
| `ainews` | AI 生成新聞（通用） | gtype, gdate, lid, gid, llmhashkey, status, reanwser, used, articleid |
| `ainews_{site}` | 各站台 AI 新聞（動態） | 同 ainews |

## 對外 API 重點

### 運動新聞
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sports/{gameType}` | 新增運動新聞 | ✅ |
| GET | `/api/v1/sports` | 取得運動新聞（可依 gameType、addTime、lang、tag 過濾） | ✅ |
| DELETE | `/api/v1/sports/{gameType}` | 刪除運動新聞 | ✅ |

### 站台文章
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sportarticles` | 設定運動站台文章 | ✅ |
| GET | `/api/v1/sportarticles` | 取得全部運動站台文章 | ✅ |
| GET | `/api/v1/sportarticles/{id}` | 取得某篇文章 | ✅ |
| DELETE | `/api/v1/sportarticles/{id}` | 刪除某篇文章 | ✅ |

### 系統
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/autocreatetable` | 自動建立資料表 | ✅ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| Cassandra | 儲存新聞與文章資料 |

## 常見使用場景

1. **爬蟲服務寫入新聞**
   - 觸發：爬蟲抓取到新賽事新聞
   - 流程：爬蟲呼叫 `POST /api/v1/sports/{gameType}` 將新聞存入對應球種 Table

2. **前端顯示最新運動新聞**
   - 觸發：使用者進入運動站台新聞頁面
   - 流程：前端呼叫 `GET /api/v1/sports` 加上 gameType / lang / tag 參數取得篩選後新聞列表

3. **AI 新聞產出後儲存**
   - 觸發：LLM 生成新聞摘要或分析文章後需持久化
   - 流程：後端寫入 `ainews` 或 `ainews_{site}` Table，之後由站台查詢並展示

4. **文章後台管理**
   - 觸發：編輯人員在後台新增或更新站台文章
   - 流程：呼叫 `POST /api/v1/sportarticles` 新增，或 `DELETE /api/v1/sportarticles/{id}` 下架

## AI 判斷關鍵字

新聞, 文章, 運動新聞, AI新聞, 球種, 賽事, 新聞爬蟲, news, article, ainews, sports news, 多語言新聞
