---
aidata_db_sync: true
engine: cassandra
db_name: member
source: 192.168.55.80:9042
keyspace: member
table_count: 22
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-07-06T05:38:36.3543686Z
sync_log_id: 8047
---

# Tables

## Table: appleinfos_game

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.appleinfos_game` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | email | text | 是 | — |  |
| 2 | name | text | 是 | — |  |
| 3 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "email": "nj52m7pwv8@privaterelay.appleid.com",
  "name": "James",
  "id": "001700.b7464d57943344788e9f1210f35d80bc.0705"
}
```

## Table: forbidden_email_domains

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.forbidden_email_domains` |
| 引擎 | cassandra |
| Primary Key | (name) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | name | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1734315629,
  "name": "gmaill.com"
}
```

## Table: gamerobots

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.gamerobots` |
| 引擎 | cassandra |
| Primary Key | (account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | enabled | int | 是 | — |  |
| 2 | lasttradetime | text | 是 | — |  |
| 3 | stoploss | int | 是 | — |  |
| 4 | takeprofit | int | 是 | — |  |
| 5 | account | text | 是 | — | PK |

### Sample（first row）

```json
{
  "enabled": 0,
  "lasttradetime": null,
  "stoploss": null,
  "takeprofit": null,
  "account": "EJFvJ1dGuwa"
}
```

## Table: gamesublogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.gamesublogs` |
| 引擎 | cassandra |
| Primary Key | (authkey) clustering: (subtime, tradeno, addtime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | autosub | boolean | 是 | — |  |
| 2 | paymethod | text | 是 | — |  |
| 3 | paytype | text | 是 | — |  |
| 4 | subendtime | text | 是 | — |  |
| 5 | subid | text | 是 | — |  |
| 6 | authkey | text | 是 | — | PK |
| 7 | subtime | text | 是 | — | CK |
| 8 | tradeno | text | 是 | — | CK |
| 9 | addtime | bigint | 是 | — | CK |

### Sample（first row）

```json
{
  "autosub": false,
  "paymethod": "disposable",
  "paytype": "Promation",
  "subendtime": "2034-06-11 23:59:59",
  "subid": "5",
  "authkey": "F15zYPRNzP",
  "subtime": "2024-06-11 10:51:27",
  "tradeno": "promation",
  "addtime": 1718079931
}
```

## Table: gameusers

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.gameusers` |
| 引擎 | cassandra |
| Primary Key | (authkey) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | account | text | 是 | — |  |
| 2 | addtime | text | 是 | — |  |
| 3 | adsource | text | 是 | — |  |
| 4 | black_account | list<text> | 是 | — |  |
| 5 | email | text | 是 | — |  |
| 6 | focus_account | list<text> | 是 | — |  |
| 7 | follow_account | list<text> | 是 | — |  |
| 8 | gamecount | int | 是 | — |  |
| 9 | headshotpath | text | 是 | — |  |
| 10 | lastactiontime | bigint | 是 | — |  |
| 11 | lastchecktime | bigint | 是 | — |  |
| 12 | memberships | list<text> | 是 | — |  |
| 13 | password | text | 是 | — |  |
| 14 | rank | int | 是 | — |  |
| 15 | renamecount | int | 是 | — |  |
| 16 | showcode | text | 是 | — |  |
| 17 | signindate | text | 是 | — |  |
| 18 | signindays | int | 是 | — |  |
| 19 | site | text | 是 | — |  |
| 20 | siteid | text | 是 | — |  |
| 21 | status | int | 是 | — |  |
| 22 | username | text | 是 | — |  |
| 23 | authkey | text | 是 | — | PK |

### Sample（first row）

```json
{
  "account": "GLHCdS2Crdi",
  "addtime": "2026-04-07 22:12:44",
  "adsource": null,
  "black_account": null,
  "email": "kf2007kf20@gmail.com",
  "focus_account": [
    "1mEHCqpU8J",
    "qICq1sEQMd",
    "nn4nKLdhIh"
  ],
  "follow_account": null,
  "gamecount": 0,
  "headshotpath": null,
  "lastactiontime": 1775571164,
  "lastchecktime": 1783267140,
  "memberships": null,
  "password": null,
  "rank": 1,
  "renamecount": null,
  "showcode": null,
  "signindate": "2026-04-07",
  "signindays": 1,
  "site": "google",
  "siteid": "104392790315426238365",
  "status": 1,
  "username": "Chien David",
  "authkey": "YLa3gLQXBZ"
}
```

## Table: gameusers_banned

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.gameusers_banned` |
| 引擎 | cassandra |
| Primary Key | (authkey) clustering: (addtime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | cost | int | 是 | — |  |
| 2 | deducted | boolean | 是 | — |  |
| 3 | description | text | 是 | — |  |
| 4 | endtime | text | 是 | — |  |
| 5 | username | text | 是 | — |  |
| 6 | addtime | bigint | 是 | — | CK |
| 7 | authkey | text | 是 | — | PK |

### Sample（first row）

```json
{
  "cost": null,
  "deducted": null,
  "description": "\u56E0\u91CD\u8907\u6D17\u7248\u6D89\u5ACC\u6D17Z\u5E63\u7981\u6B62\u4E00\u500B\u6708\u6C34\u6876",
  "endtime": "2026-05-16 23:59:59",
  "username": "\uB0A8\uBBFC\uC815",
  "addtime": 1775708605,
  "authkey": "iVDtns0rCo"
}
```

## Table: gameusers_recommend

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.gameusers_recommend` |
| 引擎 | cassandra |
| Primary Key | (authkey) clustering: (regdate, recommendaccount) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | status | int | 是 | — |  |
| 2 | authkey | text | 是 | — | PK |
| 3 | regdate | text | 是 | — | CK |
| 4 | recommendaccount | text | 是 | — | CK |

### Sample（first row）

```json
{
  "status": 1,
  "authkey": "zfSgXdRtyB",
  "regdate": "2024-01",
  "recommendaccount": "EJwRf9uz8Y9"
}
```

## Table: gameuserviews

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.gameuserviews` |
| 引擎 | cassandra |
| Primary Key | (year) clustering: (datetime, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtype | text | 是 | — |  |
| 2 | lid | text | 是 | — |  |
| 3 | views | int | 是 | — |  |
| 4 | datetime | text | 是 | — | CK |
| 5 | year | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtype": null,
  "lid": null,
  "views": 2,
  "datetime": "2024-01-01",
  "year": "2024",
  "account": "EBZMkyJrWNi"
}
```

## Table: gameuserviewsv2

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.gameuserviewsv2` |
| 引擎 | cassandra |
| Primary Key | (year) clustering: (datetime, gtype, lid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | views | counter | 是 | — |  |
| 2 | datetime | text | 是 | — | CK |
| 3 | year | text | 是 | — | PK |
| 4 | gtype | text | 是 | — | CK |
| 5 | lid | text | 是 | — | CK |
| 6 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "views": 7,
  "datetime": "2025-05-01",
  "year": "2025-05",
  "gtype": "BK",
  "lid": "L3xgCiKfsPE",
  "account": "DLufOBtCSbX"
}
```

## Table: newlottery_banned

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_banned` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (addtime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | description | text | 是 | — |  |
| 2 | endtime | text | 是 | — |  |
| 3 | username | text | 是 | — |  |
| 4 | account | text | 是 | — | PK |
| 5 | addtime | bigint | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_commissions_betpool

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_commissions_betpool` |
| 引擎 | cassandra |
| Primary Key | (gametype) clustering: (gid, btype, pid, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | coin | int | 是 | — |  |
| 3 | gametype | text | 是 | — | PK |
| 4 | gid | text | 是 | — | CK |
| 5 | btype | text | 是 | — | CK |
| 6 | pid | int | 是 | — | CK |
| 7 | id | bigint | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1780290900,
  "coin": 20,
  "gametype": "BS",
  "gid": "H0SjVk0GN0",
  "btype": "moon",
  "pid": 1,
  "id": 95
}
```

## Table: newlottery_notification_messages

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_notification_messages` |
| 引擎 | cassandra |
| Primary Key | (tid) clustering: (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | contents | map<text, text> | 是 | — |  |
| 3 | titles | map<text, text> | 是 | — |  |
| 4 | id | text | 是 | — | CK |
| 5 | tid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1774515553,
  "contents": {
    "zh-TW": "\u76EE\u524D\u50C5\u958B\u653ENBA\u8CFD\u4E8B\u8A66\u73A9\uFF0C\u672A\u4F86\u5C07\u9678\u7E8C\u958B\u653E\u66F4\u591A\u8CFD\u4E8B"
  },
  "titles": {
    "zh-TW": "\u6E2C\u8A66\u7248\u672C\u6D3B\u52D5\u9808\u77E5"
  },
  "id": "rzcewLn9eU",
  "tid": "l9xwOXnaT0"
}
```

## Table: newlottery_notification_topics

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_notification_topics` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | enabled | int | 是 | — |  |
| 2 | icon | text | 是 | — |  |
| 3 | names | map<text, text> | 是 | — |  |
| 4 | updatetime | bigint | 是 | — |  |
| 5 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "enabled": 1,
  "icon": "timer",
  "names": {
    "zh-TW": "\u6D3B\u52D5\u8A0A\u606F"
  },
  "updatetime": 1774515218,
  "id": "l9xwOXnaT0"
}
```

## Table: newlottery_sublogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_sublogs` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (subtime, tradeno) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | autosub | boolean | 是 | — |  |
| 3 | paymode | text | 是 | — |  |
| 4 | paytype | text | 是 | — |  |
| 5 | subendtime | text | 是 | — |  |
| 6 | subid | text | 是 | — |  |
| 7 | account | text | 是 | — | PK |
| 8 | subtime | text | 是 | — | CK |
| 9 | tradeno | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1777533011,
  "autosub": false,
  "paymode": "disposable",
  "paytype": "sale",
  "subendtime": "2026-07-29 23:59:59",
  "subid": "KGPA9N2bU6",
  "account": "zbdigital007",
  "subtime": "2026-04-30 15:10:11",
  "tradeno": "rmbwIiSv3E"
}
```

## Table: newlottery_subplans

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_subplans` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | coin | int | 是 | — |  |
| 2 | enabled | int | 是 | — |  |
| 3 | subdays | int | 是 | — |  |
| 4 | subdesc | text | 是 | — |  |
| 5 | subtype | text | 是 | — |  |
| 6 | updatetime | bigint | 是 | — |  |
| 7 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "coin": 60000,
  "enabled": 1,
  "subdays": 90,
  "subdesc": "\u5B63\u65B9\u6848",
  "subtype": "sale",
  "updatetime": 1776417506,
  "id": "KGPA9N2bU6"
}
```

## Table: newlottery_users

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_users` |
| 引擎 | cassandra |
| Primary Key | (account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | text | 是 | — |  |
| 2 | contact_info | map<text, text> | 是 | — |  |
| 3 | email | text | 是 | — |  |
| 4 | focus_accounts | list<text> | 是 | — |  |
| 5 | headshotpath | text | 是 | — |  |
| 6 | id | text | 是 | — |  |
| 7 | password | text | 是 | — |  |
| 8 | phone | text | 是 | — |  |
| 9 | status | int | 是 | — |  |
| 10 | username | text | 是 | — |  |
| 11 | account | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": "2026-05-29 08:55:07",
  "contact_info": {
    "line": "test1241380"
  },
  "email": "test16@rankball.com",
  "focus_accounts": null,
  "headshotpath": null,
  "id": "khAeetArWkChbG1cRtws",
  "password": "***",
  "phone": "0970000017",
  "status": 1,
  "username": "\u8B1D\u68C9",
  "account": "rankballtest16"
}
```

## Table: newlottery_users_followers

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.newlottery_users_followers` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (followaccount) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | account | text | 是 | — | PK |
| 3 | followaccount | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775029507,
  "account": "zbdigital007",
  "followaccount": "test123"
}
```

## Table: supreme_cycles

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.supreme_cycles` |
| 引擎 | cassandra |
| Primary Key | (gametype) clustering: (lid, cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | articles_likescommentscount_weighting | double | 是 | — |  |
| 2 | endtime | bigint | 是 | — |  |
| 3 | lastup_time | bigint | 是 | — |  |
| 4 | mainwincount_weighting | double | 是 | — |  |
| 5 | pointprofit_weighting | double | 是 | — |  |
| 6 | settlement | int | 是 | — |  |
| 7 | starttime | bigint | 是 | — |  |
| 8 | unlockcount_weighting | double | 是 | — |  |
| 9 | zcoinsprofit_weighting | double | 是 | — |  |
| 10 | gametype | text | 是 | — | PK |
| 11 | lid | text | 是 | — | CK |
| 12 | cid | int | 是 | — | CK |

### Sample（first row）

```json
{
  "articles_likescommentscount_weighting": 0.2,
  "endtime": 1774929600,
  "lastup_time": 1775059231,
  "mainwincount_weighting": 0.15,
  "pointprofit_weighting": 0.3,
  "settlement": 1,
  "starttime": 1761926400,
  "unlockcount_weighting": 0.25,
  "zcoinsprofit_weighting": 0.1,
  "gametype": "TN",
  "lid": "all",
  "cid": 1
}
```

## Table: supreme_records

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.supreme_records` |
| 引擎 | cassandra |
| Primary Key | (gametype) clustering: (lid, cid, type, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | data | text | 是 | — |  |
| 2 | lastup_time | bigint | 是 | — |  |
| 3 | gametype | text | 是 | — | PK |
| 4 | lid | text | 是 | — | CK |
| 5 | cid | int | 是 | — | CK |
| 6 | type | text | 是 | — | CK |
| 7 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "data": "{\u00222026-01-26\u0022:{\u0022LikeCount\u0022:11,\u0022SelfCommentCount\u0022:0,\u0022OthersCommentCount\u0022:3}}",
  "lastup_time": 1769877190,
  "gametype": "TN",
  "lid": "all",
  "cid": 1,
  "type": "ArticlesLikeAndComment",
  "account": "E1uMYDtUgTh"
}
```

## Table: supreme_winners

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.supreme_winners` |
| 引擎 | cassandra |
| Primary Key | (gametype) clustering: (lid, cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | articles_likescommentscount | int | 是 | — |  |
| 2 | articles_likescommentscount_score | int | 是 | — |  |
| 3 | lastup_time | bigint | 是 | — |  |
| 4 | mainwincount | int | 是 | — |  |
| 5 | mainwincount_score | int | 是 | — |  |
| 6 | pointprofit | int | 是 | — |  |
| 7 | pointprofit_score | int | 是 | — |  |
| 8 | total_score | double | 是 | — |  |
| 9 | unlockcount | int | 是 | — |  |
| 10 | unlockcount_score | int | 是 | — |  |
| 11 | username | text | 是 | — |  |
| 12 | zcoinsprofit | int | 是 | — |  |
| 13 | zcoinsprofit_score | int | 是 | — |  |
| 14 | gametype | text | 是 | — | PK |
| 15 | lid | text | 是 | — | CK |
| 16 | cid | int | 是 | — | CK |
| 17 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "articles_likescommentscount": 0,
  "articles_likescommentscount_score": 0,
  "lastup_time": 1775059231,
  "mainwincount": 10,
  "mainwincount_score": 74,
  "pointprofit": 18850,
  "pointprofit_score": 100,
  "total_score": 65.35,
  "unlockcount": 262,
  "unlockcount_score": 97,
  "username": "\u8C93\u738B",
  "zcoinsprofit": 0,
  "zcoinsprofit_score": 0,
  "gametype": "TN",
  "lid": "all",
  "cid": 1,
  "account": "EQZ2VXQOAFB"
}
```

## Table: thirdparties

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.thirdparties` |
| 引擎 | cassandra |
| Primary Key | (authkey) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | authmode | int | 是 | — |  |
| 2 | checkinfos | text | 是 | — |  |
| 3 | enabled | int | 是 | — |  |
| 4 | sitename | text | 是 | — |  |
| 5 | authkey | text | 是 | — | PK |

### Sample（first row）

```json
{
  "authmode": 2,
  "checkinfos": "203.204.205.206,123.124.125.126",
  "enabled": 1,
  "sitename": "3rd_testsite2",
  "authkey": "LX5lUSdRyDk"
}
```

## Table: verifygameusers

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `member.verifygameusers` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (addtime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | bankaccount | text | 是 | — |  |
| 2 | bankaccountname | text | 是 | — |  |
| 3 | bankcode | text | 是 | — |  |
| 4 | branchcode | text | 是 | — |  |
| 5 | email | text | 是 | — |  |
| 6 | idcard1 | text | 是 | — |  |
| 7 | idcard2 | text | 是 | — |  |
| 8 | passbook | text | 是 | — |  |
| 9 | phonenumber | text | 是 | — |  |
| 10 | remark | text | 是 | — |  |
| 11 | status | int | 是 | — |  |
| 12 | updatetime | bigint | 是 | — |  |
| 13 | withdrawpwd | text | 是 | — |  |
| 14 | account | text | 是 | — | PK |
| 15 | addtime | text | 是 | — | CK |

### Sample（first row）

```json
{
  "bankaccount": "00810240724938",
  "bankaccountname": "\u738B\u8B49\u7DAD",
  "bankcode": "700",
  "branchcode": null,
  "email": "wangzhengwei37@gmail.com",
  "idcard1": "https://inplayz.com/sport/img/upload/kogdaaD4cd/B89YOnuJfa.webp",
  "idcard2": "https://inplayz.com/sport/img/upload/kogdaaD4cd/SAj0T0fLcW.webp",
  "passbook": "https://inplayz.com/sport/img/upload/kogdaaD4cd/jWJus4YzOf.webp",
  "phonenumber": "968291316",
  "remark": null,
  "status": 1,
  "updatetime": 1735779984,
  "withdrawpwd": "***",
  "account": "GTHc5QsV2ou",
  "addtime": "2024-12-29 10:58"
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
