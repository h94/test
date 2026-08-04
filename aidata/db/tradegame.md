---
aidata_db_sync: true
engine: cassandra
db_name: tradegame
source: 192.168.55.80:9042
keyspace: tradegame
table_count: 11
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-07-14T09:21:52.5780616Z
sync_log_id: 9618
---

# Tables

## Table: resultlogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.resultlogs` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | lid | text | 是 | — |  |
| 3 | status | int | 是 | — |  |
| 4 | gdate | text | 是 | — | PK |
| 5 | gtype | text | 是 | — | CK |
| 6 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779971047094,
  "lid": "LjrDeSvUKa0",
  "status": 1,
  "gdate": "2026-05-28",
  "gtype": "BS",
  "gid": "GoSSYZPkQV0"
}
```

## Table: settings_gametype

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.settings_gametype` |
| 引擎 | cassandra |
| Primary Key | (gametype) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enabled | int | 是 | — |  |
| 3 | lids | text | 是 | — |  |
| 4 | gametype | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: settings_score

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.settings_score` |
| 引擎 | cassandra |
| Primary Key | (gtype, layer) clustering: (lid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | rules | text | 是 | — |  |
| 3 | gtype | text | 是 | — | PK |
| 4 | lid | text | 是 | — | CK |
| 5 | layer | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: settings_stock

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.settings_stock` |
| 引擎 | cassandra |
| Primary Key | (gtype, layer) clustering: (lid, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | gdate | text | 是 | — |  |
| 3 | initial_stock_num | int | 是 | — |  |
| 4 | rules | text | 是 | — |  |
| 5 | gtype | text | 是 | — | PK |
| 6 | lid | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |
| 8 | layer | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: stock_holdings_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.stock_holdings_BK` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (lid, gid, account, mode_spread_type) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | mode | text | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | ratio | int | 是 | — |  |
| 5 | spread | int | 是 | — |  |
| 6 | stock_num | int | 是 | — |  |
| 7 | trade_history | text | 是 | — |  |
| 8 | winloss | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | lid | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |
| 12 | account | text | 是 | — | CK |
| 13 | mode_spread_type | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1783267771071,
  "mode": "1X2",
  "oddtype": "A",
  "ratio": 0,
  "spread": 0,
  "stock_num": 0,
  "trade_history": "[{\u0022stock_price\u0022: 94, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 1000, \u0022profitpoint\u0022: -94000, \u0022trade_time\u0022: \u00222026-07-05 23:50:41\u0022}, {\u0022stock_price\u0022: 92, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 1000, \u0022profitpoint\u0022: -92000, \u0022trade_time\u0022: \u00222026-07-06 00:09:31\u0022}, {\u0022stock_price\u0022: 0, \u0022trade_type\u0022: \u0022sell\u0022, \u0022trade_operator\u0022: \u0022system\u0022, \u0022num\u0022: 2000, \u0022profitpoint\u0022: 0, \u0022trade_time\u0022: \u00222026-07-06 01:55:33\u0022}]",
  "winloss": "L",
  "gdate": "2026-07-05",
  "lid": "LW95M9CSEdE",
  "gid": "G1HMzZLCRhU",
  "account": "ETiEtvGDJVa",
  "mode_spread_type": "1X2_1X2_A"
}
```

## Table: stock_holdings_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.stock_holdings_BS` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (lid, gid, account, mode_spread_type) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | mode | text | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | ratio | int | 是 | — |  |
| 5 | spread | int | 是 | — |  |
| 6 | stock_num | int | 是 | — |  |
| 7 | trade_history | text | 是 | — |  |
| 8 | winloss | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | lid | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |
| 12 | account | text | 是 | — | CK |
| 13 | mode_spread_type | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1783245315158,
  "mode": "HA",
  "oddtype": "A",
  "ratio": -100,
  "spread": -2,
  "stock_num": 0,
  "trade_history": "[{\u0022stock_price\u0022: 67, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 1000, \u0022profitpoint\u0022: -67000, \u0022trade_time\u0022: \u00222026-07-05 17:55:01\u0022}, {\u0022stock_price\u0022: 67, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 100, \u0022profitpoint\u0022: -6700, \u0022trade_time\u0022: \u00222026-07-05 17:55:15\u0022}, {\u0022stock_price\u0022: 100, \u0022trade_type\u0022: \u0022sell\u0022, \u0022trade_operator\u0022: \u0022system\u0022, \u0022num\u0022: 1100, \u0022profitpoint\u0022: 104500, \u0022trade_time\u0022: \u00222026-07-05 20:16:19\u0022}]",
  "winloss": "W",
  "gdate": "2026-07-05",
  "lid": "LJ8raQHZPXU",
  "gid": "Ga9bgw9pPMU",
  "account": "ECrCyXhW5k6",
  "mode_spread_type": "HA_-1.5_A"
}
```

## Table: stock_holdings_ES

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.stock_holdings_ES` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (lid, gid, account, mode_spread_type) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | mode | text | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | ratio | int | 是 | — |  |
| 5 | spread | int | 是 | — |  |
| 6 | stock_num | int | 是 | — |  |
| 7 | trade_history | text | 是 | — |  |
| 8 | winloss | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | lid | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |
| 12 | account | text | 是 | — | CK |
| 13 | mode_spread_type | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: stock_holdings_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.stock_holdings_FL` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (lid, gid, account, mode_spread_type) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | mode | text | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | ratio | int | 是 | — |  |
| 5 | spread | int | 是 | — |  |
| 6 | stock_num | int | 是 | — |  |
| 7 | trade_history | text | 是 | — |  |
| 8 | winloss | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | lid | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |
| 12 | account | text | 是 | — | CK |
| 13 | mode_spread_type | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: stock_holdings_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.stock_holdings_HL` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (lid, gid, account, mode_spread_type) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | mode | text | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | ratio | int | 是 | — |  |
| 5 | spread | int | 是 | — |  |
| 6 | stock_num | int | 是 | — |  |
| 7 | trade_history | text | 是 | — |  |
| 8 | winloss | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | lid | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |
| 12 | account | text | 是 | — | CK |
| 13 | mode_spread_type | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: stock_holdings_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.stock_holdings_SC` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (lid, gid, account, mode_spread_type) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | mode | text | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | ratio | int | 是 | — |  |
| 5 | spread | int | 是 | — |  |
| 6 | stock_num | int | 是 | — |  |
| 7 | trade_history | text | 是 | — |  |
| 8 | winloss | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | lid | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |
| 12 | account | text | 是 | — | CK |
| 13 | mode_spread_type | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1783262547279,
  "mode": "1X2",
  "oddtype": "A",
  "ratio": 0,
  "spread": 0,
  "stock_num": 0,
  "trade_history": "[{\u0022stock_price\u0022: 5, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 501, \u0022profitpoint\u0022: -2505, \u0022trade_time\u0022: \u00222026-07-05 22:42:06\u0022}, {\u0022stock_price\u0022: 5, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 1000, \u0022profitpoint\u0022: -5000, \u0022trade_time\u0022: \u00222026-07-05 22:42:11\u0022}, {\u0022stock_price\u0022: 5, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 400, \u0022profitpoint\u0022: -2000, \u0022trade_time\u0022: \u00222026-07-05 22:42:21\u0022}, {\u0022stock_price\u0022: 5, \u0022trade_type\u0022: \u0022buy\u0022, \u0022trade_operator\u0022: \u0022user\u0022, \u0022num\u0022: 1, \u0022profitpoint\u0022: -5, \u0022trade_time\u0022: \u00222026-07-05 22:42:27\u0022}, {\u0022stock_price\u0022: 0, \u0022trade_type\u0022: \u0022sell\u0022, \u0022trade_operator\u0022: \u0022system\u0022, \u0022num\u0022: 1902, \u0022profitpoint\u0022: 0, \u0022trade_time\u0022: \u00222026-07-05 23:10:55\u0022}]",
  "winloss": "L",
  "gdate": "2026-07-05",
  "lid": "L91uKA8KTgk",
  "gid": "GU8XIgiGyrk",
  "account": "G3hGFcx5THU",
  "mode_spread_type": "1X2_1X2_A"
}
```

## Table: stock_holdings_TN

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `tradegame.stock_holdings_TN` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (lid, gid, account, mode_spread_type) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | mode | text | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | ratio | int | 是 | — |  |
| 5 | spread | int | 是 | — |  |
| 6 | stock_num | int | 是 | — |  |
| 7 | trade_history | text | 是 | — |  |
| 8 | winloss | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | lid | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |
| 12 | account | text | 是 | — | CK |
| 13 | mode_spread_type | text | 是 | — | CK |

### Sample（first row）

(empty table)

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
