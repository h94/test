---
aidata_db_sync: true
engine: cassandra
db_name: product
source: 192.168.55.80:9042
keyspace: product
table_count: 6
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:27:59.3601829Z
sync_log_id: 35
---

# Tables

## Table: products_activity

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `product.products_activity` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (activityevent, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | names | map<text, text> | 是 | — |  |
| 2 | price | int | 是 | — |  |
| 3 | quantity | int | 是 | — |  |
| 4 | status | int | 是 | — |  |
| 5 | updatetime | bigint | 是 | — |  |
| 6 | activityevent | text | 是 | — | CK |
| 7 | site | text | 是 | — | PK |
| 8 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "names": {
    "en-US": "5000 NT",
    "zh-TW": "\u81FA\u5E635000\u5143\u6574"
  },
  "price": 10,
  "quantity": 30,
  "status": 1,
  "updatetime": 1747878174,
  "activityevent": "cpbl-mainwinstreak",
  "site": "inplayz",
  "id": "7i0LMVpzhk"
}
```

## Table: products_activity_redeem_logs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `product.products_activity_redeem_logs` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (activityevent, account, id, pid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | status | int | 是 | — |  |
| 3 | updatetime | bigint | 是 | — |  |
| 4 | activityevent | text | 是 | — | CK |
| 5 | site | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | id | text | 是 | — | CK |
| 8 | pid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775981170,
  "status": 1,
  "updatetime": 1778479427,
  "activityevent": "mlb-mainwinstreak",
  "site": "inplayz",
  "account": "GHp9qwUAHIF",
  "id": "Zj93IPs3UO",
  "pid": "GVLpHMiLFE"
}
```

## Table: products_store

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `product.products_store` |
| 引擎 | cassandra |
| Primary Key | (pclass) clustering: (pid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | description | map<text, text> | 是 | — |  |
| 2 | image_path | map<text, text> | 是 | — |  |
| 3 | lastup_time | bigint | 是 | — |  |
| 4 | originalprice | int | 是 | — |  |
| 5 | pnames | map<text, text> | 是 | — |  |
| 6 | popular | boolean | 是 | — |  |
| 7 | price | int | 是 | — |  |
| 8 | psource | text | 是 | — |  |
| 9 | sequence | int | 是 | — |  |
| 10 | status | text | 是 | — |  |
| 11 | pclass | text | 是 | — | PK |
| 12 | pid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "description": {
    "zh-TW": "\u6211\u7684\u5065\u5EB7\u65E5\u8A18 \u8702\u738B\u81A0\u539F\u98F2(6\u5165/\u76D2)x2\u76D2"
  },
  "image_path": {
    "title": "https://inplayz.com/sport/img/product/f4D6ceQtb0.webp"
  },
  "lastup_time": 1744262431,
  "originalprice": 1200,
  "pnames": {
    "zh-TW": "\u6211\u7684\u5065\u5EB7\u65E5\u8A18 \u8702\u738B\u81A0\u539F\u98F2(6\u5165/\u76D2)x2\u76D2"
  },
  "popular": false,
  "price": 150000,
  "psource": "https://24h.pchome.com.tw/prod/DBAUFK-1900B1ZML",
  "sequence": 0,
  "status": "1",
  "pclass": "HP",
  "pid": "5xv7XjgS90"
}
```

## Table: product_store_redeem_logs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `product.product_store_redeem_logs` |
| 引擎 | cassandra |
| Primary Key | (pclass) clustering: (pid, addtime, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | address | text | 是 | — |  |
| 2 | cheadshot | text | 是 | — |  |
| 3 | cmemo | text | 是 | — |  |
| 4 | cname | text | 是 | — |  |
| 5 | deliverytime | bigint | 是 | — |  |
| 6 | description | text | 是 | — |  |
| 7 | phonenumber | text | 是 | — |  |
| 8 | recipient | text | 是 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | updatetime | bigint | 是 | — |  |
| 11 | pclass | text | 是 | — | PK |
| 12 | pid | text | 是 | — | CK |
| 13 | addtime | bigint | 是 | — | CK |
| 14 | account | text | 是 | — | CK |
| 15 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "address": "404\u53F0\u4E2D\u5E02\u5317\u5340\u4E2D\u6E05\u8DEF\u4E00\u6BB589\u865F6\u865F6\u6A13\u4E4B1",
  "cheadshot": "https://inplayz.com/sport/img/upload/WyfoIxLrVF/NF9TJZRTnZ.webp",
  "cmemo": "",
  "cname": "\u6D77\u666F\u4F4F\u5225\u5885",
  "deliverytime": 0,
  "description": null,
  "phonenumber": "0900456789",
  "recipient": "\u99AC\u514B\u676F",
  "status": "2",
  "updatetime": 1745375636,
  "pclass": "HP",
  "pid": "j7u0n7xzh0",
  "addtime": 1744967737,
  "account": "E4iEpjVPCAe",
  "id": "YlucoUM6Kk"
}
```

## Table: product_store_stock_logs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `product.product_store_stock_logs` |
| 引擎 | cassandra |
| Primary Key | (pclass) clustering: (pid, addtime, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | quantity | int | 是 | — |  |
| 2 | updatetime | bigint | 是 | — |  |
| 3 | pclass | text | 是 | — | PK |
| 4 | pid | text | 是 | — | CK |
| 5 | addtime | bigint | 是 | — | CK |
| 6 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "quantity": 25,
  "updatetime": 1744263082,
  "pclass": "HP",
  "pid": "5xv7XjgS90",
  "addtime": 1744263082,
  "id": "yM4ASh5gUK"
}
```

## Table: withdrawlogs_activity

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `product.withdrawlogs_activity` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (activityevent, account, cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | contactnumber | text | 是 | — |  |
| 2 | status | int | 是 | — |  |
| 3 | updatetime | bigint | 是 | — |  |
| 4 | activityevent | text | 是 | — | CK |
| 5 | site | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | cid | int | 是 | — | CK |

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
