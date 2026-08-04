---
aidata_db_sync: true
engine: cassandra
db_name: predict
source: 192.168.55.80:9042
keyspace: predict
table_count: 84
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:26:14.3895108Z
sync_log_id: 32
---

# Tables

## Table: activities_cycles

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.activities_cycles` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (activityevent, cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | enddate | text | 是 | — |  |
| 2 | endtime | text | 是 | — |  |
| 3 | resultcount | int | 是 | — |  |
| 4 | startdate | text | 是 | — |  |
| 5 | starttime | text | 是 | — |  |
| 6 | activityevent | text | 是 | — | CK |
| 7 | site | text | 是 | — | PK |
| 8 | cid | int | 是 | — | CK |

### Sample（first row）

```json
{
  "enddate": "2026-04-30",
  "endtime": "23:59",
  "resultcount": 1,
  "startdate": "2026-04-01",
  "starttime": "00:00",
  "activityevent": "mlb-mainwinstreak",
  "site": "inplayz",
  "cid": 1
}
```

## Table: activities_record

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.activities_record` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (eventname, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | restday | int | 是 | — |  |
| 2 | updatedate | text | 是 | — |  |
| 3 | winbets | list<text> | 是 | — |  |
| 4 | eventname | text | 是 | — | CK |
| 5 | site | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "restday": 0,
  "updatedate": "2026-05-30",
  "winbets": null,
  "eventname": "mlb-mainwinstreak",
  "site": "inplayz",
  "account": "DuEEzIDQmM3"
}
```

## Table: activities_winneraccounts

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.activities_winneraccounts` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (activityevent, cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | predictcount | int | 是 | — |  |
| 2 | profitpoint | int | 是 | — |  |
| 3 | rank | int | 是 | — |  |
| 4 | winpercentage | double | 是 | — |  |
| 5 | activityevent | text | 是 | — | CK |
| 6 | site | text | 是 | — | PK |
| 7 | cid | int | 是 | — | CK |
| 8 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "predictcount": 27,
  "profitpoint": 8890,
  "rank": 2,
  "winpercentage": 70.37,
  "activityevent": "mlb-mainwinstreak",
  "site": "inplayz",
  "cid": 1,
  "account": "EPYTbAZGzxG"
}
```

## Table: betpool_bets

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.betpool_bets` |
| 引擎 | cassandra |
| Primary Key | (gid) clustering: (account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | betoption | text | 是 | — |  |
| 3 | betzcoin | int | 是 | — |  |
| 4 | profitzcoin | int | 是 | — |  |
| 5 | winlose | text | 是 | — |  |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | PK |
| 8 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1754572764,
  "betoption": "2",
  "betzcoin": 100,
  "profitzcoin": 0,
  "winlose": "L",
  "account": "DCTv3Ig44c0",
  "gid": "JvefF9rfFE",
  "id": "AjsjDgP0kS"
}
```

## Table: betpool_games

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.betpool_games` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | basicprofitzcoin | int | 是 | — |  |
| 2 | betoptions | map<text, text> | 是 | — |  |
| 3 | bonusprofitzcoin | int | 是 | — |  |
| 4 | endtime | bigint | 是 | — |  |
| 5 | feedrate | double | 是 | — |  |
| 6 | hot | boolean | 是 | — |  |
| 7 | names | map<text, text> | 是 | — |  |
| 8 | payout | boolean | 是 | — |  |
| 9 | starttime | bigint | 是 | — |  |
| 10 | status | int | 是 | — |  |
| 11 | updatetime | bigint | 是 | — |  |
| 12 | viponly | boolean | 是 | — |  |
| 13 | winresult | text | 是 | — |  |
| 14 | zcoinprice | int | 是 | — |  |
| 15 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "basicprofitzcoin": 5000,
  "betoptions": {
    "1": "{\u0022zh-TW\u0022:\u0022\u4E2D\u83EF\u8D0F1~5\u5206\u0022}",
    "2": "{\u0022zh-TW\u0022:\u0022\u4E2D\u83EF\u8D0F6~10\u5206\u0022}",
    "3": "{\u0022zh-TW\u0022:\u0022\u4E2D\u83EF\u8D0F11~15\u5206\u0022}",
    "4": "{\u0022zh-TW\u0022:\u0022\u4E2D\u83EF\u8D0F16\u5206\u4EE5\u4E0A\u0022}",
    "5": "{\u0022zh-TW\u0022:\u0022\u7D10\u897F\u862D\u8D0F1~5\u5206\u0022}",
    "6": "{\u0022zh-TW\u0022:\u0022\u7D10\u897F\u862D\u8D0F6~10\u5206\u0022}",
    "7": "{\u0022zh-TW\u0022:\u0022\u7D10\u897F\u862D\u8D0F11~15\u5206\u0022}",
    "8": "{\u0022zh-TW\u0022:\u0022\u7D10\u897F\u862D\u8D0F16\u5206\u4EE5\u4E0A\u0022}"
  },
  "bonusprofitzcoin": 0,
  "endtime": 1754712000,
  "feedrate": 0.1,
  "hot": null,
  "names": {
    "zh-TW": "2025FIBA\u7C43\u7403\u4E9E\u6D32\u76C3 8/10(\u65E5) 02:00 \u7D10\u897F\u862D VS \u4E2D\u83EF \u52DD\u5206"
  },
  "payout": true,
  "starttime": 1754542800,
  "status": 1,
  "updatetime": 1754872132,
  "viponly": false,
  "winresult": "8",
  "zcoinprice": 100,
  "id": "JvefF9rfFE"
}
```

## Table: calculatelog

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.calculatelog` |
| 引擎 | cassandra |
| Primary Key | (weekid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | done | int | 是 | — |  |
| 3 | weekdate | text | 是 | — |  |
| 4 | weekid | int | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1711962195,
  "done": 1,
  "weekdate": "2024-03-25",
  "weekid": 23
}
```

## Table: killeraccounts_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_BK` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775462409,
  "avgodd": 0.85,
  "firstweekbetcount": 7,
  "killertype": "super",
  "profitpoint": 4660,
  "secondweekbetcount": 5,
  "totalbetcount": 12,
  "username": "Han",
  "winbetcount": 9,
  "winpercentage": 75,
  "cid": 37,
  "lid": "LxBLrkcB5XE",
  "account": "E9H7n4BHr4A"
}
```

## Table: killeraccounts_BM

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_BM` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: killeraccounts_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_BS` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779091206,
  "avgodd": 0.9,
  "firstweekbetcount": 10,
  "killertype": "normal",
  "profitpoint": 3460,
  "secondweekbetcount": 15,
  "totalbetcount": 25,
  "username": "(\u00B4\u30FB\u03C9\u30FB\u0060)",
  "winbetcount": 15,
  "winpercentage": 60,
  "cid": 38,
  "lid": "LjrDeSvUKa0",
  "account": "E1UtzoWPUlK"
}
```

