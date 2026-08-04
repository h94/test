---
aidata_db_sync: true
engine: mysql
db_name: stock
source: 192.168.9.232:3306
keyspace: Stock
table_count: 8
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:28:12.0974995Z
sync_log_id: 36
---

# Tables

## Table: FavoriteBroker

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.FavoriteBroker` |
| 引擎 | mysql |
| Primary Key | (User, Name) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | User | varchar | 否 | — | PK |
| 2 | Name | varchar | 否 | — | PK |
| 3 | Value | text | 否 | — |  |

### Sample（first row）

```json
{
  "User": "zb01",
  "Name": "\u624B\u6A5F\u5132\u5B58\u6E2C\u8A66",
  "Value": "[\u0022\u53F0\u7063\u4F01\u9280-\u53F0\u5357\u0022,\u0022\u5408\u5EAB\u0022,\u0022\u5408\u5EAB-\u53F0\u4E2D\u0022,\u0022\u571F\u9280\u0022,\u0022\u571F\u9280-\u53F0\u4E2D\u0022]"
}
```

## Table: FavoriteRule

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.FavoriteRule` |
| 引擎 | mysql |
| Primary Key | (User, Name, Strategy) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | User | varchar | 否 | — | PK |
| 2 | Name | varchar | 否 | — | PK |
| 3 | Strategy | int | 否 | — | PK |
| 4 | Value | varchar | 否 | — |  |
| 5 | NeedSend | int | 否 | — |  |
| 6 | FirstMatch | int | 否 | — |  |
| 7 | Industry | varchar | 是 | — |  |
| 8 | FilterMarket | varchar | 是 | — |  |
| 9 | Country | varchar | 否 | tw |  |

### Sample（first row）

```json
{
  "User": "zb08",
  "Name": "\u6295\u4FE1\u8CB7\u8D85\u002B\u4E09\u5927\u6CD5\u4EBA\u8CB7\u8D85\u524D50\u540D",
  "Strategy": 19,
  "Value": "[\u0022\u6295\u4FE1\u0022,\u0022\u8CB7\u8D85\u0022,\u00225\u0022,\u00221000\u0022]",
  "NeedSend": 0,
  "FirstMatch": 0,
  "Industry": null,
  "FilterMarket": null,
  "Country": "tw"
}
```

## Table: FavoriteStock

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.FavoriteStock` |
| 引擎 | mysql |
| Primary Key | (ID, User) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | int | 否 | — | PK |
| 2 | User | varchar | 否 | — | PK |
| 3 | Name | varchar | 否 | — |  |
| 4 | Value | text | 否 | — |  |
| 5 | Country | varchar | 否 | tw |  |

### Sample（first row）

```json
{
  "ID": 10,
  "User": "zb01",
  "Name": "\u81EA\u9078\u80A11",
  "Value": "[\u00221503\u0022,\u00221102\u0022,\u00221319\u0022,\u00221259\u0022,\u00221595\u0022]",
  "Country": "tw"
}
```

## Table: MessageLog

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.MessageLog` |
| 引擎 | mysql |
| Primary Key | (Date, Account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | Date | varchar | 否 | — | PK |
| 2 | Account | varchar | 否 | — | PK |
| 3 | SendAction | varchar | 否 | — |  |
| 4 | TargetAddress | varchar | 否 | — |  |
| 5 | SendStatus | int | 否 | — |  |
| 6 | MsgContent | text | 否 | — |  |
| 7 | AddTime | datetime | 否 | — |  |
| 8 | LastUpdateTime | timestamp | 否 | CURRENT_TIMESTAMP |  |

### Sample（first row）

(empty table)

## Table: Options

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.Options` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | int | 否 | — | PK |
| 2 | Value | varchar | 否 | — |  |
| 3 | Enabled | int | 否 | 1 |  |

### Sample（first row）

```json
{
  "ID": 7,
  "Value": "[\u00221\u0022,\u00222\u0022,\u00223\u0022,\u00224\u0022,\u00225\u0022,\u00226\u0022,\u00227\u0022,\u00228\u0022,\u00229\u0022,\u002210\u0022]",
  "Enabled": 1
}
```

## Table: Rules

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.Rules` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | int | 否 | — | PK |
| 2 | Type | varchar | 否 | — |  |
| 3 | Indicator | varchar | 否 | — |  |
| 4 | Text | varchar | 否 | — |  |
| 5 | Enabled | int | 否 | 1 |  |
| 6 | Parameter | varchar | 否 | — |  |
| 7 | Countries | varchar | 否 | — |  |

### Sample（first row）

```json
{
  "ID": 110,
  "Type": "\u6280\u8853\u9762",
  "Indicator": "test",
  "Text": "#0 \u5927\u65BC123kd#0 #2 ",
  "Enabled": 0,
  "Parameter": "[\u00222\u0022,\u00222\u0022,\u0022K\u0022]",
  "Countries": "[\u0022tw\u0022]"
}
```

## Table: SubLogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.SubLogs` |
| 引擎 | mysql |
| Primary Key | (Account, AddTime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | Account | varchar | 否 | — | PK |
| 2 | AddTime | bigint | 否 | — | PK |
| 3 | TradeNo | varchar | 否 | — |  |
| 4 | SubID | varchar | 否 | — |  |
| 5 | SubRank | int | 否 | — |  |
| 6 | SubTime | varchar | 否 | — |  |
| 7 | SubEndTime | varchar | 否 | — |  |

### Sample（first row）

```json
{
  "Account": "sky31",
  "AddTime": 1667271318615,
  "TradeNo": "TfE70Tg0ek",
  "SubID": "1",
  "SubRank": 2,
  "SubTime": "2022-11-01 10:54:50",
  "SubEndTime": "2033-05-11 23:59:59"
}
```

## Table: Users

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Stock.Users` |
| 引擎 | mysql |
| Primary Key | (Account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | Account | varchar | 否 | — | PK |
| 2 | Password | varchar | 否 | — |  |
| 3 | Enabled | int | 否 | 1 |  |
| 4 | Rank | int | 否 | — |  |
| 5 | SendAction | varchar | 是 | — |  |
| 6 | Phone | varchar | 是 | — |  |
| 7 | Email | varchar | 否 | — |  |
| 8 | ChatID | varchar | 是 | — |  |
| 9 | AddTime | datetime | 否 | — |  |
| 10 | SubEndTime | datetime | 是 | — |  |
| 11 | LastUpdateTime | timestamp | 否 | CURRENT_TIMESTAMP |  |

### Sample（first row）

```json
{
  "Account": "vmwum0",
  "Password": "***",
  "Enabled": 1,
  "Rank": 1,
  "SendAction": null,
  "Phone": null,
  "Email": "410721204@gms.ndhu.edu.tw",
  "ChatID": null,
  "AddTime": "2022-08-22T20:22:51",
  "SubEndTime": "0001-01-01T00:00:00",
  "LastUpdateTime": "2022-08-22T20:23:06"
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
