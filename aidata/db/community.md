---
aidata_db_sync: true
engine: cassandra
db_name: community
source: 192.168.55.80:9042
keyspace: community
table_count: 1
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T06:58:47.6274413Z
sync_log_id: 11
---

# Tables

## Table: newlottery_forums

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `community.newlottery_forums` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | country_code | text | 是 | — |  |
| 2 | edit_timestamp | bigint | 是 | — |  |
| 3 | icon | text | 是 | — |  |
| 4 | names | map<text, text> | 是 | — |  |
| 5 | status | int | 是 | — |  |
| 6 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "country_code": null,
  "edit_timestamp": 0,
  "icon": "BS",
  "names": {
    "zh-TW": "MLB"
  },
  "status": 1,
  "id": "FjjJdx6RZSTi6nvBf2iVVb"
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