## Table: killeraccounts_ES

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_ES` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779091210,
  "avgodd": 0.72,
  "firstweekbetcount": 18,
  "killertype": "normal",
  "profitpoint": 3690,
  "secondweekbetcount": 11,
  "totalbetcount": 29,
  "username": "Lenmana",
  "winbetcount": 19,
  "winpercentage": 65.5,
  "cid": 50,
  "lid": "all",
  "account": "EAh4UXHystT"
}
```

## Table: killeraccounts_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_FL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1767600000,
  "avgodd": 0.89,
  "firstweekbetcount": 10,
  "killertype": "normal",
  "profitpoint": 2930,
  "secondweekbetcount": 7,
  "totalbetcount": 17,
  "username": "\u6700\u6703\u8D0F\u7403\u5C31\u662F\u6211",
  "winbetcount": 10,
  "winpercentage": 62.5,
  "cid": 27,
  "lid": "all",
  "account": "E2zmFRG1F0V"
}
```

## Table: killeraccounts_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_HL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779696001,
  "avgodd": 0.83,
  "firstweekbetcount": 12,
  "killertype": "normal",
  "profitpoint": 2990,
  "secondweekbetcount": 7,
  "totalbetcount": 19,
  "username": "Ailsa",
  "winbetcount": 12,
  "winpercentage": 63.2,
  "cid": 55,
  "lid": "all",
  "account": "E1sc8FMXPJo"
}
```

## Table: killeraccounts_PG

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_PG` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779091200,
  "avgodd": 1,
  "firstweekbetcount": 4,
  "killertype": "super",
  "profitpoint": 5279,
  "secondweekbetcount": 9,
  "totalbetcount": 13,
  "username": "\u827E\u8299\u59AE\u723E",
  "winbetcount": 6,
  "winpercentage": 46.2,
  "cid": 53,
  "lid": "all",
  "account": "DuEEzIDQmM3"
}
```

