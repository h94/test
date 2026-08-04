---
aidata_db_sync: true
engine: cassandra
db_name: feedback
source: 192.168.55.80:9042
keyspace: feedback
table_count: 7
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T06:58:54.1750236Z
sync_log_id: 12
---

# Tables

## Table: businessmessages

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `feedback.businessmessages` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (datetime, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | respcontent | text | 是 | — |  |
| 2 | sendcontent | text | 是 | — |  |
| 3 | sendermail | text | 是 | — |  |
| 4 | status | int | 是 | — |  |
| 5 | updatetime | bigint | 是 | — |  |
| 6 | datetime | text | 是 | — | CK |
| 7 | site | text | 是 | — | PK |
| 8 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "respcontent": null,
  "sendcontent": "test",
  "sendermail": "furrymon2022@gmail.com",
  "status": 0,
  "updatetime": 1695089950,
  "datetime": "2023-09-19 10:19",
  "site": "sport",
  "id": "4V6XSH75ak"
}
```

## Table: feedbacks_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `feedback.feedbacks_sport` |
| 引擎 | cassandra |
| Primary Key | (tid) clustering: (datetime, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | adminimgpath | list<text> | 是 | — |  |
| 2 | email | text | 是 | — |  |
| 3 | imgpath | list<text> | 是 | — |  |
| 4 | problem | list<text> | 是 | — |  |
| 5 | respcontent | list<text> | 是 | — |  |
| 6 | status | int | 是 | — |  |
| 7 | updatetime | bigint | 是 | — |  |
| 8 | datetime | text | 是 | — | CK |
| 9 | tid | text | 是 | — | PK |
| 10 | account | text | 是 | — | CK |
| 11 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "adminimgpath": null,
  "email": "a85037678@yahoo.com.tw",
  "imgpath": null,
  "problem": [
    "{\u0022DateTime\u0022:\u00222025-05-14 00:35:34\u0022,\u0022Message\u0022:\u0022\u8ACB\u554F\u4E00\u4E0BZ\u5E63\u5546\u57CE\u6771\u897F\u4F55\u6642\u53EF\u4EE5\u514C\u63DB\\n\u6BCF\u6B21\u770B\u5230\u6C92\u6709\u53EF\u4EE5\u514C\u63DB\u3002\\n\u662F\u4E0D\u662F\u6709\u56FA\u5B9A\u6642\u9593\u53EF\u4EE5\u514C\u63DB\u3002\u0022}"
  ],
  "respcontent": [
    "{\u0022DateTime\u0022:\u00222025-05-14 08:27:44\u0022,\u0022Message\u0022:\u0022\u60A8\u597D, \u76EE\u524D\u5546\u54C1\u514C\u63DB\u9084\u5728\u505A\u6700\u5F8C\u7684\u6CD5\u52D9\u76F8\u95DC\u554F\u984C\u78BA\u8A8D, \u7B49\u78BA\u8A8D\u5B8C\u5F8C\u5C31\u6703\u958B\u653E\u5546\u54C1\u514C\u63DB\uFF0C\u8B1D\u8B1D\u3002\u0022}"
  ],
  "status": 2,
  "updatetime": 1747268757,
  "datetime": "2025-05-14 00:35",
  "tid": "fwX1fc4SUG",
  "account": "E2zmFRG1F0V",
  "id": "qIn1B6i7RE"
}
```

## Table: feedbacks_stock

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `feedback.feedbacks_stock` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | account | text | 是 | — |  |
| 2 | datetime | text | 是 | — |  |
| 3 | email | text | 是 | — |  |
| 4 | problem | list<text> | 是 | — |  |
| 5 | respcontent | list<text> | 是 | — |  |
| 6 | status | int | 是 | — |  |
| 7 | tid | text | 是 | — |  |
| 8 | updatetime | bigint | 是 | — |  |
| 9 | id | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: questions_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `feedback.questions_sport` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | answer | map<text, text> | 是 | — |  |
| 2 | enabled | int | 是 | — |  |
| 3 | question | map<text, text> | 是 | — |  |
| 4 | sort | int | 是 | — |  |
| 5 | tid | text | 是 | — |  |
| 6 | id | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: questions_stock

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `feedback.questions_stock` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | answer | text | 是 | — |  |
| 2 | enabled | int | 是 | — |  |
| 3 | question | text | 是 | — |  |
| 4 | sort | int | 是 | — |  |
| 5 | tid | text | 是 | — |  |
| 6 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "answer": "\u5982\u679C\u5DF2\u7D93\u70BAVIP\u6703\u54E1\uFF0C\u60A8\u53EF\u4EE5\u9078\u64C7\u76F4\u63A5\u8A02\u95B1\u9AD8\u7D1A\uFF0C\u4F46\u9700\u8981\u5F85\u539FVIP\u6642\u6548\u904E\u5F8C\u624D\u6703\u6539\u70BA\u9AD8\u7D1A\u5537",
  "enabled": 1,
  "question": "\u6211\u53EF\u4EE5\u5F9EVIP\u964D\u7D1A\u70BA\u9AD8\u7D1A\u55CE",
  "sort": 2,
  "tid": "5GQc958cOE",
  "id": "fRv90h6YO0"
}
```

## Table: topics_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `feedback.topics_sport` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | enabled | int | 是 | — |  |
| 2 | name | map<text, text> | 是 | — |  |
| 3 | sort | int | 是 | — |  |
| 4 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "enabled": 0,
  "name": {
    "en-US": "Product Redemption",
    "ja-JP": "Product Redemption",
    "th-TH": "Product Redemption",
    "zh-CN": "\u5546\u54C1\u5151\u6362",
    "zh-TW": "\u5546\u54C1\u514C\u63DB"
  },
  "sort": 5,
  "id": "fwX1fc4SUG"
}
```

## Table: topics_stock

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `feedback.topics_stock` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | enabled | int | 是 | — |  |
| 2 | name | text | 是 | — |  |
| 3 | sort | int | 是 | — |  |
| 4 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "enabled": 1,
  "name": "\u8A02\u95B1\u554F\u984C",
  "sort": 3,
  "id": "KPpNQVjHEW"
}
```

# Views
（無）

# Materialized Views
（無）

# Stored Procedures
（無）

# Functions
（無）

# Triggers
（無）

# Events
（無）

# User-Defined Types
（無）

# Cassandra Objects
（無）
