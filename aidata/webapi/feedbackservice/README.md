# FeedbackService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/feedbackservice.git

## 職責

負責管理運動站台與股票站台的使用者反饋（Topic / Question / Message），以及商業合作訊息的收發與回覆。

## 技術棧

- 框架：ASP.NET Core 6（.NET 6.0）
- 資料庫：
  - **Cassandra**（keyspace: `feedback`）：主要儲存反饋、主題、問題及商業訊息
  - **MySQL**（database: `stock`）：讀取股票站台使用者資訊與其他唯讀資料；特定內部任務寫入 `messagelog`
- 驗證：ECCore 2.0.7 內建機制，及外部 authservice 提供身分驗證
- 其他套件：SixLabors.ImageSharp 3.1.12（反饋圖片上傳）
- 郵件與檔案：委由 emailservice 及 fileservice 處理

## 資料庫重要 Table

| Table 名稱 | 用途 | 重要欄位 |
|-----------|------|---------|
| `topics_sport` | 運動站台反饋種類 | id, enabled, name (MAP<text,text>), sort |
| `questions_sport` | 運動站台反饋問題 | id, tid, question (MAP<text,text>), answer (MAP<text,text>), enabled, sort |
| `feedbacks_sport` | 運動站台反饋訊息 | tid, datetime, account, id, email, problem (LIST<text>), respcontent (LIST<text>), status, updatetime, imgpath (LIST<text>), adminimgpath (LIST<text>) |
| `topics_stock` | 股票站台反饋種類 | id, enabled, name (text), sort |
| `questions_stock` | 股票站台反饋問題 | id, tid, question (text), answer (text), enabled, sort |
| `feedbacks_stock` | 股票站台反饋訊息 | id, status, datetime, tid, account, email, problem (LIST<text>), respcontent (LIST<text>), updatetime |
| `businessmessages` | 商業合作訊息 | site, datetime, id, sendermail, sendcontent, respcontent, status, updatetime |

*※「name」欄位在運動站台為多語言 map；股票站台為純文字。*

## 對外 API 重點

### 運動站台反饋
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/feedback/topics` | 新增反饋種類 | ✅ |
| GET | `/api/v1/sport/feedback/topics` | 取得全部反饋種類 | ✅ |
| POST | `/api/v1/sport/feedback/questions` | 新增反饋問題 | ✅ |
| GET | `/api/v1/sport/feedback/questions` | 取得全部反饋問題 | ✅ |
| POST | `/api/v1/sport/feedback/messages/{tid}` | 新增反饋訊息 | ✅ |
| GET | `/api/v1/sport/feedback/messages` | 依時間、帳號查詢反饋訊息列表 | ✅ |
| GET | `/api/v1/sport/feedback/messages/{tid}/{dateTime}/{account}/{id}` | 取得單筆反饋訊息 | ✅ |
| PUT | `/api/v1/sport/feedback/topics/{id}` | 更新反饋種類 | ✅ |
| PUT | `/api/v1/sport/feedback/questions/{id}` | 更新反饋問題 | ✅ |
| PUT | `/api/v1/sport/feedback/messages/{tid}/{dateTime}/{account}/{id}/respcontent` | 更新單則客服回覆 | ✅ |
| PUT | `/api/v1/sport/feedback/messages/{tid}/{dateTime}/{account}/{id}/respcontents` | 更新全部客服回覆 | ✅ |
| PUT | `/api/v1/sport/feedback/messages/{tid}/{dateTime}/{account}/{id}/status` | 更新反饋狀態 | ✅ |

### 股票站台反饋
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/stock/topics` | 新增股票反饋種類 | ✅ |
| GET | `/api/v1/stock/topics` | 取得股票反饋種類 | ✅ |
| POST | `/api/v1/stock/questions` | 新增股票反饋問題 | ✅ |
| GET | `/api/v1/stock/questions` | 取得股票反饋問題 | ✅ |
| POST | `/api/v1/stock/messages` | 新增股票反饋訊息 | ✅ |
| GET | `/api/v1/stock/messages` | 分頁查詢反饋訊息（狀態、帳號、tid 等） | ✅ |
| GET | `/api/v1/stock/messages/users/{account}` | 取得指定會員所有反饋 | ✅ |
| GET | `/api/v1/stock/messages/users/{account}/{id}` | 取得指定會員單筆反饋 | ✅ |
| PUT | `/api/v1/stock/topics/{id}` | 更新股票反饋種類 | ✅ |
| PUT | `/api/v1/stock/questions/{id}` | 更新股票反饋問題 | ✅ |
| PUT | `/api/v1/stock/messages/users/{account}/{id}` | 會員更新自己的反饋 | ✅ |
| PUT | `/api/v1/stock/messages/users/{account}/{id}/resp` | 客服回覆指定會員反饋 | ✅ |
| PUT | `/api/v1/stock/messages/resp/{id}` | 客服回覆反饋（不限會員） | ✅ |

### 商業合作
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/business/messages` | 新增商業合作訊息 | ✅ |
| GET | `/api/v1/business/messages/{site}` | 取得站台日期範圍商業合作訊息 | ✅ |
| GET | `/api/v1/business/messages/{site}/{dateTime}/{id}` | 取得某筆商業合作訊息 | ✅ |
| PUT | `/api/v1/business/messages/{site}/{dateTime}/{id}/respcontent` | 更新回覆內容 | ✅ |

### 系統
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/autocreatetable` | 自動建表 | ✅ |
| POST | `/api/v1/system/sport/feedback/upload/image` | 反饋訊息上傳圖檔 | ✅ |
| DELETE | `/api/v1/system/sport/feedback/messages/end` | 移除已結束反饋訊息（xxl-job） | ✅ |
| DELETE | `/api/v1/system/business/messages/reply` | 移除已回覆商業合作訊息（xxl-job） | ✅ |

## 服務相依

| 相依服務/資源 | 用途 |
|---------|------|
| Cassandra (feedback) | 主資料庫，儲存所有反饋、問題、主題、商業訊息 |
| MySQL (stock) | 讀取股票站台使用者資料；由內部任務寫入 messagelog |
| authservice | 用戶認證與授權，服務僅接收已驗證請求 |
| emailservice | 發送回覆通知郵件 |
| fileservice | 反饋圖片上傳與儲存管理 |

## 常見使用場景

1. **使用者送出客服反饋**
   - 觸發：前端使用者在運動站台填寫問題反饋表單並送出
   - 流程：前端呼叫 `POST /api/v1/sport/feedback/messages/{tid}` → 寫入 `feedbacks_sport`

2. **後台管理商業合作詢問**
   - 觸發：有廠商透過網站填寫商業合作意願
   - 流程：呼叫 `POST /api/v1/business/messages` 儲存 → 管理後台 `GET /api/v1/business/messages/{site}` 查詢 → 回覆後透過 `PUT` 更新狀態

3. **xxl-job 定期清理**
   - 觸發：排程任務
   - 流程：呼叫 `DELETE /api/v1/system/sport/feedback/messages/end` 移除已結束反饋，呼叫 `DELETE /api/v1/system/business/messages/reply` 移除已回覆商業訊息

## AI 判斷關鍵字

反饋, 客服, 問題回報, 商業合作, 運動反饋, 股票反饋, 意見回饋, feedback, topic, question, business message