## Table: killeraccounts_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_SC` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779091209,
  "avgodd": 0.67,
  "firstweekbetcount": 17,
  "killertype": "super",
  "profitpoint": 3820,
  "secondweekbetcount": 13,
  "totalbetcount": 30,
  "username": "\uB0A8\uBBFC\uC815",
  "winbetcount": 19,
  "winpercentage": 70.4,
  "cid": 67,
  "lid": "all",
  "account": "EMPsPiVcq0U"
}
```

## Table: killeraccounts_TN

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.killeraccounts_TN` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekbetcount | int | 是 | — |  |
| 4 | killertype | text | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | secondweekbetcount | int | 是 | — |  |
| 7 | totalbetcount | int | 是 | — |  |
| 8 | username | text | 是 | — |  |
| 9 | winbetcount | int | 是 | — |  |
| 10 | winpercentage | double | 是 | — |  |
| 11 | cid | int | 是 | — | CK |
| 12 | lid | text | 是 | — | PK |
| 13 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779091201,
  "avgodd": 0.64,
  "firstweekbetcount": 20,
  "killertype": "super",
  "profitpoint": 3420,
  "secondweekbetcount": 11,
  "totalbetcount": 31,
  "username": "\u5566\u5566\u968A\u9644\u5C6C\u68D2\u7403\u793E",
  "winbetcount": 21,
  "winpercentage": 67.7,
  "cid": 50,
  "lid": "all",
  "account": "EA1dzxDN7kZ"
}
```

## Table: newlottery_betpoolgroups

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_betpoolgroups` |
| 引擎 | cassandra |
| Primary Key | (gametype) clustering: (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | names | map<text, text> | 是 | — |  |
| 2 | status | int | 是 | — |  |
| 3 | gametype | text | 是 | — | PK |
| 4 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "names": {
    "zh-TW": "MLB\u947D\u77F3\u5F69\u6C60"
  },
  "status": 1,
  "gametype": "BS",
  "id": "MH0sLluOKU"
}
```

## Table: newlottery_betpoolgroups_betpools

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_betpoolgroups_betpools` |
| 引擎 | cassandra |
| Primary Key | (gid) clustering: (btype, pid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | basicprofitcoin | int | 是 | — |  |
| 2 | bonusprofitcoin | int | 是 | — |  |
| 3 | endtime | bigint | 是 | — |  |
| 4 | feedrate | double | 是 | — |  |
| 5 | payout_count | int | 是 | — |  |
| 6 | payout_options | map<text, text> | 是 | — |  |
| 7 | payout_type | text | 是 | — |  |
| 8 | starttime | bigint | 是 | — |  |
| 9 | status | int | 是 | — |  |
| 10 | winconditions | map<text, text> | 是 | — |  |
| 11 | btype | text | 是 | — | CK |
| 12 | gid | text | 是 | — | PK |
| 13 | pid | int | 是 | — | CK |

### Sample（first row）

```json
{
  "basicprofitcoin": 6000,
  "bonusprofitcoin": 0,
  "endtime": 1782359940,
  "feedrate": 0.3,
  "payout_count": 10,
  "payout_options": null,
  "payout_type": "avg",
  "starttime": 1779681600,
  "status": 0,
  "winconditions": {
    "mincount": "20",
    "profit": "4000",
    "winpercentage": "60"
  },
  "btype": "moon",
  "gid": "MH0sLluOKU",
  "pid": 1
}
```

## Table: newlottery_betpoolgroups_betpools_winners

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_betpoolgroups_betpools_winners` |
| 引擎 | cassandra |
| Primary Key | (gid) clustering: (btype, pid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | avgodd | double | 是 | — |  |
| 2 | betcount | int | 是 | — |  |
| 3 | losecount | int | 是 | — |  |
| 4 | profitcoin | int | 是 | — |  |
| 5 | profitpoint | int | 是 | — |  |
| 6 | rank | int | 是 | — |  |
| 7 | wincount | int | 是 | — |  |
| 8 | winpercentage | double | 是 | — |  |
| 9 | btype | text | 是 | — | CK |
| 10 | gid | text | 是 | — | PK |
| 11 | pid | int | 是 | — | CK |
| 12 | account | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_championships

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_championships` |
| 引擎 | cassandra |
| Primary Key | (gametype) clustering: (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | closetime | int | 是 | — |  |
| 2 | endtime | bigint | 是 | — |  |
| 3 | gid | text | 是 | — |  |
| 4 | leagues | list<text> | 是 | — |  |
| 5 | names | map<text, text> | 是 | — |  |
| 6 | sell_commission_options | map<text, text> | 是 | — |  |
| 7 | sell_fee_coin | int | 是 | — |  |
| 8 | sell_rank_end | int | 是 | — |  |
| 9 | sell_rank_start | int | 是 | — |  |
| 10 | starttime | bigint | 是 | — |  |
| 11 | status | int | 是 | — |  |
| 12 | ticket_fee_coin | int | 是 | — |  |
| 13 | ticket_fee_point | int | 是 | — |  |
| 14 | gametype | text | 是 | — | PK |
| 15 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "closetime": 30,
  "endtime": 1780891140,
  "gid": "MH0sLluOKU",
  "leagues": [
    "LdjFWtnrrKU"
  ],
  "names": {
    "zh-TW": "MLB\u9326\u6A19\u8CFD0525-0608"
  },
  "sell_commission_options": {
    "moon": "10",
    "season": "10",
    "week": "10"
  },
  "sell_fee_coin": 20,
  "sell_rank_end": 1,
  "sell_rank_start": 1,
  "starttime": 1779681600,
  "status": 1,
  "ticket_fee_coin": 200,
  "ticket_fee_point": 100000,
  "gametype": "BS",
  "id": "5mU4vSagyE"
}
```

## Table: newlottery_predictbets_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_BK` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | cid | text | 是 | — |  |
| 5 | enabled | int | 是 | — |  |
| 6 | gtime | text | 是 | — |  |
| 7 | mainbet | boolean | 是 | — |  |
| 8 | match_a | int | 是 | — |  |
| 9 | match_h | int | 是 | — |  |
| 10 | mode | text | 是 | — |  |
| 11 | odd | double | 是 | — |  |
| 12 | oddtype | text | 是 | — |  |
| 13 | point | int | 是 | — |  |
| 14 | profitpoint | int | 是 | — |  |
| 15 | ratio | int | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | unlockfee | int | 是 | — |  |
| 19 | winloss | text | 是 | — |  |
| 20 | gdate | text | 是 | — | CK |
| 21 | lid | text | 是 | — | PK |
| 22 | gid | text | 是 | — | CK |
| 23 | account | text | 是 | — | CK |
| 24 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_predictbets_BK_locks

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_BK_locks` |
| 引擎 | cassandra |
| Primary Key | (cid) clustering: (account, gdate, lid, gid, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | unlock_accounts | map<text, text> | 是 | — |  |
| 2 | account | text | 是 | — | CK |
| 3 | cid | text | 是 | — | PK |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | CK |
| 6 | gid | text | 是 | — | CK |
| 7 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_predictbets_BK_unlocks_records

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_BK_unlocks_records` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (cid, gdate, lid, gid, unlockaccount, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | unlockfee | int | 是 | — |  |
| 2 | unlocktime | bigint | 是 | — |  |
| 3 | account | text | 是 | — | PK |
| 4 | cid | text | 是 | — | CK |
| 5 | gdate | text | 是 | — | CK |
| 6 | lid | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |
| 8 | unlockaccount | text | 是 | — | CK |
| 9 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_predictbets_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_BS` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | cid | text | 是 | — |  |
| 5 | enabled | int | 是 | — |  |
| 6 | gtime | text | 是 | — |  |
| 7 | mainbet | boolean | 是 | — |  |
| 8 | match_a | int | 是 | — |  |
| 9 | match_h | int | 是 | — |  |
| 10 | mode | text | 是 | — |  |
| 11 | odd | double | 是 | — |  |
| 12 | oddtype | text | 是 | — |  |
| 13 | point | int | 是 | — |  |
| 14 | profitpoint | int | 是 | — |  |
| 15 | ratio | int | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | unlockfee | int | 是 | — |  |
| 19 | winloss | text | 是 | — |  |
| 20 | gdate | text | 是 | — | CK |
| 21 | lid | text | 是 | — | PK |
| 22 | gid | text | 是 | — | CK |
| 23 | account | text | 是 | — | CK |
| 24 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779844938,
  "args": null,
  "canlock": true,
  "cid": "5mU4vSagyE",
  "enabled": 1,
  "gtime": "10:10",
  "mainbet": null,
  "match_a": null,
  "match_h": null,
  "mode": "HA",
  "odd": 0.96,
  "oddtype": "A",
  "point": 1000,
  "profitpoint": -1000,
  "ratio": 100,
  "spread": 2,
  "status": 1,
  "unlockfee": null,
  "winloss": "L",
  "gdate": "2026-05-27",
  "lid": "LdjFWtnrrKU",
  "gid": "GmIhQoAG20q",
  "account": "zbdigital004",
  "id": "2BkCltJWd0"
}
```

## Table: newlottery_predictbets_BS_locks

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_BS_locks` |
| 引擎 | cassandra |
| Primary Key | (cid) clustering: (account, gdate, lid, gid, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | unlock_accounts | map<text, text> | 是 | — |  |
| 2 | account | text | 是 | — | CK |
| 3 | cid | text | 是 | — | PK |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | CK |
| 6 | gid | text | 是 | — | CK |
| 7 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "unlock_accounts": {
    "zbdigital002": "10"
  },
  "account": "zbdigital007",
  "cid": "5mU4vSagyE",
  "gdate": "2026-05-28",
  "lid": "LdjFWtnrrKU",
  "gid": "GAVw66DX5Tk",
  "id": "AbbjlFZX90"
}
```

## Table: newlottery_predictbets_BS_unlocks_records

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_BS_unlocks_records` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (cid, gdate, lid, gid, unlockaccount, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | unlockfee | int | 是 | — |  |
| 2 | unlocktime | bigint | 是 | — |  |
| 3 | account | text | 是 | — | PK |
| 4 | cid | text | 是 | — | CK |
| 5 | gdate | text | 是 | — | CK |
| 6 | lid | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |
| 8 | unlockaccount | text | 是 | — | CK |
| 9 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "unlockfee": 10,
  "unlocktime": 1779868824,
  "account": "zbdigital002",
  "cid": "5mU4vSagyE",
  "gdate": "2026-05-28",
  "lid": "LdjFWtnrrKU",
  "gid": "GAVw66DX5Tk",
  "unlockaccount": "zbdigital007",
  "id": "AbbjlFZX90"
}
```

## Table: newlottery_predictbets_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_SC` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | cid | text | 是 | — |  |
| 5 | enabled | int | 是 | — |  |
| 6 | gtime | text | 是 | — |  |
| 7 | mainbet | boolean | 是 | — |  |
| 8 | match_a | int | 是 | — |  |
| 9 | match_h | int | 是 | — |  |
| 10 | mode | text | 是 | — |  |
| 11 | odd | double | 是 | — |  |
| 12 | oddtype | text | 是 | — |  |
| 13 | point | int | 是 | — |  |
| 14 | profitpoint | int | 是 | — |  |
| 15 | ratio | int | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | unlockfee | int | 是 | — |  |
| 19 | winloss | text | 是 | — |  |
| 20 | gdate | text | 是 | — | CK |
| 21 | lid | text | 是 | — | PK |
| 22 | gid | text | 是 | — | CK |
| 23 | account | text | 是 | — | CK |
| 24 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_predictbets_SC_locks

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_SC_locks` |
| 引擎 | cassandra |
| Primary Key | (cid) clustering: (account, gdate, lid, gid, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | unlock_accounts | map<text, text> | 是 | — |  |
| 2 | account | text | 是 | — | CK |
| 3 | cid | text | 是 | — | PK |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | CK |
| 6 | gid | text | 是 | — | CK |
| 7 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_predictbets_SC_unlocks_records

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_predictbets_SC_unlocks_records` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (cid, gdate, lid, gid, unlockaccount, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | unlockfee | int | 是 | — |  |
| 2 | unlocktime | bigint | 是 | — |  |
| 3 | account | text | 是 | — | PK |
| 4 | cid | text | 是 | — | CK |
| 5 | gdate | text | 是 | — | CK |
| 6 | lid | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |
| 8 | unlockaccount | text | 是 | — | CK |
| 9 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: newlottery_resultlogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.newlottery_resultlogs` |
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
  "addtime": 1779910760241,
  "lid": "LdjFWtnrrKU",
  "status": 1,
  "gdate": "2026-05-28",
  "gtype": "BS",
  "gid": "G67fWLtRSqk"
}
```

## Table: predictbets_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_BK` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775316128,
  "args": null,
  "canlock": true,
  "enabled": 0,
  "gtime": "13:00",
  "mainbet": false,
  "match_a": 0,
  "match_h": 0,
  "mode": "1X2",
  "odd": 1.1,
  "oddtype": "H",
  "point": 1000,
  "profitpoint": -1000,
  "ratio": 0,
  "rollupbets": null,
  "spread": 0,
  "status": 1,
  "strategy_id": 0,
  "usezcoins": false,
  "winloss": "L",
  "gdate": "2026-04-05",
  "lid": "LxBLrkcB5XE",
  "gid": "GBIvRa9ECIE",
  "account": "DCTv3Ig44c0",
  "id": "Fcdm208U2w"
}
```

## Table: predictbets_BM

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_BM` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: predictbets_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_BS` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775360344,
  "args": null,
  "canlock": true,
  "enabled": 0,
  "gtime": "13:00",
  "mainbet": false,
  "match_a": 0,
  "match_h": 0,
  "mode": "1X2",
  "odd": 0.96,
  "oddtype": "A",
  "point": 1000,
  "profitpoint": -1000,
  "ratio": 0,
  "rollupbets": null,
  "spread": 0,
  "status": 1,
  "strategy_id": 0,
  "usezcoins": false,
  "winloss": "L",
  "gdate": "2026-04-05",
  "lid": "LjrDeSvUKa0",
  "gid": "G1CD547E0kO",
  "account": "DLufOBtCSbX",
  "id": "d09OTB5HEe"
}
```

## Table: predictbets_ES

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_ES` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775315737,
  "args": null,
  "canlock": false,
  "enabled": 1,
  "gtime": "09:00",
  "mainbet": false,
  "match_a": 0,
  "match_h": 0,
  "mode": "1X2",
  "odd": 0.48,
  "oddtype": "A",
  "point": 1000,
  "profitpoint": 480,
  "ratio": 0,
  "rollupbets": null,
  "spread": 0,
  "status": 1,
  "strategy_id": 0,
  "usezcoins": false,
  "winloss": "W",
  "gdate": "2026-04-05",
  "lid": "LQd3An81Zck",
  "gid": "G3J7M8iO0Go",
  "account": "DCTv3Ig44c0",
  "id": "hagOYl3bka"
}
```

## Table: predictbets_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_FL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: predictbets_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_HL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775658446,
  "args": null,
  "canlock": false,
  "enabled": 1,
  "gtime": "01:30",
  "mainbet": false,
  "match_a": 0,
  "match_h": 0,
  "mode": "HA",
  "odd": 1.24,
  "oddtype": "A",
  "point": 1000,
  "profitpoint": -1000,
  "ratio": 0,
  "rollupbets": null,
  "spread": 0,
  "status": 1,
  "strategy_id": 0,
  "usezcoins": false,
  "winloss": "L",
  "gdate": "2026-04-09",
  "lid": "LGNhscBhP0e",
  "gid": "G5KvxXiVZrU",
  "account": "DCTv3Ig44c0",
  "id": "Liygz3s1xE"
}
```

## Table: predictbets_PG

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_PG` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775265850,
  "args": null,
  "canlock": false,
  "enabled": 1,
  "gtime": "04:05",
  "mainbet": null,
  "match_a": null,
  "match_h": null,
  "mode": null,
  "odd": 1,
  "oddtype": null,
  "point": 1000,
  "profitpoint": -1000,
  "ratio": null,
  "rollupbets": {
    "BK": "[{\u0022LID\u0022:\u0022LYr9egM00GV\u0022,\u0022GDate\u0022:\u00222026-04-04\u0022,\u0022GTime\u0022:\u002210:00\u0022,\u0022GID\u0022:\u0022GMQjzc4UAhk\u0022,\u0022Mode\u0022:\u0022OU\u0022,\u0022Spread\u0022:233,\u0022Ratio\u0022:100,\u0022OddType\u0022:\u0022O\u0022,\u0022Odd\u0022:0.92,\u0022Status\u0022:0,\u0022WinLoss\u0022:\u0022L\u0022,\u0022Args\u0022:\u0022117,113\u0022}]",
    "BS": "[{\u0022LID\u0022:\u0022LdjFWtnrrKU\u0022,\u0022GDate\u0022:\u00222026-04-05\u0022,\u0022GTime\u0022:\u002204:05\u0022,\u0022GID\u0022:\u0022GBgCGyclda0\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022Spread\u0022:-2,\u0022Ratio\u0022:-100,\u0022OddType\u0022:\u0022H\u0022,\u0022Odd\u0022:0.67,\u0022Status\u0022:0,\u0022WinLoss\u0022:\u0022L\u0022,\u0022Args\u0022:\u00220,11\u0022}]"
  },
  "spread": null,
  "status": 1,
  "strategy_id": 0,
  "usezcoins": false,
  "winloss": "L",
  "gdate": "2026-04-05",
  "lid": "all",
  "gid": "0VZMzM8LTk",
  "account": "ETklu0GKTjm",
  "id": "0VZMzM8LTk"
}
```

## Table: predictbets_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_SC` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1762976798,
  "args": {
    "odd_HA": "{\u0027-1-50\u0027: {\u0027A\u0027: \u00271.14\u0027, \u0027H\u0027: \u00270.71\u0027}}"
  },
  "canlock": false,
  "enabled": 1,
  "gtime": "10:00",
  "mainbet": false,
  "match_a": 0,
  "match_h": 0,
  "mode": "HA",
  "odd": 1.14,
  "oddtype": "A",
  "point": 1000,
  "profitpoint": 570,
  "ratio": -50,
  "rollupbets": null,
  "spread": -1,
  "status": 1,
  "strategy_id": 3,
  "usezcoins": false,
  "winloss": "WR",
  "gdate": "2025-11-14",
  "lid": "LAHtnK5oVN0",
  "gid": "GDKKCqQEVb0",
  "account": "E14ee9KCy6J",
  "id": "bf9zyQJJak"
}
```

## Table: predictbets_TN

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictbets_TN` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, gid, account, id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | canlock | boolean | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | gtime | text | 是 | — |  |
| 6 | mainbet | boolean | 是 | — |  |
| 7 | match_a | int | 是 | — |  |
| 8 | match_h | int | 是 | — |  |
| 9 | mode | text | 是 | — |  |
| 10 | odd | double | 是 | — |  |
| 11 | oddtype | text | 是 | — |  |
| 12 | point | int | 是 | — |  |
| 13 | profitpoint | int | 是 | — |  |
| 14 | ratio | int | 是 | — |  |
| 15 | rollupbets | map<text, text> | 是 | — |  |
| 16 | spread | int | 是 | — |  |
| 17 | status | int | 是 | — |  |
| 18 | strategy_id | int | 是 | — |  |
| 19 | usezcoins | boolean | 是 | — |  |
| 20 | winloss | text | 是 | — |  |
| 21 | gdate | text | 是 | — | CK |
| 22 | lid | text | 是 | — | PK |
| 23 | gid | text | 是 | — | CK |
| 24 | account | text | 是 | — | CK |
| 25 | id | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1775361062,
  "args": null,
  "canlock": false,
  "enabled": 1,
  "gtime": "18:30",
  "mainbet": false,
  "match_a": 0,
  "match_h": 0,
  "mode": "1X2",
  "odd": 1.2,
  "oddtype": "A",
  "point": 1000,
  "profitpoint": 1200,
  "ratio": 0,
  "rollupbets": null,
  "spread": 0,
  "status": 1,
  "strategy_id": 995,
  "usezcoins": false,
  "winloss": "W",
  "gdate": "2026-04-05",
  "lid": "LbJsrHRJaGE",
  "gid": "G0VByxRydXE",
  "account": "E0PZjwSe78Q",
  "id": "xq33GbquN0"
}
```

## Table: predictfilterreports

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictfilterreports` |
| 引擎 | cassandra |
| Primary Key | (reportdate) clustering: (gametype, lid, filtertype, startdate, enddate, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | avgwinodd | double | 是 | — |  |
| 2 | predictcount | int | 是 | — |  |
| 3 | predictwin | int | 是 | — |  |
| 4 | profitpoint | int | 是 | — |  |
| 5 | seq_score | int | 是 | — |  |
| 6 | seq_score_fix | int | 是 | — |  |
| 7 | winlose_detail | list<text> | 是 | — |  |
| 8 | winstreakdays | int | 是 | — |  |
| 9 | gametype | text | 是 | — | CK |
| 10 | reportdate | text | 是 | — | PK |
| 11 | lid | text | 是 | — | CK |
| 12 | filtertype | text | 是 | — | CK |
| 13 | startdate | text | 是 | — | CK |
| 14 | enddate | text | 是 | — | CK |
| 15 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "avgwinodd": 0.63,
  "predictcount": 5,
  "predictwin": 4,
  "profitpoint": 1530,
  "seq_score": 306,
  "seq_score_fix": null,
  "winlose_detail": [
    "W",
    "W",
    "W",
    "-",
    "-",
    "-",
    "-",
    "L",
    "-",
    "-",
    "-",
    "W",
    "-",
    "-",
    "-"
  ],
  "winstreakdays": 0,
  "gametype": "BK",
  "reportdate": "2026-05-28",
  "lid": "L3xgCiKfsPE",
  "filtertype": "1X2",
  "startdate": "2026-04-22",
  "enddate": "2026-05-16",
  "account": "E0bn9jWWg4q"
}
```

## Table: predictfilterreports_mainbet

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictfilterreports_mainbet` |
| 引擎 | cassandra |
| Primary Key | (reportdate) clustering: (gametype, lid, filtertype, startdate, enddate, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | avgwinodd | double | 是 | — |  |
| 2 | predictcount | int | 是 | — |  |
| 3 | predictwin | int | 是 | — |  |
| 4 | profitpoint | int | 是 | — |  |
| 5 | seq_score | int | 是 | — |  |
| 6 | seq_score_fix | int | 是 | — |  |
| 7 | winlose_detail | list<text> | 是 | — |  |
| 8 | winstreakdays | int | 是 | — |  |
| 9 | gametype | text | 是 | — | CK |
| 10 | reportdate | text | 是 | — | PK |
| 11 | lid | text | 是 | — | CK |
| 12 | filtertype | text | 是 | — | CK |
| 13 | startdate | text | 是 | — | CK |
| 14 | enddate | text | 是 | — | CK |
| 15 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "avgwinodd": 0.87,
  "predictcount": 1,
  "predictwin": 1,
  "profitpoint": 870,
  "seq_score": 1305,
  "seq_score_fix": null,
  "winlose_detail": [
    "W",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-",
    "-"
  ],
  "winstreakdays": 1,
  "gametype": "BK",
  "reportdate": "2026-05-28",
  "lid": "L3xgCiKfsPE",
  "filtertype": "main_winstreak",
  "startdate": "2026-04-22",
  "enddate": "2026-04-22",
  "account": "E3G4217fEMo"
}
```

## Table: predictgames_BK_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_BK_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "13:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-01-01",
  "lid": "LxBLrkcB5XE",
  "account": "E24TNymSRvt",
  "gid": "GBqPRxM3r0C"
}
```

