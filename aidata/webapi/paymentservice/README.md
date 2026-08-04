# PaymentService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/paymentservice.git

## 職責
負責管理平台所有金流業務，涵蓋**體育訂閱方案（Sport）**、**活動商品兌換**、**交易訂單**、**月度/年度報表**、**提現記錄**，以及**新彩票儲值與佣金**。提供後台管理與前台金流操作所需的完整支付 API。

## 技術棧
- 框架：ASP.NET Core (.NET 8.0)
- 資料庫：Cassandra（Keyspace: `payment`）、Redis（快取支付方案與訂閱計畫）
- 驗證：ECFramework.ECService（內部統一驗證框架）
- 配置中心：Zookeeper
- 日誌：Kafka + Cassandra
- 其他套件：ECCore 3.0.3、PaymentModels 3.0.1

## 資料庫重要 Table

| Table 名稱（Cassandra） | 用途 | 重要欄位 |
|----------------------|------|---------|
| payment.sport_pay_methods | 體育支付方式設定 | pay_type, mode, enabled |
| payment.sport_sub_plans | 體育訂閱方案 | id, name, price, duration, pay_methods |
| payment.sport_transactions | 體育交易訂單 | year, date_time, account, id, amount, status |
| payment.sport_reports | 月度收益報表 | year, month, total_amount |
| payment.sport_share_reports | 推薦分潤報表 | account, year, month, game_type, league |
| payment.sport_withdraw_logs | 提現記錄 | account, date_time, amount, status |
| payment.activity_products | 活動商品 | site, activity_event, id, name, price |
| payment.activity_redeem_logs | 活動兌換記錄 | site, activity_event, account, id, status |
| payment.newlottery_transactions | 新彩票交易訂單 | year, date_time, account, id |
| payment.newlottery_recharge_plans | 新彩票儲值方案 | id, name, amount |

## 對外 API 重點

### 體育支付方式
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/paymethods` | 建立支付方式 | ✅ |
| GET | `/api/v1/sport/paymethods` | 查詢所有支付方式 | ✅ |
| GET | `/api/v1/sport/paymethods/{payType}/{mode}` | 查詢單一支付方式 | ✅ |
| PUT | `/api/v1/sport/paymethods/{payType}/{mode}` | 更新支付方式 | ✅ |

### 體育訂閱方案
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/subplans` | 建立訂閱方案 | ✅ |
| GET | `/api/v1/sport/subplans` | 查詢所有訂閱方案 | ✅ |
| GET | `/api/v1/sport/subplans/{id}` | 查詢單一訂閱方案 | ✅ |
| PUT | `/api/v1/sport/subplans/{id}` | 更新訂閱方案 | ✅ |
| PUT | `/api/v1/sport/subplans/methods/{payType}/{mode}/remove` | 移除方案支付方式 | ✅ |

### 體育交易訂單
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/transactions` | 建立交易訂單 | ✅ |
| GET | `/api/v1/sport/transactions` | 查詢交易訂單（日期範圍） | ✅ |
| GET | `/api/v1/sport/transactions/{year}/{dateTime}/{account}/{id}` | 查詢單筆訂單 | ✅ |
| PUT | `/api/v1/sport/transactions/{year}/{dateTime}/{account}/{id}` | 更新訂單狀態 | ✅ |

### 體育報表
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/reports` | 建立月度報表 | ✅ |
| POST | `/api/v1/sport/sharereports` | 建立分潤報表 | ✅ |
| POST | `/api/v1/sport/recommendreports` | 建立推薦報表 | ✅ |
| POST | `/api/v1/sport/recommendsharereports` | 建立推薦分潤報表 | ✅ |
| GET | `/api/v1/sport/reports/{year}` | 查詢年度報表 | ✅ |
| GET | `/api/v1/sport/reports/{year}/{month}` | 查詢月度報表 | ✅ |
| GET | `/api/v1/sport/reportlist/{year}/{month}` | 查詢月份所有分潤報表 | ✅ |
| GET | `/api/v1/sport/sharereports/{account}` | 查詢帳號分潤報表 | ✅ |
| GET | `/api/v1/sport/recommendreports/{year}` | 查詢年度推薦報表 | ✅ |
| PUT | `/api/v1/sport/reports/{year}/{month}` | 更新月度報表 | ✅ |
| PUT | `/api/v1/sport/sharereports/{account}/{year}/{month}/{gameType}/{league}` | 更新分潤報表 | ✅ |

