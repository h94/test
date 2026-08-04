---
aidata_db_sync: true
engine: mysql
db_name: sport
source: 192.168.9.232:3306
keyspace: Sport
table_count: 7
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:18:51.9162285Z
sync_log_id: 25
---

# Tables

## Table: BK_SitePlayers

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Sport.BK_SitePlayers` |
| 引擎 | mysql |
| Primary Key | (Site, SiteID, Year) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | Site | varchar | 否 | — | PK |
| 2 | SiteID | varchar | 否 | — | PK |
| 3 | Year | varchar | 否 | — | PK |
| 4 | League | varchar | 否 | — |  |
| 5 | Name | varchar | 否 | — |  |
| 6 | TeamID | varchar | 否 | — |  |
| 7 | Team | varchar | 否 | — |  |
| 8 | Record | mediumtext | 否 | — |  |
| 9 | LastUpdateTime | bigint | 否 | — |  |

### Sample（first row）

```json
{
  "Site": "nba.com",
  "SiteID": "203210",
  "Year": "2017/18",
  "League": "NBA",
  "Name": "JaMychal Green",
  "TeamID": "",
  "Team": "Golden State Warriors",
  "Record": "{\u0022MIN\u0022:\u00221541.8133333333333\u0022,\u0022FGM\u0022:\u0022223\u0022,\u0022FGA\u0022:\u0022488\u0022,\u0022FG_Percentage\u0022:\u002245.7\u0022,\u00223PM\u0022:\u002243\u0022,\u00223PA\u0022:\u0022127\u0022,\u00223P_Percentage\u0022:\u002233.9\u0022,\u0022FTM\u0022:\u002280\u0022,\u0022FTA\u0022:\u0022111\u0022,\u0022FT_Percentage\u0022:\u002272.1\u0022,\u0022OREB\u0022:\u0022147\u0022,\u0022DREB\u0022:\u0022317\u0022,\u0022REB\u0022:\u0022464\u0022,\u0022AST\u0022:\u002279\u0022,\u0022STL\u0022:\u002232\u0022,\u0022BLK\u0022:\u002225\u0022,\u0022TOV\u0022:\u002276\u0022,\u0022PF\u0022:\u0022153\u0022,\u0022PTS\u0022:\u0022569\u0022,\u0022PlusMInus\u0022:\u0022-250\u0022}",
  "LastUpdateTime": 1676604302
}
```

## Table: ChatRoomHistories_Backup

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Sport.ChatRoomHistories_Backup` |
| 引擎 | mysql |
| Primary Key | (GID, Account, ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | GID | char | 否 | — | PK |
| 2 | Account | char | 否 | — | PK |
| 3 | ID | char | 否 | — | PK |
| 4 | AddTime | bigint | 否 | — |  |
| 5 | Message | varchar | 否 | — |  |
| 6 | ResponseID | varchar | 是 | — |  |
| 7 | LikeAccount | varchar | 是 | — |  |
| 8 | ChatType | char | 否 | — |  |
| 9 | Rank | int | 否 | — |  |
| 10 | UserName | varchar | 否 | — |  |
| 11 | HeadShotPath | varchar | 是 | — |  |

### Sample（first row）

```json
{
  "GID": "zSNaKdwLkq",
  "Account": "EXnu39NYYjV",
  "ID": "6p9LYGpyj0",
  "AddTime": 1719366017000,
  "Message": "{0x1f232}",
  "ResponseID": null,
  "LikeAccount": null,
  "ChatType": "text",
  "Rank": 1,
  "UserName": "\u672C\u5730Dive",
  "HeadShotPath": "https://inplayz.com/sport/icons/img_chat_crown.png"
}
```

## Table: Community_Groups

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Sport.Community_Groups` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | char | 否 | — | PK |
| 2 | Name | varchar | 否 | — |  |
| 3 | Enabled | int | 否 | — |  |
| 4 | IconPath | varchar | 否 | — |  |
| 5 | Seq | int | 否 | — |  |
| 6 | GType | char | 否 | — |  |
| 7 | Owner | varchar | 是 | — |  |
| 8 | Description | text | 是 | — |  |
| 9 | UpdateTime | bigint | 否 | — |  |

### Sample（first row）

```json
{
  "ID": "osws44Th70",
  "Name": "{\u0022zh-TW\u0022:\u0022\\u6211\\u7684\\u500B\\u4EBA\\u7FA4\\u7D44\u0022,\u0022zh-CN\u0022:\u0022\\u6211\\u7684\\u500B\\u4EBA\\u7FA4\\u7D44\u0022,\u0022en-US\u0022:\u0022my personal group\u0022}",
  "Enabled": 1,
  "IconPath": "https://inplayz.com/sport/img/upload/zfSgXdRtyB/Fx8dSDJNVu.webp",
  "Seq": 3,
  "GType": "personal",
  "Owner": "EXnu39NYYjV",
  "Description": "\u6E2C\u8A66\u500B\u4EBA\u7FA4\u7D44",
  "UpdateTime": 1709619295
}
```

## Table: GameUsers_Wallet

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Sport.GameUsers_Wallet` |
| 引擎 | mysql |
| Primary Key | (AuthKey) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | AuthKey | char | 否 | — | PK |
| 2 | Balance | int | 否 | — |  |
| 3 | LastUpdateTime | timestamp | 否 | CURRENT_TIMESTAMP |  |

### Sample（first row）

```json
{
  "AuthKey": "JXUyo8x4CG",
  "Balance": 30000,
  "LastUpdateTime": "2025-07-18T11:03:11"
}
```

## Table: GameUsers_Wallet_Transactions

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Sport.GameUsers_Wallet_Transactions` |
| 引擎 | mysql |
| Primary Key | (TID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | TID | int | 否 | — | PK |
| 2 | AddTime | timestamp | 否 | CURRENT_TIMESTAMP |  |
| 3 | Amount | int | 否 | — |  |
| 4 | AuthKey | char | 否 | — |  |
| 5 | TDate | date | 否 | — |  |
| 6 | Type | int | 否 | — |  |
| 7 | TypeInfo | varchar | 否 | — |  |

### Sample（first row）

```json
{
  "TID": 261,
  "AddTime": "2026-05-12T11:29:42",
  "Amount": 1000,
  "AuthKey": "tcK09FqHTr",
  "TDate": "2026-05-12T00:00:00",
  "Type": 1,
  "TypeInfo": "{\u0022Account\u0022:\u0022EzSigtEGPwU\u0022,\u0022GameType\u0022:\u0022BP\u0022,\u0022GDate\u0022:\u00222025-06-24\u0022,\u0022GID\u0022:\u0022WSmkiyncak\u0022,\u0022ID\u0022:\u0022WSmkiyncak\u0022,\u0022LID\u0022:\u0022WSmkiyncak\u0022,\u0022PredictMessage\u0022:\u0022betpool profit\u0022}"
}
```

## Table: Notification_Messages

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Sport.Notification_Messages` |
| 引擎 | mysql |
| Primary Key | (TID, ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | TID | varchar | 否 | — | PK |
| 2 | ID | varchar | 否 | — | PK |
| 3 | Enabled | int | 否 | — |  |
| 4 | Title | text | 否 | — |  |
| 5 | TW_Content | text | 否 | — |  |
| 6 | EN_Content | text | 是 | — |  |
| 7 | CN_Content | text | 是 | — |  |
| 8 | JP_Content | text | 是 | — |  |
| 9 | TH_Content | text | 是 | — |  |
| 10 | UpdateTime | bigint | 否 | — |  |

### Sample（first row）

```json
{
  "TID": "5KggzuXTFU",
  "ID": "FZcLY90UoU",
  "Enabled": 0,
  "Title": "{\u0022zh-TW\u0022:\u0022A\u0022,\u0022zh-CN\u0022:\u0022B\u0022,\u0022en-US\u0022:\u0022C\u0022}",
  "TW_Content": "D",
  "EN_Content": "FG",
  "CN_Content": "E",
  "JP_Content": null,
  "TH_Content": null,
  "UpdateTime": 1697526153
}
```

## Table: Notification_Topics

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Sport.Notification_Topics` |
| 引擎 | mysql |
| Primary Key | (ID) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | ID | varchar | 否 | — | PK |
| 2 | Enabled | int | 否 | — |  |
| 3 | NameMap | text | 否 | — |  |
| 4 | IconPath | text | 否 | — |  |
| 5 | IconColorCode | text | 否 | — |  |
| 6 | Seq | int | 否 | — |  |
| 7 | UpdateTime | bigint | 否 | — |  |

### Sample（first row）

```json
{
  "ID": "K6cEXaWuVE",
  "Enabled": 0,
  "NameMap": "{\u0022zh-TW\u0022:\u0022\u5E73\u53F0\u6D3B\u52D5\u0022,\u0022zh-CN\u0022:\u0022\u5E73\u53F0\u6D3B\u52A8\u0022,\u0022en-US\u0022:\u0022Platform activities\u0022,\u0022ja-JP\u0022:\u0022\u5E73\u53F0\u6D3B\u52D5\u0022,\u0022th-TH\u0022:\u0022\u5E73\u53F0\u6D3B\u52D5\u0022}",
  "IconPath": "https://inplayz.com/sport/icons/icon_promotion.svg",
  "IconColorCode": "#97b4ff",
  "Seq": 2,
  "UpdateTime": 1735522946
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