## Table: predictgames_BK_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_BK_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "13:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2026-01-01",
  "lid": "LxBLrkcB5XE",
  "account": "E5LcDNKe133",
  "gid": "GvjVI2nfBuU"
}
```

## Table: predictgames_BM_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_BM_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: predictgames_BM_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_BM_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: predictgames_BS_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_BS_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "12:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-02-23",
  "lid": "LjrDeSvUKa0",
  "account": "DLufOBtCSbX",
  "gid": "GGYLLEYohRE"
}
```

## Table: predictgames_BS_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_BS_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "12:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2026-02-21",
  "lid": "LjrDeSvUKa0",
  "account": "EIE8xLpxVoS",
  "gid": "G4ec0PmpPd0"
}
```

## Table: predictgames_ES_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_ES_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "19:30",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-01-04",
  "lid": "LQd3An81Zck",
  "account": "ET8sSGhnv4m",
  "gid": "GCOR93cuNEG"
}
```

## Table: predictgames_ES_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_ES_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "21:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2026-01-02",
  "lid": "LQd3An81Zck",
  "account": "E3DG3KUdmZ9",
  "gid": "Gp6JVxImnuU"
}
```

## Table: predictgames_FL_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_FL_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "09:10",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-01-05",
  "lid": "LNFgm3ea42E",
  "account": "DLufOBtCSbX",
  "gid": "GNW2klreMQk"
}
```

