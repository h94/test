# ProductService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/productservice.git

## 職責

負責管理商城商品與活動商品，包含商品資料維護、兌換紀錄、庫存記錄，以及活動提領紀錄的查詢與寫入。

## 技術棧

- 框架：ASP.NET Core 8（.NET 8.0）
- 資料庫：Cassandra（主要儲存）、Redis（快取）
- 驗證：ECCore 3.0.2 內建機制
- 其他套件：PaymentModels 3.0.1（支付相關模型）、Microsoft.VisualStudio.Azure.Containers.Tools.Targets（Docker 支援）

## 資料庫重要 Table

| Table 名稱 | 用途 | 重要欄位 |
|-----------|------|---------|
| `products_store` | 商城商品 | pclass, pid, pnames (MAP), originalprice, price, status, popular, description (MAP), image_path (MAP), psource, lastup_time |
| `product_store_redeem_logs` | 商城商品兌換紀錄 | pclass, pid, addtime, account, id, cname, cheadshot, address, cmemo, status, description, deliverytime, updatetime |
| `product_store_stock_logs` | 商城商品庫存紀錄 | pclass, pid, addtime, id, quantity, updatetime |
| `products_activity` | 活動商品 | site, activityevent, id, names (MAP), price, quantity, status, updatetime |
| `products_activity_redeem_logs` | 活動商品兌換紀錄 | site, activityevent, account, id, pid, addtime, status, updatetime |
| `withdrawlogs_activity` | 活動提領紀錄 | site, activityevent, account, cid, status, contactnumber, updatetime |

## 對外 API 重點

### 商城商品
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/store/products` | 新增商城商品 | ✅ |
| GET | `/api/v1/store/products/{pclass}/{pid}` | 取得商城某種類單一商品 | ✅ |
| GET | `/api/v1/store/products/{pclass}` | 取得商城某種類全部商品 | ✅ |
| POST | `/api/v1/store/productredeemlogs` | 建立商品兌換紀錄 | ✅ |
| POST | `/api/v1/store/productstocklogs` | 新增商品庫存紀錄 | ✅ |

### 活動商品
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/activity/products` | 新增活動商品 | ✅ |
| GET | `/api/v1/activity/products/{site}/{activityEvent}` | 取得站台活動商品 | ✅ |
| POST | `/api/v1/activity/productredeemlogs` | 新增活動商品兌換紀錄 | ✅ |
| POST | `/api/v1/activity/withdrawlogs` | 新增活動提領紀錄 | ✅ |

### 系統
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/autocreatetable` | 自動建表 | ✅ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| Cassandra | 儲存商品、兌換、庫存、活動資料 |
| Redis | 商品快取（HashCache） |
| PaymentModels | 支付相關資料模型共用 |

## 常見使用場景

1. **使用者在商城兌換商品**
   - 觸發：使用者點擊兌換後由前端觸發
   - 流程：查 `GET /api/v1/store/products/{pclass}/{pid}` 確認商品狀態 → 呼叫 `POST /api/v1/store/productredeemlogs` 建立兌換紀錄 → 更新 `POST /api/v1/store/productstocklogs` 庫存

2. **後台新增或上架商品**
   - 觸發：管理人員在後台建立新商品
   - 流程：呼叫 `POST /api/v1/store/products` 新增商品資料，含多語言名稱與圖片路徑

3. **活動期間商品兌換**
   - 觸發：使用者參與活動並兌換活動商品
   - 流程：`POST /api/v1/activity/productredeemlogs` 記錄兌換 → `POST /api/v1/activity/withdrawlogs` 建立提領申請

## AI 判斷關鍵字

商品, 商城, 兌換, 庫存, 活動商品, 提領, 點數兌換, product, store, redeem, stock, activity, 商品管理
