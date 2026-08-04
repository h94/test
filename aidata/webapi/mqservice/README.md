# MQService WebAPI

- **Git Repository**：https://git.zbdigital.net/biz/mqservice.git

## 職責

負責統一發送各類型訊息通知，包含 Kafka、RocketChat、Telegram、Email（Gmail / Zoho）、SMS（台灣簡訊）及 Prometheus 告警，作為全平台的訊息中介服務。

## 技術棧

- 框架：ASP.NET Core 8（.NET 8.0）
- 資料庫：無（純訊息轉發，無持久化）  
  > **注意**：雖然服務本身無專屬業務資料庫，但會讀取 `stock` 資料庫的 `users`、`favoriterule`、`favoritestock` 等表以進行規則判斷，並將發送記錄寫入 `stock.messagelog` 表。
- 驗證：ECCore 3.0.2 內建機制
- 其他套件：MailKit 2.9.0（Email 發送）、Telegram.Bot 15.7.1（Telegram 機器人）

## 資料庫重要 Table

此服務無自有資料庫 Table，但操作下列 `stock` 資料庫的 table：

| Table | 操作類型 | 用途 |
|-------|---------|------|
| `stock.users` | 讀取 | 檢查使用者啟用狀態、訂閱到期日，判斷是否觸發通知 |
| `stock.favoriterule` | 讀取 | 讀取使用者自訂通知規則，包含 NeedSend、FirstMatch、行業/市場篩選條件 |
| `stock.favoritestock` | 讀取 | 取得使用者自選股票清單，用於規則匹配 |
| `stock.rules` | 讀取 | 取得系統觸發規則清單（僅讀取 Enabled=1 者） |
| `stock.messagelog` | 寫入 | 記錄所有訊息發送日誌（append-only） |

## 對外 API 重點

### 系統

| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| GET | `/api/heart` | 服務存活檢查 | ❌ |
| GET | `/api/version` | 服務版本與建置資訊 | ❌ |

### 訊息發送

| Method | 路由 | 說明 | 需要驗證 |
|--------|------|------|---------|
| POST | `/api/v1/kafka/message` | 發送 Kafka 訊息 | ✅ |
| POST | `/api/v1/log/message` | 寫入應用程式日誌（Kafka Logger） | ✅ |
| POST | `/api/v1/rocket/message` | 發送 RocketMQ 訊息（一般 Webhook） | ✅ |
| POST | `/api/v1/rocket/message/inplayz` | 發送 RocketMQ 訊息（InPlayZ 專用 Webhook） | ✅ |
| POST | `/api/v1/telegram/message` | 發送 Telegram 告警訊息（支援 Program/IT 聊天室） | ✅ |
| POST | `/api/v1/telegram/message/stock` | 發送 Telegram 股票相關訊息至指定使用者或群組 | ✅ |
| POST | `/api/v1/telegram/message/bank` | 發送 Telegram 銀行相關訊息（SBIBankAlert Bot） | ✅ |
| POST | `/api/v1/telegram/message/inplayz` | 發送 Telegram InPlayZ 告警（InPlayZAlert Bot） | ✅ |
| POST | `/api/v1/prometheus/message` | 接收 Prometheus Alertmanager Webhook，轉發至 Telegram + RocketMQ | ✅ |
| POST | `/api/v1/mail/message` | 發送一般 Email（Gmail SMTP） | ✅ |
| POST | `/api/v1/mail/inplayz/message` | 發送 InPlayZ 品牌 Email（Zoho SMTP） | ✅ |
| POST | `/api/v1/sms/twsms/message` | 發送 SMS（台灣簡訊 TwSMS） | ✅ |

> **需人工確認**：各端點使用的驗證機制細節（如 ECCore 的 `[RQ.Authorized]` 屬性配置方式）需與實際程式碼核對。

## 服務相依

| 相依服務 | 用途 |
|---------|------|
| Kafka（192.168.55.85~87） | 訊息佇列寫入 |
| RocketMQ（192.168.9.231） | 即時通訊告警頻道（一般 / InPlayZ Webhook） |
| Telegram Bot | 告警、股票、銀行、InPlayZ 通知（支援多 Bot 配置） |
| Gmail SMTP（smtp.gmail.com:587） | 一般 Email 發送 |
| Zoho SMTP（smtp.zoho.com:587） | InPlayZ 品牌 Email 發送 |
| TwSMS API | 台灣手機簡訊發送 |
| Zookeeper（192.168.1.246:2181） | 服務配置中心 |
| Stock MySQL（192.168.9.232:3306） | 讀取使用者/規則資料，寫入訊息發送日誌 |

## 常見使用場景

1. **系統異常告警**
   - 觸發：任何後端服務發生例外或閾值超標
   - 流程：呼叫 `POST /api/v1/telegram/message` 或 `POST /api/v1/rocket/message` 將告警推送到指定群組

2. **使用者 Email 通知**
   - 觸發：使用者完成註冊、交易、提領等操作需寄送通知信
   - 流程：後端服務呼叫 `POST /api/v1/mail/message`（一般） 或 `POST /api/v1/mail/inplayz/message`（InPlayZ 品牌）

3. **SMS 簡訊驗證**
   - 觸發：使用者需要手機驗證碼
   - 流程：呼叫 `POST /api/v1/sms/twsms/message` 透過台灣簡訊發送驗證碼

4. **Kafka 事件串流**
   - 觸發：需要跨服務異步通知的業務事件
   - 流程：呼叫 `POST /api/v1/kafka/message` 寫入指定 Topic

## AI 判斷關鍵字

訊息, 通知, 告警, Email, 簡訊, SMS, Telegram, RocketChat, RocketMQ, Kafka, 發信, 推播, MQ, 訊息佇列, alert, notification, Prometheus, Webhook