## Table: predictgames_FL_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_FL_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "09:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2026-01-04",
  "lid": "LNFgm3ea42E",
  "account": "E1UtzoWPUlK",
  "gid": "G7Gmw8HL3Uk"
}
```

## Table: predictgames_HL_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_HL_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "02:30",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-01-03",
  "lid": "LGNhscBhP0e",
  "account": "E0GQtMYAWQu",
  "gid": "GB4qdVX8NN0"
}
```

## Table: predictgames_HL_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_HL_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "02:30",
  "unlock_accounts": {
    "EHjRfjTdRzI": "2026-01-03 01:22:00",
    "ESFDYj1Vk4z": "2026-01-03 00:46:00",
    "EU5s4oViDDm": "2026-01-03 00:56:00"
  },
  "unlock_rb_accounts": null,
  "gdate": "2026-01-03",
  "lid": "LGNhscBhP0e",
  "account": "E0Zpgs5hAes",
  "gid": "GgQJzA3EzLk"
}
```

## Table: predictgames_PG_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_PG_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "10:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-01-01",
  "lid": "all",
  "account": "DuEEzIDQmM3",
  "gid": "4bJmnwVEEG"
}
```

## Table: predictgames_PG_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_PG_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "09:00",
  "unlock_accounts": {
    "GaehMgLFjUo": "2025-12-31 15:49:07"
  },
  "unlock_rb_accounts": null,
  "gdate": "2026-01-01",
  "lid": "all",
  "account": "E1uMYDtUgTh",
  "gid": "HUj71k2ToU"
}
```

## Table: predictgames_SC_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_SC_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "05:30",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-01-16",
  "lid": "L4hBNMd9T5E",
  "account": "E32ccdoDSJd",
  "gid": "GA1Wn3xtsME"
}
```

