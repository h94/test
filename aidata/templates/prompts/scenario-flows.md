你是一位資深系統架構師與維運工程師。

請根據以下資料：

1. README.md
2. dbschema detail.md
3. db-usage 文件
4. API reference / OpenAPI
5. rules / PLAN_SPEC
6. 相關 code evidence（Controller / Service / Provider / SQL / Redis / Kafka）
7. 測試腳本（若存在）

產生「Scenario Flow Document」。

==================================================
【目標】
==================================================

這份文件的目的：

1. 協助新人理解系統實際運行流程
2. 協助 AI 後續產生正確 Plan / Code / Test
3. 避免 AI 與新人誤解 DB / API / Cache / Queue 使用方式
4. 描述「業務流程」，不是單純 API 文件

==================================================
【重要限制】
==================================================

1. 不可憑空猜測
2. 所有重要結論必須有 evidence
3. 若資訊不足，請標記：
   - 「需人工確認」
4. 不要複製整段 code
5. 不要產生過度冗長文件
6. 文件以「場景」為單位
7. 不要描述所有 implementation detail
8. 優先描述：
   - 系統流程
   - DB / Redis / Queue 使用
   - 高風險行為
   - 錯誤情境
   - 驗證規則

==================================================
【請分析】
==================================================

請分析：

1. 入口 API
2. Controller → Service → Provider 流程
3. DB table 使用方式
4. Redis / Cache 使用
5. Queue / Kafka 使用
6. 外部 API 呼叫
7. 權限 / 驗證流程
8. 成功流程
9. 錯誤流程
10. 高風險操作
11. 測試重點
12. 常見錯誤

==================================================
【輸出格式】
==================================================

請輸出 markdown：

# 場景名稱

## 1. 場景目的

簡短描述這個流程的目的。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|

---

## 3. 流程總覽

請用條列描述完整流程。

例如：

1. 接收登入 request
2. 驗證 authKey
3. 查詢 member.users
4. 驗證會員狀態
5. 寫入 Redis session
6. 回傳 token

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|

Layer 例如：
- Controller
- Service
- Provider
- Validator
- Transfer

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|

類型例如：
- DB
- Redis
- Kafka
- Queue

操作例如：
- Read
- Write
- Update
- Delete
- Publish
- Consume

---

## 6. 重要規則

請列出：

- 權限限制
- 欄位限制
- 不可暴露資料
- TTL 規則
- Transaction 規則
- Retry 規則
- 狀態值限制
- 不可修改欄位

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|

例如：

- 帳號不存在
- 權限不足
- Redis 寫入失敗
- DB timeout
- Kafka publish 失敗

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|

類型例如：
- Integration Test
- API Test
- Permission Test
- Flow Test

---

## 9. 高風險區域

請列出：

- 高風險 table
- 高風險 API
- 跨服務資料同步
- Transaction
- Cache consistency
- Queue retry
- Idempotency

---

## 10. 常見錯誤

請列出：

- 新人容易犯錯
- AI 容易誤解
- 常見漏檢查項目
- 常見錯誤流程

---

## 11. Evidence

所有重要結論必須附 evidence：

| 類型 | 來源 |
|---|---|
| API | AuthController.Login |
| DB | member.users |
| Redis | session:{token} |
| Code | AuthService.Login |
| SQL | SELECT * FROM member.users |

==================================================
【額外要求】
==================================================

1. 不要超過 200 行
2. 若場景過大，請拆成多份 scenario
3. 不要產生巨大總文件
4. 文件需適合：
   - 新人閱讀
   - AI 後續引用
   - QA 理解流程
5. 若發現流程缺少 README / db-usage / rules，請額外列出：
   - 建議新增文件
   - 建議新增規則
   - 建議新增測試情境