### 體育提現
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/sport/withdrawlogs` | 建立提現記錄 | ✅ |
| GET | `/api/v1/sport/withdrawlogs` | 查詢提現記錄（日期範圍） | ✅ |
| GET | `/api/v1/sport/withdrawlogs/{account}` | 查詢帳號提現記錄 | ✅ |
| PUT | `/api/v1/sport/withdrawlogs/{account}/{dateTime}/result` | 更新提現結果 | ✅ |

### 活動商品與兌換
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/activity/products` | 建立活動商品 | ✅ |
| GET | `/api/v1/activity/products/{site}/{activityEvent}` | 查詢活動商品 | ✅ |
| PUT | `/api/v1/activity/products` | 更新活動商品 | ✅ |
| POST | `/api/v1/activity/productredeemlogs` | 建立兌換記錄 | ✅ |
| GET | `/api/v1/activity/productredeemlogs/{site}/{activityEvent}` | 查詢兌換記錄 | ✅ |
| PUT | `/api/v1/activity/productredeemlogs/{site}/{activityEvent}/{account}/{id}/status` | 更新兌換狀態 | ✅ |
| POST | `/api/v1/activity/withdrawlogs` | 建立活動提現記錄 | ✅ |

### 新彩票金流
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/newlottery/rechargeplans` | 建立儲值方案 | ✅ |
| GET | `/api/v1/newlottery/rechargeplans` | 查詢儲值方案 | ✅ |
| PUT | `/api/v1/newlottery/rechargeplans/{id}` | 更新儲值方案 | ✅ |
| POST | `/api/v1/newlottery/transactions` | 建立新彩票交易訂單 | ✅ |
| GET | `/api/v1/newlottery/transactions` | 查詢新彩票交易訂單 | ✅ |
| PUT | `/api/v1/newlottery/transactions/{year}/{dateTime}/{account}/{id}` | 更新新彩票訂單 | ✅ |
| POST | `/api/v1/newlottery/commissions/betpool` | 建立獎池佣金 | ✅ |
| GET | `/api/v1/newlottery/commissions/betpool/{betpool}` | 查詢獎池佣金 | ✅ |

### 系統工具
| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/system/autocreatetable` | 自動建立 Cassandra Table | ✅ |
| DELETE | `/api/v1/system/sport/shakehandlogs` | 清除握手日誌 | ✅ |
| GET | `/api/heart` | Health Check | ❌ |
| GET | `/api/version` | 查詢版本號 | ❌ |

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| `memberservice` | 驗證會員身份（訂閱前確認帳號狀態） |
| `mq`（Message Queue） | 發送付款成功通知信 |

## 常見使用場景

1. **會員訂閱體育方案**
   - 觸發：前台會員選擇訂閱方案並完成付款
   - 流程：GET `/api/v1/sport/subplans` 查詢方案 → POST `/api/v1/sport/transactions` 建立訂單 → PUT 更新訂單狀態

2. **後台建立月度收益報表**
   - 觸發：每月定時排程觸發（由 pricebackendservice 呼叫）
   - 流程：POST `/api/v1/sport/reports` → POST `/api/v1/sport/sharereports` 建立分潤報表

3. **活動兌換獎品**
   - 觸發：前台會員在活動頁面兌換商品
   - 流程：GET `/api/v1/activity/products/{site}/{activityEvent}` 查詢商品 → POST `/api/v1/activity/productredeemlogs` 建立兌換記錄 → PUT 更新兌換狀態

4. **新彩票會員儲值**
   - 觸發：新彩票前台使用者選擇儲值方案
   - 流程：GET `/api/v1/newlottery/rechargeplans` 查詢方案 → POST `/api/v1/newlottery/transactions` 建立交易 → 呼叫 memberservice 更新彩幣錢包

5. **會員申請提現**
   - 觸發：前台會員提交提現申請
   - 流程：POST `/api/v1/sport/withdrawlogs` 建立提現記錄 → 後台審核 → PUT `/api/v1/sport/withdrawlogs/{account}/{dateTime}/result` 更新結果

## AI 判斷關鍵字

支付, 金流, 訂閱, 方案, 交易, 訂單, 報表, 分潤, 提現, 活動兌換, 儲值, 佣金, 體育付款, 新彩票金流, ECPay, 月度報表, 年度報表