## Table: predictgames_SC_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_SC_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "07:30",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2026-01-11",
  "lid": "L4hBNMd9T5E",
  "account": "E4MuL9P6cS3",
  "gid": "GYTRBmhhNNk"
}
```

## Table: predictgames_TN_lock_2025

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_TN_lock_2025` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "09:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2025-01-01",
  "lid": "LbJsrHRJaGE",
  "account": "Ekj9aXZmhqD",
  "gid": "GLOq2mL8roU"
}
```

## Table: predictgames_TN_lock_2026

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predictgames_TN_lock_2026` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (gdate, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | gtime | text | 是 | — |  |
| 2 | unlock_accounts | map<text, text> | 是 | — |  |
| 3 | unlock_rb_accounts | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | lid | text | 是 | — | PK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "gtime": "08:00",
  "unlock_accounts": null,
  "unlock_rb_accounts": null,
  "gdate": "2026-01-02",
  "lid": "LbJsrHRJaGE",
  "account": "DCTv3Ig44c0",
  "gid": "G4gC7Y7kUES"
}
```

## Table: predict_robot_1

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.predict_robot_1` |
| 引擎 | cassandra |
| Primary Key | (strategy_id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | enable | int | 是 | — |  |
| 2 | repeat | int | 是 | — |  |
| 3 | target | map<text, frozen<list<text>>> | 是 | — |  |
| 4 | strategy_id | int | 是 | — | PK |

### Sample（first row）

```json
{
  "enable": 1,
  "repeat": 1,
  "target": {
    "BS": [
      "all"
    ]
  },
  "strategy_id": 23
}
```

## Table: resultlogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.resultlogs` |
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
  "addtime": 1779931283086,
  "lid": "LfIat3iWVEG",
  "status": 1,
  "gdate": "2026-05-28",
  "gtype": "BK",
  "gid": "GGO0h9MQtsk"
}
```

## Table: settings_killer

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer` |
| 引擎 | cassandra |
| Primary Key | (gametype) clustering: (lid, killertype) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofitpoint | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | gametype | text | 是 | — | PK |
| 9 | lid | text | 是 | — | CK |
| 10 | killertype | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1689227292,
  "avgodd": 0.75,
  "firstweekmincount": 5,
  "mincount": 28,
  "minprofitpoint": 20,
  "minwinpercentage": 60,
  "secondweekmincount": 5,
  "gametype": "BS",
  "lid": "LJ8raQHZPXU",
  "killertype": "normal"
}
```

## Table: settings_killer_conditions_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_BK` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1774049353,
  "avgodd": 0.75,
  "firstweekmincount": 4,
  "mincount": 12,
  "minprofits": 0,
  "minwinpercentage": 60,
  "secondweekmincount": 4,
  "superminwinpercentage": 66.6,
  "cid": 37,
  "lid": "LxBLrkcB5XE"
}
```

## Table: settings_killer_conditions_BM

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_BM` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: settings_killer_conditions_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_BS` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803340,
  "avgodd": 0.6,
  "firstweekmincount": 7,
  "mincount": 21,
  "minprofits": 0,
  "minwinpercentage": 60,
  "secondweekmincount": 7,
  "superminwinpercentage": 66.6,
  "cid": 39,
  "lid": "LjrDeSvUKa0"
}
```

