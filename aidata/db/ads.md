---
aidata_db_sync: true
engine: cassandra
db_name: ads
source: 192.168.55.80:9042
keyspace: ads
table_count: 3
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T05:50:28.0593532Z
sync_log_id: 3
---

# Tables

## Table: advertising

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `ads.advertising` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | action | text | 是 | — |  |
| 2 | closetime | bigint | 是 | — |  |
| 3 | createdby | text | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | lang | text | 是 | — |  |
| 6 | path | text | 是 | — |  |
| 7 | seq | int | 是 | — |  |
| 8 | starttime | bigint | 是 | — |  |
| 9 | title | text | 是 | — |  |
| 10 | type | text | 是 | — |  |
| 11 | url | text | 是 | — |  |
| 12 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "action": "blank",
  "closetime": 2166796800,
  "createdby": "promotion",
  "enabled": 1,
  "lang": "zh-TW\u0026zh-CN\u0026en-US\u0026ja-JP\u0026vi-VN\u0026th-TH",
  "path": "advertising/202208220246\u4E0B\u8F09.png",
  "seq": 1,
  "starttime": 1659283200,
  "title": "\u80A1\u7968King",
  "type": "right",
  "url": "https://stock.zbdigital.net/",
  "id": "6Tl8wVLUiM"
}
```

## Table: advertising_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `ads.advertising_sport` |
| 引擎 | cassandra |
| Primary Key | (adarea) clustering: (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | adclass | text | 是 | — |  |
| 2 | closedate | text | 是 | — |  |
| 3 | enabled | int | 是 | — |  |
| 4 | imgpath | text | 是 | — |  |
| 5 | mobileimgpath | text | 是 | — |  |
| 6 | seq | int | 是 | — |  |
| 7 | startdate | text | 是 | — |  |
| 8 | supportlangs | list<text> | 是 | — |  |
| 9 | tageturl | text | 是 | — |  |
| 10 | title | text | 是 | — |  |
| 11 | adarea | text | 是 | — | PK |
| 12 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "adclass": "self",
  "closedate": "2028-01-24",
  "enabled": 0,
  "imgpath": "sport/advertising/Ckrh8g7kZk.jpg",
  "mobileimgpath": "sport/advertising/TUwZPPBlAU.jpg",
  "seq": 16,
  "startdate": "2024-05-10",
  "supportlangs": [
    "zh-TW"
  ],
  "tageturl": "https://inplayz.com/tw/master?page=SC\u0026lid=all\u0026tag=topKillerAccountLeaderboard\u0026pageIndex=1",
  "title": "XXXXX",
  "adarea": "banner",
  "id": "0EbpoFXKiU"
}
```

## Table: bulletinboard_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `ads.bulletinboard_sport` |
| 引擎 | cassandra |
| Primary Key | (aid) clustering: (addtime, announcementmethod) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | endtime | text | 是 | — |  |
| 2 | lastup_time | bigint | 是 | — |  |
| 3 | maintopic | map<text, text> | 是 | — |  |
| 4 | sequence | int | 是 | — |  |
| 5 | starttime | text | 是 | — |  |
| 6 | status | int | 是 | — |  |
| 7 | text1 | map<text, text> | 是 | — |  |
| 8 | text2 | map<text, text> | 是 | — |  |
| 9 | text3 | map<text, text> | 是 | — |  |
| 10 | addtime | bigint | 是 | — | CK |
| 11 | aid | text | 是 | — | PK |
| 12 | announcementmethod | int | 是 | — | CK |

### Sample（first row）

```json
{
  "endtime": "2090-05-22 23:59:59",
  "lastup_time": 1747965919,
  "maintopic": {
    "en-US": "Earn Z coins every day",
    "zh-CN": "\u6BCF\u5929\u8D5AZ\u5E01",
    "zh-TW": "\u6BCF\u5929\u8CFAZ\u5E63"
  },
  "sequence": 0,
  "starttime": "2025-05-22 00:00:01",
  "status": 1,
  "text1": {
    "en-US": "Redeem your mall gifts now!",
    "zh-CN": "\u5546\u57CE\u597D\u793C\u7B49\u4F60\u6362",
    "zh-TW": "\u5546\u57CE\u597D\u79AE\u7B49\u4F60\u63DB"
  },
  "text2": null,
  "text3": null,
  "addtime": 1747965919,
  "aid": "vKkijIdEeE",
  "announcementmethod": 1
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
