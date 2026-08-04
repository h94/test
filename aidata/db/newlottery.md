---
aidata_db_sync: true
engine: mysql
db_name: newlottery
source: 192.168.9.232:3306
keyspace: NewLottery
table_count: 4
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:25:17.1809351Z
sync_log_id: 31
---

# Tables

## Table: ChampionshipWallet

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `NewLottery.ChampionshipWallet` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | bigint | 否 | — | PK |
| 2 | Account | varchar | 否 | — |  |
| 3 | Balance | bigint | 否 | — |  |
| 4 | CID | char | 否 | — |  |
| 5 | LastUpdateTime | timestamp | 否 | CURRENT_TIMESTAMP |  |

### Sample（first row）

(empty table)

## Table: ChampionShipWallet_Transactions

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `NewLottery.ChampionShipWallet_Transactions` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | bigint | 否 | — | PK |
| 2 | AddTime | timestamp | 否 | CURRENT_TIMESTAMP |  |
| 3 | Account | varchar | 否 | — |  |
| 4 | CID | char | 否 | — |  |
| 5 | Point | bigint | 否 | — |  |
| 6 | T_Detail | varchar | 是 | — |  |
| 7 | T_Type | int | 否 | — |  |

### Sample（first row）

(empty table)

## Table: CoinWallet

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `NewLottery.CoinWallet` |
| 引擎 | mysql |
| Primary Key | (Account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | Account | varchar | 否 | — | PK |
| 2 | Balance | int | 否 | — |  |
| 3 | LastUpdateTime | timestamp | 否 | CURRENT_TIMESTAMP |  |

### Sample（first row）

```json
{
  "Account": "rankballtest15",
  "Balance": 0,
  "LastUpdateTime": "2026-05-28T16:44:44"
}
```

## Table: CoinWallet_Transactions

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `NewLottery.CoinWallet_Transactions` |
| 引擎 | mysql |
| Primary Key | (T_ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | T_ID | bigint | 否 | — | PK |
| 2 | Account | varchar | 否 | — |  |
| 3 | AddTime | timestamp | 否 | CURRENT_TIMESTAMP |  |
| 4 | Coin | int | 否 | — |  |
| 5 | T_Date | date | 否 | — |  |
| 6 | T_Detail | varchar | 是 | — |  |
| 7 | T_Type | int | 否 | — |  |
| 8 | T_UID | char | 是 | — |  |

### Sample（first row）

```json
{
  "T_ID": 1,
  "Account": "zbdigital007",
  "AddTime": "2026-04-22T09:23:41",
  "Coin": 300,
  "T_Date": "2026-04-22T00:00:00",
  "T_Detail": "",
  "T_Type": 77,
  "T_UID": ""
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