## Table: settings_killer_conditions_ES

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_ES` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803160,
  "avgodd": 0.6,
  "firstweekmincount": 7,
  "mincount": 21,
  "minprofits": 0,
  "minwinpercentage": 60,
  "secondweekmincount": 7,
  "superminwinpercentage": 66.6,
  "cid": 51,
  "lid": "all"
}
```

## Table: settings_killer_conditions_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_FL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1767399359,
  "avgodd": 0.6,
  "firstweekmincount": 3,
  "mincount": 10,
  "minprofits": 0,
  "minwinpercentage": 60,
  "secondweekmincount": 3,
  "superminwinpercentage": 66.6,
  "cid": 28,
  "lid": "all"
}
```

## Table: settings_killer_conditions_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_HL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1779581098,
  "avgodd": 0.6,
  "firstweekmincount": 3,
  "mincount": 10,
  "minprofits": 0,
  "minwinpercentage": 60,
  "secondweekmincount": 3,
  "superminwinpercentage": 66.6,
  "cid": 56,
  "lid": "all"
}
```

## Table: settings_killer_conditions_PG

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_PG` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803093,
  "avgodd": 1,
  "firstweekmincount": 4,
  "mincount": 10,
  "minprofits": 1000,
  "minwinpercentage": 15,
  "secondweekmincount": 4,
  "superminwinpercentage": 40,
  "cid": 54,
  "lid": "all"
}
```

## Table: settings_killer_conditions_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_SC` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803121,
  "avgodd": 0.6,
  "firstweekmincount": 9,
  "mincount": 28,
  "minprofits": 0,
  "minwinpercentage": 60,
  "secondweekmincount": 9,
  "superminwinpercentage": 66.6,
  "cid": 68,
  "lid": "all"
}
```

## Table: settings_killer_conditions_TN

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_conditions_TN` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | avgodd | double | 是 | — |  |
| 3 | firstweekmincount | int | 是 | — |  |
| 4 | mincount | int | 是 | — |  |
| 5 | minprofits | int | 是 | — |  |
| 6 | minwinpercentage | double | 是 | — |  |
| 7 | secondweekmincount | int | 是 | — |  |
| 8 | superminwinpercentage | double | 是 | — |  |
| 9 | cid | int | 是 | — | CK |
| 10 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1779151222,
  "avgodd": 0.6,
  "firstweekmincount": 9,
  "mincount": 28,
  "minprofits": 0,
  "minwinpercentage": 60,
  "secondweekmincount": 9,
  "superminwinpercentage": 66.6,
  "cid": 51,
  "lid": "all"
}
```

## Table: settings_killer_cycle_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_BK` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1775466009,
  "enddate": "2026-04-06",
  "endtime": "11:59",
  "payout": true,
  "resultcount": 1,
  "startdate": "2026-03-23",
  "starttime": "12:00",
  "cid": 37,
  "lid": "LxBLrkcB5XE"
}
```

## Table: settings_killer_cycle_BM

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_BM` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: settings_killer_cycle_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_BS` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803340,
  "enddate": "2026-06-01",
  "endtime": "11:59",
  "payout": null,
  "resultcount": 0,
  "startdate": "2026-05-18",
  "starttime": "12:00",
  "cid": 39,
  "lid": "LjrDeSvUKa0"
}
```

