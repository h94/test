---
aidata_db_sync: true
engine: cassandra
db_name: payment
source: 192.168.55.80:9042
keyspace: payment
table_count: 17
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:23:48.0132504Z
sync_log_id: 29
---

# Tables

## Table: paymethods_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.paymethods_sport` |
| 引擎 | cassandra |
| Primary Key | (paytype) clustering: (mode) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | enabled | int | 是 | — |  |
| 2 | names | map<text, text> | 是 | — |  |
| 3 | mode | text | 是 | — | CK |
| 4 | paytype | text | 是 | — | PK |

### Sample（first row）

```json
{
  "enabled": 1,
  "names": {
    "en-US": "Supermarket Code",
    "zh-CN": "\u8D85\u5546\u4EE3\u7801",
    "zh-TW": "\u8D85\u5546\u4EE3\u78BC"
  },
  "mode": "disposable",
  "paytype": "CVS"
}
```

## Table: products_activity

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.products_activity` |
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
    "zh-TW": "\u53F0\u5E635000\u5143\u6574"
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
| 完整名稱 | `payment.products_activity_redeem_logs` |
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
  "addtime": 1755091757,
  "status": 1,
  "updatetime": 1755478396,
  "activityevent": "cpbl-mainwinstreak",
  "site": "inplayz",
  "account": "E2zmFRG1F0V",
  "id": "j9ZF03MpNE",
  "pid": "mWwY4QD1s0"
}
```

## Table: rechargeplans_newlottery

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.rechargeplans_newlottery` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | amount | int | 是 | — |  |
| 2 | coin | int | 是 | — |  |
| 3 | currency | text | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | endtime | bigint | 是 | — |  |
| 6 | lastupdatetime | bigint | 是 | — |  |
| 7 | starttime | bigint | 是 | — |  |
| 8 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "amount": 10000,
  "coin": 100000,
  "currency": "TWD",
  "enabled": 0,
  "endtime": 2556028799,
  "lastupdatetime": 1777535555,
  "starttime": 1772726400,
  "id": "jybh1J8Xka"
}
```

## Table: reports_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.reports_sport` |
| 引擎 | cassandra |
| Primary Key | (year) clustering: (month) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | finishing | boolean | 是 | — |  |
| 2 | leaguesunlock | map<text, text> | 是 | — |  |
| 3 | shareamount | int | 是 | — |  |
| 4 | totalincome | int | 是 | — |  |
| 5 | unlockcount | int | 是 | — |  |
| 6 | month | int | 是 | — | CK |
| 7 | year | int | 是 | — | PK |

### Sample（first row）

```json
{
  "finishing": true,
  "leaguesunlock": {
    "BK": "[{\u0022LID\u0022:\u0022LHSP3MLU160\u0022,\u0022UnlockCount\u0022:9233},{\u0022LID\u0022:\u0022L3xgCiKfsPE\u0022,\u0022UnlockCount\u0022:2735},{\u0022LID\u0022:\u0022LxBLrkcB5XE\u0022,\u0022UnlockCount\u0022:13176},{\u0022LID\u0022:\u0022LYr9egM00GV\u0022,\u0022UnlockCount\u0022:75880},{\u0022LID\u0022:\u0022LfIat3iWVEG\u0022,\u0022UnlockCount\u0022:0},{\u0022LID\u0022:\u0022LA98lnM9NUk\u0022,\u0022UnlockCount\u0022:12329}]",
    "BS": "[{\u0022LID\u0022:\u0022L8UD4CDxjgE\u0022,\u0022UnlockCount\u0022:0},{\u0022LID\u0022:\u0022LdjFWtnrrKU\u0022,\u0022UnlockCount\u0022:0},{\u0022LID\u0022:\u0022LJ8raQHZPXU\u0022,\u0022UnlockCount\u0022:0},{\u0022LID\u0022:\u0022LjrDeSvUKa0\u0022,\u0022UnlockCount\u0022:0},{\u0022LID\u0022:\u0022LkKKYz2tO20\u0022,\u0022UnlockCount\u0022:0}]",
    "ES": "[{\u0022LID\u0022:\u0022all\u0022,\u0022UnlockCount\u0022:3413}]",
    "FL": "[{\u0022LID\u0022:\u0022all\u0022,\u0022UnlockCount\u0022:3269}]",
    "HL": "[{\u0022LID\u0022:\u0022all\u0022,\u0022UnlockCount\u0022:25951}]",
    "PG": "[{\u0022LID\u0022:\u0022all\u0022,\u0022UnlockCount\u0022:251}]",
    "SC": "[{\u0022LID\u0022:\u0022all\u0022,\u0022UnlockCount\u0022:38999}]",
    "TN": "[{\u0022LID\u0022:\u0022all\u0022,\u0022UnlockCount\u0022:6029}]"
  },
  "shareamount": 125656,
  "totalincome": 240489,
  "unlockcount": 191265,
  "month": 1,
  "year": 2025
}
```

