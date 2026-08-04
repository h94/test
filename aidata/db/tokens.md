---
aidata_db_sync: true
engine: mysql
db_name: tokens
source: 192.168.9.232:3306
keyspace: Tokens
table_count: 2
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:30:28.8803527Z
sync_log_id: 39
---

# Tables

## Table: Logs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Tokens.Logs` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | int | 否 | — | PK |
| 2 | CompanyCode | char | 否 |  |  |
| 3 | AccessTime | datetime | 否 | CURRENT_TIMESTAMP |  |
| 4 | Action | varchar | 否 |  |  |

### Sample（first row）

```json
{
  "ID": 261,
  "CompanyCode": "ZB",
  "AccessTime": "2022-10-04T09:37:58",
  "Action": "Token Validation Request: 7LrHjteaFX"
}
```

## Table: Tokens

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Tokens.Tokens` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | int | 否 | — | PK |
| 2 | HashKey | char | 否 |  |  |
| 3 | CompanyCode | char | 否 |  |  |
| 4 | AddTime | datetime | 否 | CURRENT_TIMESTAMP |  |
| 5 | ExpirationTime | datetime | 否 | CURRENT_TIMESTAMP |  |
| 6 | Enabled | int | 否 | 1 |  |

### Sample（first row）

```json
{
  "ID": 110,
  "HashKey": "eX1dxT4mks",
  "CompanyCode": "ZB",
  "AddTime": "2021-06-15T10:26:26",
  "ExpirationTime": "2021-06-15T11:26:26",
  "Enabled": 1
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