## Table: settings_killer_cycle_ES

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_ES` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803159,
  "enddate": "2026-06-01",
  "endtime": "11:59",
  "payout": null,
  "resultcount": 0,
  "startdate": "2026-05-18",
  "starttime": "12:00",
  "cid": 51,
  "lid": "all"
}
```

## Table: settings_killer_cycle_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_FL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1768813207,
  "enddate": "2026-01-19",
  "endtime": "11:59",
  "payout": true,
  "resultcount": 1,
  "startdate": "2026-01-05",
  "starttime": "12:00",
  "cid": 28,
  "lid": "all"
}
```

## Table: settings_killer_cycle_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_HL` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1779581098,
  "enddate": "2026-06-08",
  "endtime": "11:59",
  "payout": null,
  "resultcount": 0,
  "startdate": "2026-05-25",
  "starttime": "12:00",
  "cid": 56,
  "lid": "all"
}
```

## Table: settings_killer_cycle_PG

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_PG` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803093,
  "enddate": "2026-06-01",
  "endtime": "11:59",
  "payout": null,
  "resultcount": 0,
  "startdate": "2026-05-18",
  "starttime": "12:00",
  "cid": 54,
  "lid": "all"
}
```

## Table: settings_killer_cycle_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_SC` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803121,
  "enddate": "2026-06-01",
  "endtime": "11:59",
  "payout": null,
  "resultcount": 0,
  "startdate": "2026-05-18",
  "starttime": "12:00",
  "cid": 68,
  "lid": "all"
}
```

## Table: settings_killer_cycle_TN

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_killer_cycle_TN` |
| 引擎 | cassandra |
| Primary Key | (lid) clustering: (cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | enddate | text | 是 | — |  |
| 3 | endtime | text | 是 | — |  |
| 4 | payout | boolean | 是 | — |  |
| 5 | resultcount | int | 是 | — |  |
| 6 | startdate | text | 是 | — |  |
| 7 | starttime | text | 是 | — |  |
| 8 | cid | int | 是 | — | CK |
| 9 | lid | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1778803191,
  "enddate": "2026-06-01",
  "endtime": "11:59",
  "payout": null,
  "resultcount": 0,
  "startdate": "2026-05-18",
  "starttime": "12:00",
  "cid": 51,
  "lid": "all"
}
```

## Table: settings_league

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_league` |
| 引擎 | cassandra |
| Primary Key | (gametype) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | classified | boolean | 是 | — |  |
| 3 | enabled | int | 是 | — |  |
| 4 | lids | list<text> | 是 | — |  |
| 5 | gametype | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1712627961,
  "classified": true,
  "enabled": 1,
  "lids": [
    "all"
  ],
  "gametype": "PG"
}
```

## Table: settings_playmode

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.settings_playmode` |
| 引擎 | cassandra |
| Primary Key | (gametype) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | playmodes | list<text> | 是 | — |  |
| 3 | gametype | text | 是 | — | PK |

### Sample（first row）

```json
{
  "addtime": 1712627922,
  "playmodes": null,
  "gametype": "PG"
}
```

## Table: strategy_bet_log

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.strategy_bet_log` |
| 引擎 | cassandra |
| Primary Key | (strategy_id) clustering: (game_type, date, mode, gid, account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | args | map<text, text> | 是 | — |  |
| 3 | oddtype | text | 是 | — |  |
| 4 | result | int | 是 | — |  |
| 5 | spread | text | 是 | — |  |
| 6 | game_type | text | 是 | — | CK |
| 7 | strategy_id | int | 是 | — | PK |
| 8 | date | text | 是 | — | CK |
| 9 | mode | text | 是 | — | CK |
| 10 | gid | text | 是 | — | CK |
| 11 | account | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": null,
  "args": null,
  "oddtype": null,
  "result": -1000,
  "spread": null,
  "game_type": "BS",
  "strategy_id": 5,
  "date": "2025-03-18",
  "mode": "HA",
  "gid": "GzDfaZBsqWU",
  "account": "E14ee9KCy6J"
}
```

## Table: strategy_bet_log_test2

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.strategy_bet_log_test2` |
| 引擎 | cassandra |
| Primary Key | (strategy_id) clustering: (game_type, date, mode, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | account | text | 是 | — |  |
| 2 | addtime | bigint | 是 | — |  |
| 3 | args | map<text, text> | 是 | — |  |
| 4 | oddtype | text | 是 | — |  |
| 5 | result | int | 是 | — |  |
| 6 | spread | text | 是 | — |  |
| 7 | game_type | text | 是 | — | CK |
| 8 | strategy_id | int | 是 | — | PK |
| 9 | date | text | 是 | — | CK |
| 10 | mode | text | 是 | — | CK |
| 11 | gid | text | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: weeklyreport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `predict.weeklyreport` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (weekid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | reports | map<text, text> | 是 | — |  |
| 3 | weekdate | text | 是 | — |  |
| 4 | account | text | 是 | — | PK |
| 5 | weekid | int | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1739767849,
  "reports": {
    "bets": "1",
    "loss": "1",
    "profitpoint": "-1000",
    "win": "0"
  },
  "weekdate": "2025-02-10",
  "account": "EJFvJ1dGuwa",
  "weekid": 69
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