## Table: reports_sport_recommend

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.reports_sport_recommend` |
| 引擎 | cassandra |
| Primary Key | (year) clustering: (month) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | finishing | boolean | 是 | — |  |
| 2 | shareamount | int | 是 | — |  |
| 3 | totalregcount | int | 是 | — |  |
| 4 | totalsubcount | int | 是 | — |  |
| 5 | totaltransactionamount | int | 是 | — |  |
| 6 | month | int | 是 | — | CK |
| 7 | year | int | 是 | — | PK |

### Sample（first row）

```json
{
  "finishing": true,
  "shareamount": 0,
  "totalregcount": 0,
  "totalsubcount": 0,
  "totaltransactionamount": 0,
  "month": 1,
  "year": 2025
}
```

## Table: shakehandlogs_service_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.shakehandlogs_service_sport` |
| 引擎 | cassandra |
| Primary Key | (date) clustering: (account, addtime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | actiontype | text | 是 | — |  |
| 2 | req | text | 是 | — |  |
| 3 | resp | text | 是 | — |  |
| 4 | account | text | 是 | — | CK |
| 5 | date | text | 是 | — | PK |
| 6 | addtime | bigint | 是 | — | CK |

### Sample（first row）

```json
{
  "actiontype": "create ecpay creditcard period order",
  "req": "{\u0022Site\u0022:\u0022sport\u0022,\u0022Account\u0022:\u0022EuY0UnbktUQ\u0022,\u0022AccountToken\u0022:\u0022qICq1sEQMd\u0022,\u0022SubID\u0022:\u00223\u0022,\u0022PayType\u0022:\u0022CreditCard\u0022,\u0022Language\u0022:\u0022zh-TW\u0022}",
  "resp": "{\u0022PeriodAmount\u0022:225,\u0022PeriodType\u0022:\u0022D\u0022,\u0022Frequency\u0022:3,\u0022ExecTimes\u0022:999,\u0022PeriodReturnURL\u0022:\u0022https://inplayz.com/apiservice/api/system/verify/payment/ecpay/period/subscription\u0022,\u0022Url\u0022:\u0022https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5\u0022,\u0022MerchantID\u0022:\u00223354328\u0022,\u0022MerchantTradeNo\u0022:\u0022pqXvg8b11U\u0022,\u0022MerchantTradeDate\u0022:\u00222024/07/19 23:04:30\u0022,\u0022PaymentType\u0022:\u0022aio\u0022,\u0022TotalAmount\u0022:225,\u0022TradeDesc\u0022:\u0022\u8A02\u95B1\u4E09\u5929225\u65B9\u6848\u0022,\u0022ItemName\u0022:\u0022\u8A02\u95B1\u4E09\u5929225\u65B9\u6848\u0022,\u0022ReturnURL\u0022:\u0022https://inplayz.com/apiservice/api/system/verify/payment/ecpay/subscription\u0022,\u0022ChoosePayment\u0022:\u0022Credit\u0022,\u0022CheckMacValue\u0022:\u0022A8A11C370DFE7B20FE91ED5DE4701CF4FC1D82B68018C63FFBB32FC53249A83B\u0022,\u0022EncryptType\u0022:1,\u0022StoreID\u0022:\u0022sport\u0022,\u0022NeedExtraPaidInfo\u0022:\u0022Y\u0022,\u0022CustomField1\u0022:\u00223-EuY0UnbktUQ\u0022,\u0022CustomField2\u0022:\u0022qICq1sEQMd\u0022,\u0022CustomField3\u0022:\u00222024/07/19 23:04:30\u0022,\u0022CustomField4\u0022:null,\u0022Language\u0022:\u0022\u0022}",
  "account": "EuY0UnbktUQ",
  "date": "2024-07-19",
  "addtime": 1721401470281
}
```

## Table: shakehandlogs_site_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.shakehandlogs_site_sport` |
| 引擎 | cassandra |
| Primary Key | (date) clustering: (account, addtime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | actiontype | text | 是 | — |  |
| 2 | req | text | 是 | — |  |
| 3 | result | text | 是 | — |  |
| 4 | account | text | 是 | — | CK |
| 5 | date | text | 是 | — | PK |
| 6 | addtime | bigint | 是 | — | CK |

### Sample（first row）

```json
{
  "actiontype": "update trade order",
  "req": "{\u0022Year\u0022:\u00222024\u0022,\u0022DateTime\u0022:\u00222024-07-19 23:04:30\u0022,\u0022Account\u0022:\u0022EuY0UnbktUQ\u0022,\u0022OrderID\u0022:\u0022pqXvg8b11U\u0022,\u0022SubID\u0022:\u00223\u0022,\u0022Amount\u0022:0,\u0022PayType\u0022:\u0022CreditCard\u0022,\u0022PayMethod\u0022:\u0022period\u0022,\u0022Card4No\u0022:\u00225705\u0022,\u0022Status\u0022:1,\u0022ThirdPartyName\u0022:null,\u0022FirstDateTime\u0022:null,\u0022ThirdPartyOrderID\u0022:\u00222407192304300219\u0022,\u0022FirstOrderID\u0022:null,\u0022PeriodSuccessCount\u0022:1,\u0022LastUpdateTime\u0022:0}",
  "result": "update success",
  "account": "175.99.72.1",
  "date": "2024-07-19",
  "addtime": 1721401610934
}
```

## Table: sharereports_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.sharereports_sport` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (year, month, gametype, league) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | eventunlock | int | 是 | — |  |
| 2 | normalunlock | int | 是 | — |  |
| 3 | payout | boolean | 是 | — |  |
| 4 | shareamount | int | 是 | — |  |
| 5 | sharezcoin | int | 是 | — |  |
| 6 | superunlock | int | 是 | — |  |
| 7 | totalunlock | int | 是 | — |  |
| 8 | updatetime | bigint | 是 | — |  |
| 9 | account | text | 是 | — | PK |
| 10 | year | int | 是 | — | CK |
| 11 | month | int | 是 | — | CK |
| 12 | gametype | text | 是 | — | CK |
| 13 | league | text | 是 | — | CK |

### Sample（first row）

```json
{
  "eventunlock": 1,
  "normalunlock": 0,
  "payout": true,
  "shareamount": 0,
  "sharezcoin": 0,
  "superunlock": 0,
  "totalunlock": 1,
  "updatetime": 1749060449,
  "account": "EpPMaXrgWPW",
  "year": 2025,
  "month": 5,
  "gametype": "BS",
  "league": "LjrDeSvUKa0"
}
```

## Table: sharereports_sport_recommend

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.sharereports_sport_recommend` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (year, month) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | accountregistercount | int | 是 | — |  |
| 2 | shareamount | int | 是 | — |  |
| 3 | sharepercentage | double | 是 | — |  |
| 4 | subcount | int | 是 | — |  |
| 5 | totaltransactionamount | int | 是 | — |  |
| 6 | transactiondetails | text | 是 | — |  |
| 7 | updatetime | bigint | 是 | — |  |
| 8 | account | text | 是 | — | PK |
| 9 | year | int | 是 | — | CK |
| 10 | month | int | 是 | — | CK |

### Sample（first row）

```json
{
  "accountregistercount": 1,
  "shareamount": 0,
  "sharepercentage": 0,
  "subcount": 0,
  "totaltransactionamount": 0,
  "transactiondetails": "",
  "updatetime": 1754330782,
  "account": "GDC632eMdpt",
  "year": 2025,
  "month": 7
}
```

## Table: subplans_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.subplans_sport` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | amount | int | 是 | — |  |
| 2 | currency | text | 是 | — |  |
| 3 | effectivelength | int | 是 | — |  |
| 4 | enabled | int | 是 | — |  |
| 5 | enddate | text | 是 | — |  |
| 6 | lastupdatetime | bigint | 是 | — |  |
| 7 | names | map<text, text> | 是 | — |  |
| 8 | startdate | text | 是 | — |  |
| 9 | subdesc | map<text, text> | 是 | — |  |
| 10 | sublimit | boolean | 是 | — |  |
| 11 | subtype | text | 是 | — |  |
| 12 | supportmethods | text | 是 | — |  |
| 13 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "amount": 0,
  "currency": "TWD",
  "effectivelength": 3,
  "enabled": 0,
  "enddate": "2024-12-31",
  "lastupdatetime": 1704186733,
  "names": {
    "en-US": "Join the free three-day subscription event",
    "zh-CN": "\u52A0\u5165\u9001\u4E09\u5929\u514D\u8D39\u8BA2\u9605\u6D3B\u52A8",
    "zh-TW": "\u52A0\u5165\u9001\u4E09\u5929\u514D\u8CBB\u8A02\u95B1\u6D3B\u52D5"
  },
  "startdate": "2024-01-01",
  "subdesc": {
    "en-US": "Join the free three-day subscription event",
    "zh-CN": "\u52A0\u5165\u9001\u4E09\u5929\u514D\u8D39\u8BA2\u9605\u6D3B\u52A8",
    "zh-TW": "\u52A0\u5165\u9001\u4E09\u5929\u514D\u8CBB\u8A02\u95B1\u6D3B\u52D5"
  },
  "sublimit": false,
  "subtype": "D",
  "supportmethods": "[{\u0022PayType\u0022:\u0022Promation\u0022,\u0022Mode\u0022:\u0022disposable\u0022,\u0022Enabled\u0022:1,\u0022Names\u0022:{\u0022en-US\u0022:\u0022Official offer\u0022,\u0022zh-CN\u0022:\u0022\u5B98\u65B9\u4F18\u60E0\u0022,\u0022zh-TW\u0022:\u0022\u5B98\u65B9\u512A\u60E0\u0022}}]",
  "id": "6"
}
```

## Table: subplans_stock

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.subplans_stock` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | amount | int | 是 | — |  |
| 2 | enabled | int | 是 | — |  |
| 3 | enddate | text | 是 | — |  |
| 4 | name | text | 是 | — |  |
| 5 | startdate | text | 是 | — |  |
| 6 | subdesc | text | 是 | — |  |
| 7 | subrank | int | 是 | — |  |
| 8 | subtitle | text | 是 | — |  |
| 9 | subtype | text | 是 | — |  |
| 10 | subtypecount | int | 是 | — |  |
| 11 | id | text | 是 | — | PK |

### Sample（first row）

```json
{
  "amount": 299,
  "enabled": 2,
  "enddate": "2077-12-30",
  "name": "\u9AD8\u7D1A\u6703\u54E1\u5347\u7D1A\uFF0C25\u65E5\u4EE5\u4E0A\u5DEE\u984D\u65B9\u6848",
  "startdate": "2022-10-01",
  "subdesc": "\u4EAB\u7528\u5168\u90E8\u9078\u80A1\u7B56\u7565\u53CA\u53C3\u6578-\u7121\u9650\u5236\u7684\u5238\u5546\u641C\u529F\u80FD-\u5238\u5546\u641C\u5C0B\u529F\u80FD\u65E5\u671F\u9650\u523614\u65E5\u5167-\u7121\u9650\u5236\u7684\u5238\u5546\u7FA4\u7D44\u53CA\u5206\u884C-\u7121\u9650\u5236\u7684\u81EA\u9078\u80A1\u7FA4\u7D44\u53CA\u80A1\u7968-\u7121\u9650\u5236\u7684\u56DE\u6E2C\u6B21\u6578-\u7121\u9650\u5236\u7684\u56DE\u6E2C\u65E5\u671F-\u958B\u653E\u4F7F\u7528\u81EA\u52D5\u56DE\u6E2C\u529F\u80FD-\u958B\u653E\u63A8\u64AD\u529F\u80FD-\u6BCF\u7D44\u5E33\u865F\u53EA\u80FD\u5728\u5169\u90E8\u8A2D\u5099\u4E0A\u4FDD\u6301\u767B\u5165",
  "subrank": 3,
  "subtitle": "\u6708\u8A02\u5236",
  "subtype": "M",
  "subtypecount": 1,
  "id": "6"
}
```

## Table: tradeorder_newlottery

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.tradeorder_newlottery` |
| 引擎 | cassandra |
| Primary Key | (year) clustering: (datetime, account, orderid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | amount | int | 是 | — |  |
| 2 | card4no | text | 是 | — |  |
| 3 | firstdatetime | text | 是 | — |  |
| 4 | firstorderid | text | 是 | — |  |
| 5 | lastupdatetime | bigint | 是 | — |  |
| 6 | paymethod | text | 是 | — |  |
| 7 | paytype | text | 是 | — |  |
| 8 | periodsuccesscount | int | 是 | — |  |
| 9 | status | int | 是 | — |  |
| 10 | subid | text | 是 | — |  |
| 11 | thirdpartyname | text | 是 | — |  |
| 12 | thirdpartyorderid | text | 是 | — |  |
| 13 | datetime | text | 是 | — | CK |
| 14 | year | text | 是 | — | PK |
| 15 | account | text | 是 | — | CK |
| 16 | orderid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "amount": 600,
  "card4no": null,
  "firstdatetime": null,
  "firstorderid": null,
  "lastupdatetime": 1777531718,
  "paymethod": "disposable",
  "paytype": "Transfer",
  "periodsuccesscount": null,
  "status": 1,
  "subid": "60000",
  "thirdpartyname": null,
  "thirdpartyorderid": null,
  "datetime": "2026-04-30 14:45:40",
  "year": "2026",
  "account": "test123",
  "orderid": "eOvaJ9NIz0"
}
```

## Table: tradeorder_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.tradeorder_sport` |
| 引擎 | cassandra |
| Primary Key | (year) clustering: (datetime, account, orderid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | amount | int | 是 | — |  |
| 2 | card4no | text | 是 | — |  |
| 3 | firstdatetime | text | 是 | — |  |
| 4 | firstorderid | text | 是 | — |  |
| 5 | lastupdatetime | bigint | 是 | — |  |
| 6 | paymethod | text | 是 | — |  |
| 7 | paytype | text | 是 | — |  |
| 8 | periodsuccesscount | int | 是 | — |  |
| 9 | status | int | 是 | — |  |
| 10 | subid | text | 是 | — |  |
| 11 | thirdpartyname | text | 是 | — |  |
| 12 | thirdpartyorderid | text | 是 | — |  |
| 13 | datetime | text | 是 | — | CK |
| 14 | year | text | 是 | — | PK |
| 15 | account | text | 是 | — | CK |
| 16 | orderid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "amount": 225,
  "card4no": null,
  "firstdatetime": null,
  "firstorderid": null,
  "lastupdatetime": 1704334909,
  "paymethod": "disposable",
  "paytype": "WebATM",
  "periodsuccesscount": 0,
  "status": 0,
  "subid": "3",
  "thirdpartyname": "ECPay",
  "thirdpartyorderid": null,
  "datetime": "2024-01-02 15:51:52",
  "year": "2024",
  "account": "GUwoKbsZa2m",
  "orderid": "oaNjHIAoN0"
}
```

## Table: tradeorder_stock

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.tradeorder_stock` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (orderid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | amount | int | 是 | — |  |
| 2 | card4no | text | 是 | — |  |
| 3 | datetime | text | 是 | — |  |
| 4 | paytype | text | 是 | — |  |
| 5 | status | int | 是 | — |  |
| 6 | subid | text | 是 | — |  |
| 7 | thirdname | text | 是 | — |  |
| 8 | thirdorderid | text | 是 | — |  |
| 9 | account | text | 是 | — | PK |
| 10 | orderid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "amount": 10,
  "card4no": null,
  "datetime": "2022/12/22 15:07:08",
  "paytype": null,
  "status": 0,
  "subid": "4",
  "thirdname": null,
  "thirdorderid": null,
  "account": "zb01",
  "orderid": "q2Vh5Ytm9E"
}
```

## Table: withdrawlogs_activity

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.withdrawlogs_activity` |
| 引擎 | cassandra |
| Primary Key | (site) clustering: (activityevent, account, cid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | accountname | text | 是 | — |  |
| 2 | contactnumber | text | 是 | — |  |
| 3 | status | int | 是 | — |  |
| 4 | updatetime | bigint | 是 | — |  |
| 5 | activityevent | text | 是 | — | CK |
| 6 | site | text | 是 | — | PK |
| 7 | account | text | 是 | — | CK |
| 8 | cid | int | 是 | — | CK |

### Sample（first row）

(empty table)

## Table: withdrawlogs_sport

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `payment.withdrawlogs_sport` |
| 引擎 | cassandra |
| Primary Key | (account) clustering: (datetime) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | amount | int | 是 | — |  |
| 2 | remark | text | 是 | — |  |
| 3 | status | int | 是 | — |  |
| 4 | updatetime | bigint | 是 | — |  |
| 5 | account | text | 是 | — | PK |
| 6 | datetime | text | 是 | — | CK |

### Sample（first row）

```json
{
  "amount": 5500,
  "remark": "\u672A\u6536\u5230\u8CC7\u6599",
  "status": 2,
  "updatetime": 1734081064,
  "account": "EUYjeDt1cz8",
  "datetime": "2024-11-15 14:11"
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
