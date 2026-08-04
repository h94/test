---
aidata_db_sync: true
engine: cassandra
db_name: news
source: 192.168.55.80:9042
keyspace: news
table_count: 17
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-05-30T08:23:42.6860354Z
sync_log_id: 28
---

# Tables

## Table: aifunshits

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.aifunshits` |
| 引擎 | cassandra |
| Primary Key | (funsname) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | aihints | text | 是 | — |  |
| 2 | workspace | text | 是 | — |  |
| 3 | funsname | text | 是 | — | PK |

### Sample（first row）

```json
{
  "aihints": "\u751F\u6210\u4E00\u7BC7\u672C\u6587\u4EE5\u53CA\u65B0\u768412\u7BC7\u56DE\u8986\u77ED\u53E5,\u5982\u672C\u6587\u5167\u5BB9\u4E2D\u6709\u63D0\u53CA\u53C3\u8003\u9023\u7D50(X,\u5B98\u7DB2,espn,\u65B0\u805E\u4F86\u6E90 \u7B49\u7B49)\u548C\u672C\u6587\u76F8\u95DC\u9700\u5BEB\u51FA\u9023\u7D50\u7DB2\u5740\u51FA\u8655,\u5982\u7121\u9023\u7D50\u8CC7\u8A0A\u5247\u7121\u9700\u5BEB\u51FA.\u4E0D\u8981\u6709Tag\u6A19\u7C64,\u5167\u5BB9\u7121\u9700\u6A19\u984C\u4E3B\u65E8.\u5982\u6709\u95DC\u65BC\u6BD4\u8CFD\u806F\u76DF\u968A\u4F0D\u7403\u54E1\u540D\u7A31\u8981\u7528\u53F0\u7063\u5E38\u7528\u540D\u7A31,",
  "workspace": null,
  "funsname": "WriteBotArticleCommon"
}
```

## Table: ainews

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.ainews` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, lid, gid, llmhashkey, status) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | anwser | text | 是 | — |  |
| 2 | articleid | text | 是 | — |  |
| 3 | bets | list<text> | 是 | — |  |
| 4 | createtime | text | 是 | — |  |
| 5 | llmsettings | map<text, text> | 是 | — |  |
| 6 | others | map<text, text> | 是 | — |  |
| 7 | question | text | 是 | — |  |
| 8 | reanwser | text | 是 | — |  |
| 9 | used | int | 是 | — |  |
| 10 | gdate | text | 是 | — | PK |
| 11 | gtype | text | 是 | — | CK |
| 12 | lid | text | 是 | — | CK |
| 13 | gid | text | 是 | — | CK |
| 14 | llmhashkey | text | 是 | — | CK |
| 15 | status | int | 是 | — | CK |

### Sample（first row）

```json
{
  "anwser": "{Q1 00]InplayAI\u5373\u6642\u5206\u6790\u5831\u544A.Half\u8B93\u5206\u52A0\u6B0A\u5206\u6578\u70BA20.44,\u9810\u6E2C\u7D50\u679C\u70BA\u4E3B\u968A[\u675C\u62DC](3.5)\u7372\u52DD.Half\u5927\u5C0F\u52A0\u6B0A\u5206\u6578\u70BA23.30,\u9810\u6E2C\u7D50\u679C\u70BA97.5\u5927\u7372\u52DD.(\u767C\u5E03\u65BC:02:20)",
  "articleid": null,
  "bets": null,
  "createtime": "2025-11-07 02:20:17",
  "llmsettings": null,
  "others": {
    "gtime": "02:00",
    "half_HA": "Half",
    "half_OU": "Half",
    "key_HA": "BK_11_HA_Half_Main_AdditionH",
    "key_OU": "BK_11_OU_Half_Main_AdditionH",
    "league": "\u6B50\u6D32\u7C43\u7403\u806F\u8CFD",
    "predict_HA": "1",
    "predict_OU": "1",
    "rule_HA": "[-6.34]",
    "rule_OU": "[-8.27]",
    "score_A": "25",
    "score_H": "26",
    "score_HA": "20.44",
    "score_OU": "23.30",
    "spread_HA": "3.5",
    "spread_OU": "97.5",
    "teamA": "\u7279\u62C9\u7DAD\u592B\u590F\u666E\u723E",
    "teamH": "\u675C\u62DC"
  },
  "question": null,
  "reanwser": null,
  "used": 1,
  "gdate": "2025-11-07",
  "gtype": "BK",
  "lid": "LHSP3MLU160",
  "gid": "G2SkJMOTbUU",
  "llmhashkey": "InplayAI",
  "status": 11
}
```

## Table: ainews_gs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.ainews_gs` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, lid, gid, llmhashkey, status) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | anwser | text | 是 | — |  |
| 2 | articleid | text | 是 | — |  |
| 3 | bets | list<text> | 是 | — |  |
| 4 | createtime | text | 是 | — |  |
| 5 | llmsettings | map<text, text> | 是 | — |  |
| 6 | others | map<text, text> | 是 | — |  |
| 7 | question | text | 是 | — |  |
| 8 | reanwser | text | 是 | — |  |
| 9 | used | int | 是 | — |  |
| 10 | gdate | text | 是 | — | PK |
| 11 | gtype | text | 是 | — | CK |
| 12 | lid | text | 是 | — | CK |
| 13 | gid | text | 是 | — | CK |
| 14 | llmhashkey | text | 是 | — | CK |
| 15 | status | int | 是 | — | CK |

### Sample（first row）

```json
{
  "anwser": "\u6B50\u6D32\u7C43\u7403\u806F\u8CFD\uFF1A\u675C\u62DC\u7C43\u7403\u6703\u8FCE\u6230\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B\n\n\u6B50\u6D32\u7C43\u7403\u806F\u8CFD\u4ECA\u665A\u71B1\u9B27\u958B\u6253\uFF01\u675C\u62DC\u7C43\u7403\u6703\u4E3B\u5834\u8FCE\u6230\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B\uFF0C\u8CFD\u4E8B\u5B9A\u65BC2025\u5E7411\u67087\u65E502:00\uFF08\u53F0\u7063\u6642\u9593\uFF09\u5728\u85A9\u62C9\u71B1\u7AA9\u7684Olimpijska dvorana Juan Antonio Samaranch\u9AD4\u80B2\u9928\u8209\u884C\u3002\u9019\u5834\u5C0D\u6C7A\u5099\u53D7\u77DA\u76EE\uFF0C\u5169\u968A\u5BE6\u529B\u76F8\u7576\uFF0C\u7403\u8FF7\u5011\u5343\u842C\u5225\u932F\u904E\u3002\n\n\u675C\u62DC\u7C43\u7403\u6703\u8FD1\u6CC1\u8D77\u4F0F\u4E0D\u5B9A\uFF0C\u5E73\u5747\u6BCF\u5834\u5F97\u520683.6\u5206\u3001\u5931\u520680.8\u5206\uFF0C\u6700\u8FD15\u6230\u70BAL-L-L-W-W\uFF0C\u9632\u5B88\u7AEF\u7A0D\u986F\u7A69\u5065\u4F46\u9032\u653B\u706B\u529B\u9700\u52A0\u5F37\u3002\u53CD\u89C0\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B\u72C0\u614B\u706B\u71B1\uFF0C\u5E73\u5747\u5F97\u520685.8\u5206\u3001\u5931\u5206\u540C\u6A2380.8\u5206\uFF0C\u8FD15\u6230L-W-W-W-W\uFF0C\u9023\u52DD\u6C23\u52E2\u6B63\u65FA\uFF0C\u770B\u4F86\u4ED6\u5011\u9032\u653B\u7AEF\u7279\u5225\u7280\u5229\uFF0C\u675C\u62DC\u5F97\u5C0F\u5FC3\u61C9\u5C0D\u3002\n\n\u535A\u5F69\u5E02\u5834\u71B1\u8B70\u4E0D\u65B7\uFF0C\u4E0D\u8B93\u5206\u7368\u8D0F\u8CE0\u7387\u986F\u793A\u675C\u62DC2.204\u3001\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B1.717\uFF0C\u5E02\u5834\u660E\u986F\u770B\u597D\u5BA2\u968A\u3002\u8B93\u5206\u76E4\u5247\u662F\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B\u8B932.5\u7403\uFF0C\u96D9\u65B9\u8CE0\u7387\u76861.93\uFF1B\u5927\u5C0F\u5206\u5B9A\u5728169.5\u5206\uFF0C\u540C\u6A231.93\u5747\u8861\u958B\u51FA\u3002\n\n\u672C\u7CFB\u7D71AI\u9810\u6E2C\u6A21\u578B\u6295\u7968\u7D50\u679C\u51FA\u7210\uFF1A\u52DD\u8CA0\u76E4\u4E3B2\u7968 vs \u5BA23\u7968\uFF0C\u770B\u597D\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B\u53D6\u52DD\uFF1B\u8B93\u5206\u76E4\u4E3B0\u7968 vs \u5BA23\u7968\uFF0C\u62BC\u6CE8\u590F\u666E\u723E\u8B932.5\u7403\u6709\u7372\u5229\u7A7A\u9593\uFF0C\u986F\u793A\u5F37\u968A\u512A\u52E2\u660E\u986F\uFF1B\u5927\u5C0F\u5206\u5247\u59273\u7968 vs \u5C0F2\u7968\uFF0C\u50BE\u5411\u9AD8\u5206\u5C0D\u6C7A\u3002\u8CFD\u524D\u6C1B\u570D\u7DCA\u5F35\uFF0C\u62ED\u76EE\u4EE5\u5F85\uFF01\uFF08248\u5B57\uFF09(\u767C\u5E03\u65BC:2025-11-06 08:23)",
  "articleid": null,
  "bets": null,
  "createtime": "2025-11-06 08:23:46",
  "llmsettings": {
    "chatModel": "grok-4-fast-non-reasoning",
    "chatProvider": "xai",
    "openAiPrompt": "\u8ACB\u6839\u64DA\u6211\u63D0\u4F9B\u7684\u6BD4\u8CFD\u6578\u64DA\u8207\u53C3\u6578\uFF0C\u64B0\u5BEB\u4E00\u7BC7**\u6392\u7248\u6574\u6F54**\u7684\u904B\u52D5\u8CFD\u4E8B\u5831\u5C0E\u3002\n\n\u64B0\u5BEB\u6642\u8ACB\u9075\u5B88\u4EE5\u4E0B\u898F\u5247\uFF1A\n\n\u683C\u5F0F\u8981\u6C42\uFF1A\n1. \u4F7F\u7528\u6BB5\u843D\u6E05\u695A\u5206\u7BC0\uFF0C\u6BCF\u6BB5\u4E0D\u8D85\u904E 5 \u884C\uFF0C\u5229\u65BC\u95B1\u8B80\u3002\n2. \u4E0D\u8981\u51FA\u73FE\u7121\u610F\u7FA9\u7684\u7A7A\u767D\u6216\u4E82\u78BC\uFF0C\u8A9E\u53E5\u9808\u901A\u9806\u3002\n3. \u6587\u7AE0\u7E3D\u5B57\u6578\u52D9\u5FC5\u9650\u5236\u5728300\u5B57\u5167\u3002\n4.  \u5168\u6587\u4EE5\u7E41\u9AD4\u4E2D\u6587\u64B0\u5BEB\u3002\n\u5167\u5BB9\u8981\u6C42\uFF1A\n1. \u5168\u6587\u9700**\u4EE5\u6211\u63D0\u4F9B\u7684\u8CC7\u6599\u70BA\u4E3B**\u64B0\u5BEB\uFF0C\u52FF\u751F\u6210\u865B\u69CB\u4E8B\u4EF6\u6216\u6BD4\u6578\u3002\n2. \u6587\u7AE0\u8A9E\u6C23\u50CF\u662F\u9AD4\u80B2\u65B0\u805E\u6216\u904B\u52D5\u7DB2\u7AD9\u7684\u8A9E\u6C23\uFF0C\u53EF\u4EE5\u66F4\u52A0\u6D3B\u6F51\u751F\u52D5\u3002\n3.\u7576\u5167\u5BB9\u63D0\u5230\u4E3B\u968A\u6216\u5BA2\u968A\u6642\uFF0C\u9700\u6539\u7528\u968A\u540D\u7A31\u547C\uFF0C\u4E0D\u4F7F\u7528\u4E3B\u5BA2\u968A\u4EE3\u66FF\u3002\n4. \u5305\u542B\u4EE5\u4E0B\u8CC7\u8A0A\uFF1A\n   - \u4EA4\u6230\u968A\u4F0D\u8207\u6BD4\u8CFD\u6642\u9593\u3001\u5834\u5730\n   - \u7403\u968A\u8FD1\u6CC1\u6982\u8FF0\uFF08\u82E5\u6709\u8CC7\u6599\uFF09\n   - \u7403\u54E1\u6982\u8FF0 \uFF08\u82E5\u6709\u8CC7\u6599\uFF09\n   - AI\u63A8\u85A6\uFF08\u82E5\u6709\u8CC7\u6599\uFF09\n   - \u535A\u5F69\u516C\u53F8\u76E4\u53E3\u8CC7\u6599\n5.\u5982\u82E5\u6587\u7AE0\u4E2D\u5167\u5BB9\u4E2D\u6709\u63D0\u5230\u968A\u4F0D\u7684 \u512A\u52E2\u52A3\u52E2\u4E0D\u8981\u7528\u689D\u5217\u7684,\u6539\u5BEB\u6210[\u7C21\u7565\u7684][\u53E3\u8A9E\u5316\u7684]\n6.\u4E0D\u8981\u63A8\u6E2C\u6BD4\u8CFD\u7D50\u679C\u3002",
    "openAiTemp": "0.7"
  },
  "others": {
    "ai_all": "{\u0022Home\u0022:2,\u0022Away\u0022:3,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:3,\u0022Over\u0022:3,\u0022Under\u0022:2}",
    "ai_fake": "{\u0022Home\u0022:2,\u0022Away\u0022:3,\u0022Over\u0022:2,\u0022Under\u0022:2,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:0}",
    "ai_odd": "{\u0022Home\u0022:0,\u0022Away\u0022:0,\u0022Over\u0022:0,\u0022Under\u0022:0,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:0}",
    "ai_player": "{\u0022Home\u0022:0,\u0022Away\u0022:1,\u0022Over\u0022:1,\u0022Under\u0022:0,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:3}",
    "ai_site": "{\u0022Home\u0022:0,\u0022Away\u0022:0,\u0022Over\u0022:0,\u0022Under\u0022:0,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:0}",
    "gtime": "02:00",
    "ha_spread": "-2.5",
    "league": "\u6B50\u6D32\u7C43\u7403\u806F\u8CFD",
    "ou_spread": "169.5",
    "teamA": "\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B",
    "teamH": "\u675C\u62DC\u7C43\u7403\u6703",
    "users": "[{\u0022Account\u0022:\u0022E2PuhQCjS6S\u0022,\u0022UserName\u0022:\u0022Manal\u0022,\u0022FilterType\u0022:\u0022Killer\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:0,\u0022PredictCount\u0022:0,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022E6GcFFB0bRx\u0022,\u0022UserName\u0022:\u0022\\u6B50\\u6587\u0022,\u0022FilterType\u0022:\u0022Killer\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:0,\u0022PredictCount\u0022:0,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022E6mZ7ND1ayF\u0022,\u0022UserName\u0022:\u0022\\u5C0FP\u0022,\u0022FilterType\u0022:\u0022Killer\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:0,\u0022PredictCount\u0022:0,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022EDEeFQV7ocq\u0022,\u0022UserName\u0022:\u0022\\u6930\\u4EBA\u0022,\u0022FilterType\u0022:\u0022Killer\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:0,\u0022PredictCount\u0022:0,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022EFCaGW8R7rY\u0022,\u0022UserName\u0022:\u0022jklceks7215\u0022,\u0022FilterType\u0022:\u0022Killer\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:0,\u0022PredictCount\u0022:0,\u0022PredictGames\u0022:[]}]"
  },
  "question": "\u5BEB\u4E00\u7BC7\u95DC\u65BC\u85CD\u7403\u6BD4\u8CFD\u7684\u8CFD\u524D\u5831\u5C0E,[2025-11-07 \u6B50\u6D32\u7C43\u7403\u806F\u8CFD \u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B vs \u675C\u62DC\u7C43\u7403\u6703],\u4E3B\u968A\u70BA\u675C\u62DC\u7C43\u7403\u6703,\u5BA2\u968A\u70BA\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B,\u6BD4\u8CFD\u6642\u9593 2025-11-07 02:00 (\u53F0\u7063\u6642\u9593),\u4E26\u4E14\u52A0\u4E0A\u4EE5\u4E0B\u7684\u5167\u5BB9:\r\n1.\u675C\u62DC\u8FD1\u6CC1:\u5E73\u5747\u6BCF\u5834\u5F97\u520683.6,\u5931\u520680.8,\u6700\u8FD15\u5834\u52DD\u8CA0\u72C0\u6CC1[L,L,L,W,W](\u8FD1-\u9060);\n\u7279\u62C9\u7DAD\u592B\u590F\u666E\u723E\u8FD1\u6CC1:\u5E73\u5747\u6BCF\u5834\u5F97\u520685.8,\u5931\u520680.8,\u6700\u8FD15\u5834\u52DD\u8CA0\u72C0\u6CC1[L,W,W,W,W](\u8FD1-\u9060);\n\r\n2.\u672C\u5834\u8CFD\u4E8B\u57FA\u672C\u8CC7\u6599\u6BD4\u8CFD\u5834\u5730=Olimpijska dvorana Juan Antonio Samaranch (Sarajevo);\r\n3.\u570B\u969B\u76E4\u53E3\u8CE0\u7387(Odds)\u8CC7\u8A0A:\u4E0D\u8B93\u5206(\u7368\u8D0F)\u7684\u8CE0\u7387(\u6E2F\u5F0F)\u70BA\u4E3B\u968A\u8CE0\u7387(\u6E2F\u5F0F):2.204,\u5BA2\u968A\u8CE0\u7387(\u6E2F\u5F0F):1.717;\u5E02\u5834\u975E\u5E38\u770B\u597D\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B;,\u8B93\u5206\u7684\u76E4\u53E3\u70BA\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B(\u5F37\u968A)\u8B932.5\u7403,\u675C\u62DC\u7C43\u7403\u6703\u8CE0\u7387(\u6E2F\u5F0F):1.93,\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B\u8CE0\u7387(\u6E2F\u5F0F):1.93;,\u5927\u5C0F\u5206\u7684\u76E4\u53E3:169.5\u5206,\u8CE0\u7387(\u6E2F\u5F0F)\u70BA\u5927\u5206\u8CE0\u7387(\u6E2F\u5F0F):1.93,\u5C0F\u5206\u8CE0\u7387(\u6E2F\u5F0F):1.93;.,,\r\n4.[\u672C\u7CFB\u7D71]\u7684AI\u52DD\u8CA0\u9810\u6E2C\u6A21\u578B\u7684\u6295\u7968\u7D50\u679C:\u770B\u597D\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B\u80FD\u7372\u52DD,(\u4E3B2\u7968 vs \u5BA23\u7968).[\u672C\u7CFB\u7D71]\u7684AI\u8B93\u5206\u76E4\u9810\u6E2C\u6A21\u578B\u7684\u6295\u7968\u7D50\u679C:\u770B\u597D\u62BC\u6CE8\u590F\u666E\u723E\u7279\u62C9\u7DAD\u592B(\u8B932.5)\u80FD\u7372\u5229,(\u4E3B0\u7968 vs \u5BA23\u7968).,AI\u65BC\u8B93\u5206\u548C\u52DD\u8CA0\u76E4\u540C\u6A23\u9078\u64C7\u5F37\u968A.\u8868\u793A\u5F37\u968A\u5F37\u58D3\u5BA2\u968A.[\u672C\u7CFB\u7D71]\u7684AI\u5927\u5C0F\u5206\u9810\u6E2C\u6A21\u578B\u7684\u6295\u7968\u7D50\u679C:\u770B\u597D169.5\u5927\u5206,(\u5927\u52063\u7968 vs \u5C0F\u52062\u7968).",
  "reanwser": null,
  "used": 1,
  "gdate": "2025-11-07",
  "gtype": "BK",
  "lid": "LHSP3MLU160",
  "gid": "G2SkJMOTbUU",
  "llmhashkey": "TYL0CQ5E3O",
  "status": 2
}
```

## Table: ainews_lt

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.ainews_lt` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, lid, gid, llmhashkey, status) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | anwser | text | 是 | — |  |
| 2 | bets | list<text> | 是 | — |  |
| 3 | createtime | text | 是 | — |  |
| 4 | llmsettings | map<text, text> | 是 | — |  |
| 5 | others | map<text, text> | 是 | — |  |
| 6 | question | text | 是 | — |  |
| 7 | reanwser | text | 是 | — |  |
| 8 | used | int | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | gtype | text | 是 | — | CK |
| 11 | lid | text | 是 | — | CK |
| 12 | gid | text | 是 | — | CK |
| 13 | llmhashkey | text | 是 | — | CK |
| 14 | status | int | 是 | — | CK |

### Sample（first row）

```json
{
  "anwser": "\u53F0\u7063\u904B\u5F69AI\u5206\u6790\u300B2025-11-07 NBA \u6D1B\u6749\u78EF\u5FEB\u8247 vs \u9CF3\u51F0\u57CE\u592A\u967D \u8CFD\u524D\u71B1\u8B70\n\n\u63D0\u4F9B\u8005:InplayZ,,\u53F0\u7063\u904B\u52D5\u5F69\u52B5\u7684\u6295\u6CE8\u7DE8\u865F:318\n\n\u563F\uFF0C\u7C43\u7403\u8FF7\u5011\uFF01\u660E\u5929\u65E9\u4E0A10\u9EDE\uFF08\u53F0\u7063\u6642\u9593\uFF09\uFF0C\u9CF3\u51F0\u57CE\u592A\u967D\u8981\u5728\u81EA\u5BB6\u4E3B\u5834\u8FCE\u6230\u6D1B\u6749\u78EF\u5FEB\u8247\uFF0C\u9019\u53EF\u662F\u4ED6\u5011\u672C\u5B63\u9996\u6B21\u4E3B\u5BA2\u5C0D\u6C7A\u7684\u958B\u5834\u79C0\u3002\u592A\u967D\u76EE\u524D\u4E3B\u58343\u52DD1\u8CA0\uFF0C\u611F\u89BA\u5728\u5BB6\u88E1\u6253\u7403\u5C31\u662F\u6709\u80A1\u9B54\u529B\uFF0C\u5BA2\u5834\u537B0\u52DD4\u8CA0\uFF0C\u7C21\u76F4\u662F\u5169\u500B\u6975\u7AEF\u554A\uFF5E\u5FEB\u8247\u5462\uFF1F\u4ED6\u5011\u6700\u8FD1\u72C0\u614B\u8D77\u4F0F\u4E0D\u5B9A\uFF0C\u4F46\u6709Kawhi Leonard\u56DE\u6B78\uFF0C\u706B\u529B\u53EF\u4E0D\u80FD\u5C0F\u770B\u3002\u4F86\u804A\u804A\u5169\u968A\u8FD1\u6CC1\u5427\uFF01\n\n\u5148\u8AAA\u592A\u967D\uFF0C\u4ED6\u5011\u5E73\u5747\u6BCF\u5834\u8F5F120.4\u5206\uFF0C\u5931\u5206116.8\uFF0C\u6700\u8FD15\u5834\u662FL,W,W,L,L\uFF08\u5F9E\u8FD1\u5230\u9060\uFF09\u3002\u5728\u5BB6\u88E1\uFF0C\u4ED6\u5011\u9023\u7E8C\u96D9\u4F4D\u6578\u5927\u52DD\u7336\u4ED6\u7235\u58EB\u548C\u8056\u5B89\u6771\u5C3C\u5967\u99AC\u523A\uFF0C\u4E0A\u5834\u5C0D\u99AC\u523A\u751A\u81F3\u9818\u514831\u5206\uFF0C\u6700\u5F8C130-118\u6536\u5DE5\u3002\u5B63\u521D\u5728\u5BB6\u9006\u8F49\u85A9\u514B\u62C9\u9580\u6258\u570B\u738B\uFF0C\u5F9E17\u5206\u843D\u5F8C\u8FFD\u56DE\u4F86\uFF0C\u8D85\u523A\u6FC0\uFF01\u4E0D\u904E\u5BA2\u5834\u8F38\u7D66\u91D1\u5DDE\u52C7\u58EB118-107\uFF0CDevin Booker\u7206\u780D38\u5206\u9084\u4E0D\u5920\uFF0C\u4ED6\u81EA\u5DF1\u8AAA\uFF1A\u300C\u6C92\u7167\u904A\u6232\u8A08\u5283\u8D70\uFF0C\u5F97\u66F4\u5C08\u6CE8\uFF0C\u5F9E\u958B\u5C40\u5C31\u885D\u523A\u3002\u300D\n\n\u5FEB\u8247\u9019\u908A\uFF0C\u5E73\u5747\u5F97\u5206109\uFF0C\u5931\u5206115\uFF0C\u6700\u8FD15\u5834L,L,W,L,W\u3002\u4ED6\u5011\u4E0A\u5834\u5728\u5BB6\u8F38\u7D66\u5967\u514B\u62C9\u8377\u99AC\u57CE\u96F7\u9706126-107\uFF0C\u7B2C\u4E09\u7BC0\u88AB17-0\u8DD1\u8D70\uFF0CJames Harden\u524D\u534A\u5834\u731B\u4F46\u5F8C\u534A\u53EA\u5F973\u5206\u3002\u4ED6\u8AAA\uFF1A\u300C\u7C43\u7403\u5C31\u662F\u4E00\u5834\u8DD1\u5206\u7684\u904A\u6232\uFF0C\u5C0D\u4E0A\u885B\u5195\u51A0\u8ECD\uFF0C\u7C21\u55AE\u3002\u300DKawhi Leonard\u819D\u50B7\u5FA9\u51FA\uFF0C\u9810\u8A08\u4E0A\u9663\uFF0C\u4ED6\u6700\u8FD1\u5169\u583461\u5206\u52A010\u6284\u622A\uFF0C\u52A0\u76DF\u53F2\u53EA\u6709Ron Harper\u548CChris Paul\u505A\u5230\u9019\u7D00\u9304\u3002Bradley Beal\u8173\u8E1D\u50B7\u5F8C\u4E5F\u56DE\u6B78\uFF0C\u9019\u662F\u4ED6\u96E2\u958B\u592A\u967D\u5F8C\u9996\u5EA6\u56DE\u9CF3\u51F0\u57CE\uFF0C\u7576\u521D\u592A\u967D\u653E\u68C4\u4ED6\u5403\u63891.1\u5104\u5408\u7D04\uFF0C\u4ED6\u4ECA\u590F\u8F49\u6295\u5FEB\u8247\u7C3D2\u5E741100\u842C\u3002\n\n\u5169\u968A\u4E0A\u56DE\u4EA4\u624B\u662F10\u670824\u65E5\uFF0C\u5FEB\u8247\u5728\u5BB6129-102\u5927\u52DD\u592A\u967D\uFF0CLeonard 26\u5206\uFF0CBeal 6\u5206\u3002\u592A\u967D\u9019\u908A\uFF0CMark Williams\u5C0D\u52C7\u58EB\u780D16\u520616\u7C43\u677F\u96D9\u5341\uFF0C\u5834\u5747\u4E0A27\u5206\u9418\uFF0C\u770B\u4F86\u5728\u63A7\u7BA1\u6642\u9593\u3002\u300C\u4E0A\u5834\u5C31\u60F3\u5F71\u97FF\u6BD4\u8CFD\uFF0C\u300D\u4ED6\u8AAA\u3002Dillon Brooks\u6838\u5FC3\u808C\u50B7\u3001Jalen Green\u817F\u7B4B\u50B7\u7F3A\u9663\uFF0CGreen\u5B63\u524D\u50B7\u5230\u73FE\u5728\uFF0C\u6559\u7DF4Jordan Ott\u8AAA\u4ED6\u8DA8\u52E2\u6B63\u9762\uFF0C\u6700\u8FD1\u7DF45\u5C0D5\u3002Grayson Allen\u5834\u574716.4\u5206\u5148\u767C\uFF0CRoyce O\u0027Neale 13.4\u52066.6\u7C43\u677F\uFF0C\u5916\u52A019\u8A18\u4E09\u5206\u3002\n\n\u89C0\u6230\u91CD\u9EDE\u4F86\u4E86\uFF1AHome is where the Suns shine\uFF01\u592A\u967D\u56DE\u4E3B\u5834\u8D85\u6709\u512A\u52E2\uFF0C\u552F\u4E00\u4E3B\u5834\u8F38\u7403\u662F10\u670829\u65E5\u8F38\u5B5F\u83F2\u65AF\u7070\u718A114-113\uFF0CJa Morant\u6700\u5F8C7.6\u79D2\u7D55\u6BBA\u3002\u4ED6\u5011\u9818\u514825\u5206\u5BB0\u7235\u58EB\u300131\u5206\u6EC5\u99AC\u523A\uFF0C\u611F\u89BA\u5728\u5BB6\u5C31\u662F\u7121\u6575\u6A21\u5F0F\u3002\u5FEB\u8247\u5C11\u4E86Leonard\u548CBeal\u6253\u80CC\u9760\u80CC\uFF0CHarden\u7368\u6490\u4F46\u5F8C\u52C1\u4E0D\u8DB3\u3002\u9019\u5834\u662F\u4E3B\u5BA2\u9023\u6230\u9996\u6230\uFF0C2\u67081\u65E5\u518D\u898B\u771F\u7AE0\u3002\n\n\u73FE\u5728\u804A\u804A\u76E4\u53E3\u8CC7\u8A0A\uFF0C\u5F9E\u4E0D\u8B93\u5206\uFF08\u7368\u8D0F\uFF09\u4F86\u770B\uFF0C\u4E3B\u968A\u592A\u967D\u52DD\u738757.4%\uFF0C\u5BA2\u968A\u5FEB\u824742.6%\u3002\u52DD\u7387\u8B8A\u5316\u5F9E\u820A\u5230\u65B0\uFF1A52.5%\u300157.4%\u300152.5%...\u4E00\u8DEF\u523057.4%\uFF0C\u5168\u9AD4\u770B\u597D\u5EA6\u6CE2\u52D5\uFF0C\u610F\u898B\u5206\u6B67\u4E2D\u592A\u967D\u7A0D\u4F54\u4E0A\u98A8\u3002\u8B93\u5206\u76E4\u662F\u592A\u967D\u8B932.5\u7403\uFF0C\u592A\u967D\u52DD\u738750%\uFF0C\u5FEB\u824750%\uFF1B\u8B8A\u5316\u5F9E51.3%\u523048.7%\uFF0C\u4E00\u6A23\u6CE2\u52D5\u5206\u6B67\u3002\u5927\u5C0F\u5206\u76E4223.5\u5206\uFF0C\u5927\u5206\u548C\u5C0F\u5206\u540450%\uFF0C\u4E2D\u6027\u5E73\u8861\u3002\n\n\u7403\u738BInplayZ AI\u9810\u6E2C\u6578\u64DA  \nAI\u52DD\u8CA0\u6A21\u578B\u6295\u7968\uFF1A\u770B\u597D\u9CF3\u51F0\u57CE\u592A\u967D\u7372\u52DD\uFF08\u4E3B4\u7968 vs \u5BA21\u7968\uFF09\u3002  \nAI\u8B93\u5206\u76E4\u6A21\u578B\uFF08\u592A\u967D\u8B932.5\uFF09\uFF1A\u770B\u597D\u62BC\u6CE8\u9CF3\u51F0\u57CE\u592A\u967D\u80FD\u7372\u5229\uFF08\u4E3B5\u7968 vs \u5BA20\u7968\uFF09\u3002AI\u5728\u8B93\u5206\u548C\u52DD\u8CA0\u90FD\u9078\u5F37\u968A\uFF0C\u986F\u793A\u592A\u967D\u5F37\u58D3\u5FEB\u8247\u3002  \nAI\u5927\u5C0F\u5206\u6A21\u578B\uFF08223.5\u5206\uFF09\uFF1A\u76E4\u53E3\u76F8\u7576\uFF0C\u96E3\u4EE5\u5340\u5206\uFF08\u5927\u52062\u7968 vs \u5C0F\u52062\u7968\uFF09\u3002\n\n\u7E3D\u4E4B\uFF0C\u9019\u5834\u592A\u967D\u4E3B\u5834\u512A\u52E2\u5927\uFF0CBooker\u706B\u529B\u5168\u958B\u5C0D\u4E0ALeonard\u56DE\u6B78\u7684\u5FEB\u8247\uFF0C\u7D55\u5C0D\u706B\u82B1\u56DB\u5C04\uFF01\u7403\u8FF7\u5011\uFF0C\u6E96\u5099\u597D\u71AC\u591C\u4E86\u55CE\uFF1F\u8A18\u5F97\u9396\u5B9A\u8CFD\u4E8B\uFF0C\u908A\u770B\u908A\u804A\u554A\uFF5E\uFF08\u5B57\u6578: 628\uFF09(\u767C\u5E03\u65BC:2025-11-06 16:12)",
  "bets": null,
  "createtime": "2025-11-06 16:12:13",
  "llmsettings": {
    "chatModel": "grok-4-0709",
    "chatProvider": "xai",
    "openAiPrompt": "1.\u5168\u6587\u9700**\u4EE5\u6211\u63D0\u4F9B\u7684\u8CC7\u6599\u70BA\u4E3B**\u64B0\u5BEB\uFF0C\u8ACB\u52FF\u751F\u6210\u865B\u69CB\u4E8B\u4EF6\u6216\u6BD4\u6578\n2.\u5168\u6587\u6392\u7248\u9069\u5408\u624B\u6A5F\u95B1\u8B80\uFF08\u6BB5\u843D\u4E0D\u8D85\u904E 3 \u884C\uFF09\uFF0C\u6587\u7AE0\u7E3D\u5B57\u6578\u52D9\u5FC5\u9650\u5236\u5728500-700\u5B57\u3002\n3.\u6587\u5B57\u8A9E\u6C23\u8F15\u9B06\u3001\u53E3\u8A9E\u5316\u3001\u6709\u6897\u4F46\u4E0D\u4F4E\u4FD7\uFF0C\u50CF\u793E\u7FA4\u8CBC\u6587\u6216\u904B\u5F69\u793E\u7FA4\u7684\u98A8\u683C\u3002\n4.\u5305\u542B\u8CFD\u4E8B\u8CC7\u8A0A\u3001 \u535A\u5F69\u516C\u53F8\u76E4\u53E3\u8CC7\u6599\u3002(\u5982\u539F\u59CB\u8CC7\u6599\u7121\u63D0\u4F9B\u5247\u4E0D\u9700\u8981)\n5.AI\u9810\u6E2C\u6578\u64DA\uFF0C\u9700\u8981\u52A0\u5165\u6A19\u984C\u5167\u3002\n7.\u4E0D\u8981\u592A\u5236\u5F0F\uFF0C\u50CF\u5728\u8DDF\u904B\u52D5\u8FF7\u804A\u5929\u4E00\u6A23\u3002\n8.\u7576\u5167\u5BB9\u63D0\u5230\u4E3B\u968A\u6216\u5BA2\u968A\u6642\uFF0C\u9700\u6539\u7528\u968A\u540D\u7A31\u547C\uFF0C\u4E0D\u4F7F\u7528\u4E3B\u5BA2\u968A\u4EE3\u66FF\u3002\n9.\u5982\u8CC7\u6599\u5DF2\u7D93\u63D0\u4F9B\u6BD4\u8CFDAI\u9810\u6E2C\u5167\u5BB9\uFF0C\u5247\u4F9D\u64DA\u9810\u6E2C\u5167\u5BB9\u65B9\u5411\u53BB\u5BEB\uFF0C\u7121\u9808\u5C07\u5167\u5BB9\u6539\u70BA\u8F03\u70BA\u4E2D\u7ACB\u7684\u9810\u6E2C\u3002\n10.\u4E0D\u8981\u63A8\u6E2C\u6BD4\u8CFD\u7D50\u679C\u3002\n11.\u6587\u7AE0\u7528\u5B57\u76E1\u91CF\u4E0D\u4EE5\u5E36\u6709\u8CED\u535A\u6027\u7684\u5B57\u773C\uFF0C\u4F8B\u5982\u300C\u8CED\u300D\u3001\u300C\u8CED\u9322\u300D\u3001\u300C\u8CED\u535A\u300D\u3001\u300C\u8CED\u76E4\u300D\u3001\u300C\u4E0B\u6CE8\u300D\u3002",
    "openAiTemp": "0.7"
  },
  "others": {
    "ai_all": "{\u0022Home\u0022:4,\u0022Away\u0022:1,\u0022Home_HA\u0022:5,\u0022Away_HA\u0022:0,\u0022Over\u0022:2,\u0022Under\u0022:2}",
    "ai_fake": "{}",
    "ai_odd": "{\u0022Home\u0022:1,\u0022Away\u0022:0,\u0022Over\u0022:0,\u0022Under\u0022:0,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:0}",
    "ai_player": "{\u0022Home\u0022:3,\u0022Away\u0022:1,\u0022Over\u0022:2,\u0022Under\u0022:0,\u0022Home_HA\u0022:4,\u0022Away_HA\u0022:0}",
    "ai_site": "{\u0022Home\u0022:3,\u0022Away\u0022:0,\u0022Over\u0022:2,\u0022Under\u0022:2,\u0022Home_HA\u0022:2,\u0022Away_HA\u0022:0}",
    "gtime": "10:00",
    "ha_spread": "2.5",
    "league": "\u7F8E\u570B\u8077\u7C43",
    "ou_spread": "223.5",
    "teamA": "\u6D1B\u6749\u78EF\u5FEB\u8247",
    "teamH": "\u9CF3\u51F0\u57CE\u592A\u967D",
    "users": "[{\u0022Account\u0022:\u0022ELs4KfGQ4pd\u0022,\u0022UserName\u0022:\u0022\\u82B1\\u958B\\u53C8\\u82B1\\u8B1D\\u82B1\\u6EFF\\u5929\u0022,\u0022FilterType\u0022:\u0022OU_winstreak\u0022,\u0022WinStreakDays\u0022:6,\u0022PredictWin\u0022:29,\u0022PredictCount\u0022:39,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022GaehMgLFjUo\u0022,\u0022UserName\u0022:\u0022\\u963F\\u5EB7\u0022,\u0022FilterType\u0022:\u0022OU\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:19,\u0022PredictCount\u0022:26,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022LDVKLg8acLI\u0022,\u0022UserName\u0022:\u0022kevin lin\u0022,\u0022FilterType\u0022:\u0022main\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:5,\u0022PredictCount\u0022:6,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022EW5QKLPfY5n\u0022,\u0022UserName\u0022:\u0022\\u6C6A\\u6C6A\u0022,\u0022FilterType\u0022:\u0022main\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:4,\u0022PredictCount\u0022:5,\u0022PredictGames\u0022:[]},{\u0022Account\u0022:\u0022GLV3CoguKv0\u0022,\u0022UserName\u0022:\u0022\\u9006\\u8F49\\u52DD\u0022,\u0022FilterType\u0022:\u0022main\u0022,\u0022WinStreakDays\u0022:0,\u0022PredictWin\u0022:12,\u0022PredictCount\u0022:16,\u0022PredictGames\u0022:[]}]"
  },
  "question": "\u5BEB\u4E00\u7BC7\u95DC\u65BC\u85CD\u7403\u6BD4\u8CFD\u7684\u8CFD\u524D\u5831\u5C0E,[2025-11-07 \u7F8E\u570B\u8077\u7C43 \u6D1B\u6749\u78EF\u5FEB\u8247 vs \u9CF3\u51F0\u57CE\u592A\u967D],\u4E3B\u968A\u70BA\u9CF3\u51F0\u57CE\u592A\u967D,\u5BA2\u968A\u70BA\u6D1B\u6749\u78EF\u5FEB\u8247,\u6BD4\u8CFD\u6642\u9593 2025-11-07 10:00 (\u53F0\u7063\u6642\u9593),\u4E26\u4E14\u52A0\u4E0A\u4EE5\u4E0B\u7684\u5167\u5BB9:\u5C07[\u63D0\u4F9B\u8005:InplayZ,,\u53F0\u7063\u904B\u52D5\u5F69\u52B5\u7684\u6295\u6CE8\u7DE8\u865F:318]\u653E\u5165\u6A19\u984C\u7684\u4E0B\u4E00\u884C\r\n1.Phoenix Suns\u8FD1\u6CC1:\u5E73\u5747\u6BCF\u5834\u5F97\u5206120.4,\u5931\u5206116.8,\u6700\u8FD15\u5834\u52DD\u8CA0\u72C0\u6CC1[L,W,W,L,L](\u8FD1-\u9060);\nLA Clippers\u8FD1\u6CC1:\u5E73\u5747\u6BCF\u5834\u5F97\u5206109,\u5931\u5206115,\u6700\u8FD15\u5834\u52DD\u8CA0\u72C0\u6CC1[L,L,W,L,W](\u8FD1-\u9060);\n\u5169\u968A\u8FD11\u5834\u5C0D\u6230\u7D50\u679C:[2025-10-25,LA Clippers(H) vs Phoenix Suns \u8CFD\u679C:129(H):102]\n\r\n2.\n\u89C0\u6230\u91CD\u9EDE:Home is where the Suns shine.\nPhoenix will return to its own building Thursday night to meet the Los Angeles Clippers in the first game of a home-and-home set, and the Suns will welcome the familiar surroundings.\nThe Suns are 3-1 at home this season, with their only loss coming on Ja Morant\u0027s 11-footer in the lane with 7.6 seconds remaining in Memphis\u0027 114-113 victory on Oct. 29.\nSince then, the Suns have double-digit home victories over the Utah Jazz and San Antonio Spurs. They led by as many as 25 in a 118-96 victory over the Jazz, and most recently built a 31-point lead to hand the Spurs their first loss 130-118 on Sunday.\nPhoenix overcame a 17-point deficit to beat the Sacramento Kings in the season opener at home but enter Thursday after a 118-107 loss at Golden State in a game in which the Suns fell behind by 25 points and dropped to 0-4 on the road.\n\u0022Just not following the game plan,\u0022 said Suns guard Devin Booker, who had a season-high 38 points. \u0022We got to come in more focused. We got to get off to a better start.\u0022\nThe Clippers enter after a 126-107 home loss to the Oklahoma City Thunder, when they played the defending champions even into the third quarter but gave up a 17-0 run in the late third and early fourth.\n\u0022Basketball is a game of runs, defending champs, simple,\u0022 Clippers guard James Harden said of the outcome. \u0022It\u0027s a four-quarter game.\u0022\nHarden had 25 points, six assists and six rebounds while leading the Clippers, who played without Kawhi Leonard (knee) and Bradley Beal (ankle) in the second game of a back-to-back. Harden had three points in the second half.\nLeonard, who is expected to play against the Suns, has 61 points and 10 steals in his last two games. He joined Ron Harper (twice) and Chris Paul as the only players in franchise history to hit those numbers. Paul, like Beal, also played for the Suns.\nBeal will make his first appearance in Phoenix since the ill-fitting marriage ended in divorce after last season, when the Suns waived him and ate the final two years and $110 million of his contract. Beal signed a two-year, $11 million deal with the Clippers in the offseason.\nLeonard had 26 points and Beal six in the Clippers\u0027 129-102 home victory over the Suns on Oct. 24. The teams will meet for the final time on Feb. 1.\nThe Suns\u0027 Mark Williams had a 16-point, 16-rebound, double-double against the Warriors in 27 minutes and appears to be playing on a minutes\u0027 limit. He has played more than 28 minutes once, when he went 31 in an overtime loss at Utah on Oct. 27.\n\u0022Whenever I am out there, I try to make an impact,\u0022 Williams said.\nThe Suns again were without Dillon Brooks (core muscle) and Jalen Green (hamstring) at Golden State, and their status for Thursday remains unknown. Green appears to be getting close to making his season debut after going through a 5-on-5 pregame workout Tuesday.\n\u0022Definitely trending in the right direction,\u0022 Suns coach Jordan Ott said of Green, who has not played since hamstring injury in training camp.\nGrayson Allen (16.4 points per game) has started alongside Booker in the backcourt, and Royce O\u0027Neale is averaging 13.4 points and 6.6 rebounds with 19 made 3-pointers in five starts in place of Brooks.\r\n3.\u5F9E\u904B\u5F69\u76E4\u53E3\u8CE0\u7387(Odds)\u8CC7\u8A0A\u63A8\u6E2C\u7684\u52DD\u7387:\u4E0D\u8B93\u5206(\u7368\u8D0F)\u7684\u52DD\u7387(%)\u70BA\u4E3B\u968A\u52DD\u7387(%):57.4,\u5BA2\u968A\u52DD\u7387(%):42.6;,\u8B93\u5206\u7684\u76E4\u53E3\u70BA\u9CF3\u51F0\u57CE\u592A\u967D(\u5F37\u968A)\u8B932.5\u7403,\u9CF3\u51F0\u57CE\u592A\u967D\u52DD\u7387(%):50,\u6D1B\u6749\u78EF\u5FEB\u8247\u52DD\u7387(%):50;,\u5927\u5C0F\u5206\u7684\u76E4\u53E3:223.5\u5206,\u52DD\u7387(%)\u70BA\u5927\u5206\u52DD\u7387(%):50,\u5C0F\u5206\u52DD\u7387(%):50;.[\u4E0D\u8B93\u5206(\u7368\u8D0F)\u52DD\u7387(%),\u4E3B\u968A\u8B8A\u5316(\u7531\u820A\u5230\u65B0)\u70BA52.5%,57.4%,52.5%,57.4%,57.6%,56.6%,57.6%,56.6%,57.6%,54.4%,57.4%,53%,57.4%,53%,57.4%,53%,57.4%,53%,57.4%,53%,57.4%,,\u5168\u9AD4\u770B\u597D\u5EA6\u6301\u7E8C\u6CE2\u52D5,\u770B\u6CD5\u5206\u6B67];,[\u8B93\u5206\u52DD\u7387(%),\u4E3B\u968A\u8B8A\u5316(\u7531\u820A\u5230\u65B0)\u70BA51.3%,51.3%,52.2%,51.3%,52.2%,51.3%,48.7%,,\u5168\u9AD4\u770B\u597D\u5EA6\u6301\u7E8C\u6CE2\u52D5,\u770B\u6CD5\u5206\u6B67];,\r\n4.[\u7403\u738BinplayZ]\u7684AI\u52DD\u8CA0\u9810\u6E2C\u6A21\u578B\u7684\u6295\u7968\u7D50\u679C:\u770B\u597D\u9CF3\u51F0\u57CE\u592A\u967D\u80FD\u7372\u52DD,(\u4E3B4\u7968 vs \u5BA21\u7968).[\u7403\u738BinplayZ]\u7684AI\u8B93\u5206\u76E4\u9810\u6E2C\u6A21\u578B\u7684\u6295\u7968\u7D50\u679C:\u770B\u597D\u62BC\u6CE8\u9CF3\u51F0\u57CE\u592A\u967D(\u8B932.5)\u80FD\u7372\u5229,(\u4E3B5\u7968 vs \u5BA20\u7968).,AI\u65BC\u8B93\u5206\u548C\u52DD\u8CA0\u76E4\u540C\u6A23\u9078\u64C7\u5F37\u968A.\u8868\u793A\u5F37\u968A\u5F37\u58D3\u5BA2\u968A.[\u7403\u738BinplayZ]\u7684AI\u5927\u5C0F\u5206\u9810\u6E2C\u6A21\u578B\u7684\u6295\u7968\u7D50\u679C:\u76E4\u53E3\u76F8\u7576,\u96E3\u4EE5\u5340\u5206,(\u5927\u52062\u7968 vs \u5C0F\u52062\u7968).",
  "reanwser": null,
  "used": 0,
  "gdate": "2025-11-07",
  "gtype": "BK",
  "lid": "LYr9egM00GV",
  "gid": "Gi01d7uoIzk",
  "llmhashkey": "BKTHGBAL9A",
  "status": 2
}
```

## Table: aireports

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.aireports` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, lid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | bets | map<text, text> | 是 | — |  |
| 2 | others | map<text, text> | 是 | — |  |
| 3 | results | map<text, text> | 是 | — |  |
| 4 | gdate | text | 是 | — | PK |
| 5 | gtype | text | 是 | — | CK |
| 6 | lid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "bets": {
    "R1": "[{\u0022Gid\u0022:\u0022G2SkJMOTbUU\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:620,\u0022Odd\u0022:0.62,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022G2SkJMOTbUU\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:910,\u0022Odd\u0022:0.91,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022C\u0022,\u0022Spread\u0022:-3,\u0022Ratio\u0022:-100},{\u0022Gid\u0022:\u0022G5vRsNPDj50\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:660,\u0022Odd\u0022:0.66,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022G5vRsNPDj50\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:900,\u0022Odd\u0022:0.9,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022C\u0022,\u0022Spread\u0022:3,\u0022Ratio\u0022:100},{\u0022Gid\u0022:\u0022G6Ud4uwe07k\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:-1000,\u0022Odd\u0022:0.88,\u0022WinLoss\u0022:\u0022L\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:14,\u0022Ratio\u0022:100},{\u0022Gid\u0022:\u0022GVRLJ0NvqA0\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:560,\u0022Odd\u0022:0.56,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022GVRLJ0NvqA0\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:-1000,\u0022Odd\u0022:0.9,\u0022WinLoss\u0022:\u0022L\u0022,\u0022IsLowPrice\u0022:\u0022C\u0022,\u0022Spread\u0022:-5,\u0022Ratio\u0022:-100},{\u0022Gid\u0022:\u0022GzZYvWGFvEC\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:-1000,\u0022Odd\u0022:0.53,\u0022WinLoss\u0022:\u0022L\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022GzZYvWGFvEC\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:-1000,\u0022Odd\u0022:0.95,\u0022WinLoss\u0022:\u0022L\u0022,\u0022IsLowPrice\u0022:\u0022C\u0022,\u0022Spread\u0022:5,\u0022Ratio\u0022:100}]",
    "R2": "[{\u0022Gid\u0022:\u0022G2SkJMOTbUU\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:620,\u0022Odd\u0022:0.62,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022G2SkJMOTbUU\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:910,\u0022Odd\u0022:0.91,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022C\u0022,\u0022Spread\u0022:-3,\u0022Ratio\u0022:-100},{\u0022Gid\u0022:\u0022G5vRsNPDj50\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:660,\u0022Odd\u0022:0.66,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022G6Ud4uwe07k\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:-1000,\u0022Odd\u0022:0.88,\u0022WinLoss\u0022:\u0022L\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:14,\u0022Ratio\u0022:100},{\u0022Gid\u0022:\u0022GVRLJ0NvqA0\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022A\u0022,\u0022ProfitPoint\u0022:560,\u0022Odd\u0022:0.56,\u0022WinLoss\u0022:\u0022W\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022GzZYvWGFvEC\u0022,\u0022Mode\u0022:\u00221X2\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:-1000,\u0022Odd\u0022:0.53,\u0022WinLoss\u0022:\u0022L\u0022,\u0022IsLowPrice\u0022:\u0022Y\u0022,\u0022Spread\u0022:0,\u0022Ratio\u0022:0},{\u0022Gid\u0022:\u0022GzZYvWGFvEC\u0022,\u0022Mode\u0022:\u0022HA\u0022,\u0022OddType\u0022:\u0022H\u0022,\u0022ProfitPoint\u0022:-1000,\u0022Odd\u0022:0.95,\u0022WinLoss\u0022:\u0022L\u0022,\u0022IsLowPrice\u0022:\u0022C\u0022,\u0022Spread\u0022:5,\u0022Ratio\u0022:100}]",
    "R3": "[]"
  },
  "others": {
    "G2SkJMOTbUU": "{\u0022League\u0022:\u0022\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022,\u0022TeamA\u0022:\u0022\\u590F\\u666E\\u723E\\u7279\\u62C9\\u7DAD\\u592B\u0022,\u0022TeamH\u0022:\u0022\\u675C\\u62DC\\u7C43\\u7403\\u6703\u0022,\u0022GTime\u0022:\u002202:00\u0022,\u0022MatchH\u0022:97,\u0022MatchA\u0022:109,\u0022AI_ALL\u0022:{\u0022Home\u0022:0,\u0022Away\u0022:2,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:3,\u0022Over\u0022:0,\u0022Under\u0022:0},\u0022Lid\u0022:\u0022LHSP3MLU160\u0022,\u0022Teamid_A\u0022:\u0022TaVRTNkltO0\u0022,\u0022Teamid_H\u0022:\u0022TDWH4Q4NLrk\u0022,\u0022LName_Map\u0022:{\u0022de-DE\u0022:\u0022Europa - Euroleague\u0022,\u0022en-US\u0022:\u0022Europe - Euroleague\u0022,\u0022es-ES\u0022:\u0022Europe - Euroleague\u0022,\u0022fr-FR\u0022:\u0022Europe - EuroLigue\u0022,\u0022ja-JP\u0022:\u0022\\u30E8\\u30FC\\u30ED\\u30C3\\u30D1 - \\u30E6\\u30FC\\u30ED\\u30EA\\u30FC\\u30B0\u0022,\u0022ko-KR\u0022:\u0022\\uC720\\uB7FD - \\uC720\\uB85C \\uB9AC\\uADF8\u0022,\u0022pt-PT\u0022:\u0022\u0022,\u0022th-TH\u0022:\u0022\\u0E22\\u0E38\\u0E42\\u0E23\\u0E1B - \\u0E22\\u0E39\\u0E42\\u0E23\\u0E25\\u0E35\\u0E01\u0022,\u0022vi-VN\u0022:\u0022Ch\\u00E2u \\u00C2u - Euroleague\u0022,\u0022zh-CN\u0022:\u0022\\u6B27\\u6D32\\u7BEE\\u7403\\u8054\\u8D5B\u0022,\u0022zh-TW\u0022:\u0022\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022},\u0022TeamAName_Map\u0022:{\u0022en-US\u0022:\u0022Hapoel Tel-Aviv\u0022,\u0022fr-FR\u0022:\u0022Hapo\\u00EBl Tel-Aviv\u0022,\u0022ja-JP\u0022:\u0022\\u30CF\\u30DD\\u30A8\\u30EB\\u30FB\\u30C6\\u30EB\\u30A2\\u30D3\\u30D6\u0022,\u0022ko-KR\u0022:\u0022\\uD558\\uD3EC\\uC5D8 \\uD154\\uC544\\uBE44\\uBE0C\u0022,\u0022th-TH\u0022:\u0022\\u0E2E\\u0E32\\u0E42\\u0E1B\\u0E40\\u0E2D\\u0E25 \\u0E40\\u0E17\\u0E25\\u0E2D\\u0E32\\u0E27\\u0E35\\u0E1F\u0022,\u0022zh-TW\u0022:\u0022\\u590F\\u666E\\u723E\\u7279\\u62C9\\u7DAD\\u592B\u0022},\u0022TeamHName_Map\u0022:{\u0022en-US\u0022:\u0022BC Dubai\u0022,\u0022fr-FR\u0022:\u0022BC Duba\\u00EF\u0022,\u0022ja-JP\u0022:\u0022BC\\u30C9\\u30D0\\u30A4\u0022,\u0022ko-KR\u0022:\u0022BC \\uB450\\uBC14\\uC774\u0022,\u0022th-TH\u0022:\u0022\\u0E1A\\u0E35\\u0E0B\\u0E35 \\u0E14\\u0E39\\u0E44\\u0E1A\u0022,\u0022zh-TW\u0022:\u0022\\u675C\\u62DC\\u7C43\\u7403\\u6703\u0022}}",
    "G5vRsNPDj50": "{\u0022League\u0022:\u0022\\u570B\\u969B\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022,\u0022TeamA\u0022:\u0022\\u6CE2\\u9686\\u90A3\u0022,\u0022TeamH\u0022:\u0022\\u5DF4\\u65AF\\u5E72\\u5C3C\\u4E9E\u0022,\u0022GTime\u0022:\u002203:30\u0022,\u0022MatchH\u0022:87,\u0022MatchA\u0022:76,\u0022AI_ALL\u0022:{\u0022Home\u0022:2,\u0022Away\u0022:0,\u0022Home_HA\u0022:2,\u0022Away_HA\u0022:1,\u0022Over\u0022:0,\u0022Under\u0022:0},\u0022Lid\u0022:\u0022LHSP3MLU160\u0022,\u0022Teamid_A\u0022:\u0022TOg4aTBmYPk\u0022,\u0022Teamid_H\u0022:\u0022T5ohaIRT6vk\u0022,\u0022LName_Map\u0022:{\u0022de-DE\u0022:\u0022Europa - Euroleague\u0022,\u0022en-US\u0022:\u0022Europe - Euroleague\u0022,\u0022es-ES\u0022:\u0022Europe - Euroleague\u0022,\u0022fr-FR\u0022:\u0022Europe - EuroLigue\u0022,\u0022ja-JP\u0022:\u0022\\u30E8\\u30FC\\u30ED\\u30C3\\u30D1 - \\u30E6\\u30FC\\u30ED\\u30EA\\u30FC\\u30B0\u0022,\u0022ko-KR\u0022:\u0022\\uC720\\uB7FD - \\uC720\\uB85C \\uB9AC\\uADF8\u0022,\u0022pt-PT\u0022:\u0022\u0022,\u0022th-TH\u0022:\u0022\\u0E22\\u0E38\\u0E42\\u0E23\\u0E1B - \\u0E22\\u0E39\\u0E42\\u0E23\\u0E25\\u0E35\\u0E01\u0022,\u0022vi-VN\u0022:\u0022Ch\\u00E2u \\u00C2u - Euroleague\u0022,\u0022zh-CN\u0022:\u0022\\u6B27\\u6D32\\u7BEE\\u7403\\u8054\\u8D5B\u0022,\u0022zh-TW\u0022:\u0022\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022},\u0022TeamAName_Map\u0022:{\u0022de-DE\u0022:\u0022Virtus Bologna\u0022,\u0022en-US\u0022:\u0022Virtus Bologna\u0022,\u0022es-ES\u0022:\u0022Virtus Bologna\u0022,\u0022fr-FR\u0022:\u0022Virtus Bologne\u0022,\u0022ja-JP\u0022:\u0022\\u30F4\\u30A3\\u30EB\\u30C8\\u30A5\\u30B9\\u30FB\\u30DC\\u30ED\\u30FC\\u30CB\\u30E3\u0022,\u0022ko-KR\u0022:\u0022\\uBE44\\uB974\\uD22C\\uC2A4 \\uBCFC\\uB85C\\uB0D0\u0022,\u0022pt-PT\u0022:\u0022Virtus Granarolo Bologna\u0022,\u0022th-TH\u0022:\u0022\\u0E27\\u0E35\\u0E23\\u0E4C\\u0E15\\u0E38\\u0E2A \\u0E42\\u0E1A\\u0E42\\u0E25\\u0E0D\\u0E0D\\u0E48\\u0E32\u0022,\u0022vi-VN\u0022:\u0022Virtus Bologna\u0022,\u0022zh-CN\u0022:\u0022\\u6CE2\\u9686\\u90A3\\u535A\\u6D1B\\u5C3C\\u4E9A\u0022,\u0022zh-TW\u0022:\u0022\\u6CE2\\u9686\\u90A3\\u535A\\u6D1B\\u5C3C\\u4E9E\u0022},\u0022TeamHName_Map\u0022:{\u0022de-DE\u0022:\u0022Baskonia Vitoria-Gasteiz\u0022,\u0022en-US\u0022:\u0022Baskonia Vitoria-Gasteiz\u0022,\u0022es-ES\u0022:\u0022Baskonia Vitoria-Gasteiz\u0022,\u0022fr-FR\u0022:\u0022Baskonia Vitoria-Gasteiz\u0022,\u0022ja-JP\u0022:\u0022\\u30D0\\u30B9\\u30B3\\u30CB\\u30A2\\u30FB\\u30D3\\u30C8\\u30EA\\u30A2\\uFF1D\\u30AC\\u30B9\\u30C6\\u30A3\\u30B9\u0022,\u0022ko-KR\u0022:\u0022\\uBC14\\uC2A4\\uCF54\\uB2C8\\uC544 \\uBE44\\uD1A0\\uB9AC\\uC544-\\uAC00\\uC2A4\\uD14C\\uC774\\uC988\u0022,\u0022pt-PT\u0022:\u0022Saski Baskonia\u0022,\u0022th-TH\u0022:\u0022\\u0E1A\\u0E32\\u0E2A\\u0E42\\u0E01\\u0E40\\u0E19\\u0E35\\u0E22 \\u0E1A\\u0E35\\u0E42\\u0E15\\u0E40\\u0E23\\u0E35\\u0E22-\\u0E01\\u0E32\\u0E2A\\u0E40\\u0E15\\u0E2D\\u0E34\\u0E0B\u0022,\u0022vi-VN\u0022:\u0022Baskonia Vitoria-Gasteiz\u0022,\u0022zh-CN\u0022:\u0022\\u7EF4\\u591A\\u5229\\u4E9A\\u52A0\\u65AF\\u63D0\\u4F0A\\u5179\\u5DF4\\u65AF\\u5E72\\u5C3C\\u4E9A\u0022,\u0022zh-TW\u0022:\u0022\\u7DAD\\u591A\\u5229\\u4E9E\\u52A0\\u65AF\\u63D0\\u4F0A\\u8332\\u5DF4\\u65AF\\u5E79\\u5C3C\\u4E9E\u0022}}",
    "G6Ud4uwe07k": "{\u0022League\u0022:\u0022\\u570B\\u969B\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022,\u0022TeamA\u0022:\u0022\\u827E\\u601D\\u7DAD\\u723E\u0022,\u0022TeamH\u0022:\u0022\\u8CBB\\u5167\\u5DF4\\u5207\u0022,\u0022GTime\u0022:\u002201:45\u0022,\u0022MatchH\u0022:81,\u0022MatchA\u0022:67,\u0022AI_ALL\u0022:{\u0022Home\u0022:0,\u0022Away\u0022:0,\u0022Home_HA\u0022:0,\u0022Away_HA\u0022:4,\u0022Over\u0022:1,\u0022Under\u0022:1},\u0022Lid\u0022:\u0022LHSP3MLU160\u0022,\u0022Teamid_A\u0022:\u0022TV3vuT7NZG0\u0022,\u0022Teamid_H\u0022:\u0022TGM1f2hu9Zk\u0022,\u0022LName_Map\u0022:{\u0022de-DE\u0022:\u0022Europa - Euroleague\u0022,\u0022en-US\u0022:\u0022Europe - Euroleague\u0022,\u0022es-ES\u0022:\u0022Europe - Euroleague\u0022,\u0022fr-FR\u0022:\u0022Europe - EuroLigue\u0022,\u0022ja-JP\u0022:\u0022\\u30E8\\u30FC\\u30ED\\u30C3\\u30D1 - \\u30E6\\u30FC\\u30ED\\u30EA\\u30FC\\u30B0\u0022,\u0022ko-KR\u0022:\u0022\\uC720\\uB7FD - \\uC720\\uB85C \\uB9AC\\uADF8\u0022,\u0022pt-PT\u0022:\u0022\u0022,\u0022th-TH\u0022:\u0022\\u0E22\\u0E38\\u0E42\\u0E23\\u0E1B - \\u0E22\\u0E39\\u0E42\\u0E23\\u0E25\\u0E35\\u0E01\u0022,\u0022vi-VN\u0022:\u0022Ch\\u00E2u \\u00C2u - Euroleague\u0022,\u0022zh-CN\u0022:\u0022\\u6B27\\u6D32\\u7BEE\\u7403\\u8054\\u8D5B\u0022,\u0022zh-TW\u0022:\u0022\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022},\u0022TeamAName_Map\u0022:{\u0022de-DE\u0022:\u0022ASVEL Lyon-Villeurbanne\u0022,\u0022en-US\u0022:\u0022ASVEL Lyon Villeurbanne\u0022,\u0022es-ES\u0022:\u0022Asvel Lyon Villeurbanne\u0022,\u0022fr-FR\u0022:\u0022ASVEL Lyon Villeurbanne\u0022,\u0022ja-JP\u0022:\u0022\\u30A2\\u30B9\\u30F4\\u30A7\\u30EB\\u30FB\\u30EA\\u30E8\\u30F3\\u30FB\\u30F4\\u30A3\\u30EB\\u30FC\\u30EB\\u30D0\\u30F3\\u30CC\u0022,\u0022ko-KR\u0022:\u0022ASVEL \\uB9AC\\uC639 \\uBE4C\\uB8B0\\uB974\\uBC18\u0022,\u0022pt-PT\u0022:\u0022ASVEL Lyon-Villeurbanne\u0022,\u0022th-TH\u0022:\u0022\\u0E41\\u0E2D\\u0E2A\\u0E40\\u0E27\\u0E25 \\u0E25\\u0E35\\u0E22\\u0E07 \\u0E27\\u0E34\\u0E25\\u0E40\\u0E25\\u0E2D\\u0E23\\u0E4C\\u0E1A\\u0E32\\u0E19\\u0E19\\u0E4C\u0022,\u0022vi-VN\u0022:\u0022ASVEL Lyon Villeurbanne\u0022,\u0022zh-CN\u0022:\u0022\\u827E\\u601D\\u7EF4\\u5C14\\u91CC\\u6602\\u7EF4\\u7EA6\\u73ED\u0022,\u0022zh-TW\u0022:\u0022\\u827E\\u601D\\u7DAD\\u723E\\u91CC\\u6602\\u7DAD\\u7D04\\u73ED\u0022},\u0022TeamHName_Map\u0022:{\u0022de-DE\u0022:\u0022Fenerbah\\u00E7e Istanbul\u0022,\u0022en-US\u0022:\u0022Fenerbahce Istanbul\u0022,\u0022es-ES\u0022:\u0022Fenerbahce Istanbul\u0022,\u0022fr-FR\u0022:\u0022Fenerbahce Istanbul\u0022,\u0022ja-JP\u0022:\u0022\\u30D5\\u30A7\\u30CD\\u30EB\\u30D0\\u30D5\\u30C1\\u30A7\\u30FB\\u30A4\\u30B9\\u30BF\\u30F3\\u30D6\\u30FC\\u30EB\u0022,\u0022ko-KR\u0022:\u0022\\uD398\\uB124\\uB974\\uBC14\\uCCB4 \\uC774\\uC2A4\\uD0C4\\uBD88\u0022,\u0022pt-PT\u0022:\u0022Fenerbahce\u0022,\u0022th-TH\u0022:\u0022\\u0E40\\u0E1F\\u0E40\\u0E19\\u0E23\\u0E4C\\u0E1A\\u0E32\\u0E2B\\u0E4C\\u0E40\\u0E0A\\u0E48 \\u0E2D\\u0E34\\u0E2A\\u0E15\\u0E31\\u0E19\\u0E1A\\u0E39\\u0E25\u0022,\u0022vi-VN\u0022:\u0022Fenerbahce Istanbul\u0022,\u0022zh-CN\u0022:\u0022\\u8D39\\u4F26\\u5DF4\\u6CBB\\u4F0A\\u65AF\\u5766\\u5821\u0022,\u0022zh-TW\u0022:\u0022\\u8CBB\\u502B\\u5DF4\\u6CBB\\u4F0A\\u65AF\\u5766\\u5821\u0022}}",
    "GVRLJ0NvqA0": "{\u0022League\u0022:\u0022\\u570B\\u969B\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022,\u0022TeamA\u0022:\u0022\\u6469\\u7D0D\\u54E5\u0022,\u0022TeamH\u0022:\u0022\\u99AC\\u5361\\u6BD4\\u7279\\u62C9\\u7DAD\\u592B\u0022,\u0022GTime\u0022:\u002204:00\u0022,\u0022MatchH\u0022:107,\u0022MatchA\u0022:112,\u0022AI_ALL\u0022:{\u0022Home\u0022:0,\u0022Away\u0022:3,\u0022Home_HA\u0022:2,\u0022Away_HA\u0022:1,\u0022Over\u0022:0,\u0022Under\u0022:0},\u0022Lid\u0022:\u0022LHSP3MLU160\u0022,\u0022Teamid_A\u0022:\u0022TrFEkkEeHtE\u0022,\u0022Teamid_H\u0022:\u0022TgkTIj86A0C\u0022,\u0022LName_Map\u0022:{\u0022de-DE\u0022:\u0022Europa - Euroleague\u0022,\u0022en-US\u0022:\u0022Europe - Euroleague\u0022,\u0022es-ES\u0022:\u0022Europe - Euroleague\u0022,\u0022fr-FR\u0022:\u0022Europe - EuroLigue\u0022,\u0022ja-JP\u0022:\u0022\\u30E8\\u30FC\\u30ED\\u30C3\\u30D1 - \\u30E6\\u30FC\\u30ED\\u30EA\\u30FC\\u30B0\u0022,\u0022ko-KR\u0022:\u0022\\uC720\\uB7FD - \\uC720\\uB85C \\uB9AC\\uADF8\u0022,\u0022pt-PT\u0022:\u0022\u0022,\u0022th-TH\u0022:\u0022\\u0E22\\u0E38\\u0E42\\u0E23\\u0E1B - \\u0E22\\u0E39\\u0E42\\u0E23\\u0E25\\u0E35\\u0E01\u0022,\u0022vi-VN\u0022:\u0022Ch\\u00E2u \\u00C2u - Euroleague\u0022,\u0022zh-CN\u0022:\u0022\\u6B27\\u6D32\\u7BEE\\u7403\\u8054\\u8D5B\u0022,\u0022zh-TW\u0022:\u0022\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022},\u0022TeamAName_Map\u0022:{\u0022de-DE\u0022:\u0022AS Monaco\u0022,\u0022en-US\u0022:\u0022AS Monaco\u0022,\u0022es-ES\u0022:\u0022\u0022,\u0022fr-FR\u0022:\u0022AS Monaco\u0022,\u0022ja-JP\u0022:\u0022AS\\u30E2\\u30CA\\u30B3\u0022,\u0022ko-KR\u0022:\u0022AS \\uBAA8\\uB098\\uCF54\u0022,\u0022pt-PT\u0022:\u0022\u0022,\u0022th-TH\u0022:\u0022\\u0E2D\\u0E32\\u0E41\\u0E2D\\u0E2A \\u0E42\\u0E21\\u0E19\\u0E32\\u0E42\\u0E01\u0022,\u0022vi-VN\u0022:\u0022AS Monaco\u0022,\u0022zh-CN\u0022:\u0022AS\\u6469\\u7EB3\\u54E5\u0022,\u0022zh-TW\u0022:\u0022\\u6469\\u7D0D\\u54E5\\u8DB3\\u7403\\u6703\u0022},\u0022TeamHName_Map\u0022:{\u0022de-DE\u0022:\u0022Maccabi Tel-Aviv\u0022,\u0022en-US\u0022:\u0022Maccabi Tel-Aviv\u0022,\u0022es-ES\u0022:\u0022Maccabi Tel-Aviv\u0022,\u0022fr-FR\u0022:\u0022Maccabi Tel-Aviv\u0022,\u0022ja-JP\u0022:\u0022\\u30DE\\u30C3\\u30AB\\u30D3\\u30FB\\u30C6\\u30EB\\u30A2\\u30D3\\u30D6\u0022,\u0022ko-KR\u0022:\u0022\\uB9C8\\uCE74\\uBE44 \\uD154-\\uC544\\uBE44\\uBE0C\u0022,\u0022pt-PT\u0022:\u0022Maccabi Tel Aviv\u0022,\u0022th-TH\u0022:\u0022\\u0E21\\u0E31\\u0E04\\u0E04\\u0E32\\u0E1A\\u0E35\\u0E49 \\u0E40\\u0E17\\u0E25-\\u0E2D\\u0E32\\u0E27\\u0E35\\u0E1F\u0022,\u0022vi-VN\u0022:\u0022Maccabi Tel Aviv\u0022,\u0022zh-CN\u0022:\u0022\\u9A6C\\u5361\\u6BD4\\u7279\\u62C9\\u7EF4\\u592B\u0022,\u0022zh-TW\u0022:\u0022\\u7279\\u62C9\\u7DAD\\u592B\\u99AC\\u5361\\u6BD4\u0022}}",
    "GzZYvWGFvEC": "{\u0022League\u0022:\u0022\\u570B\\u969B\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022,\u0022TeamA\u0022:\u0022\\u62DC\\u4EC1\\u6155\\u5C3C\\u9ED1\u0022,\u0022TeamH\u0022:\u0022\\u5DF4\\u9ECE\\u7C43\\u7403\\u4FF1\\u6A02\\u90E8\u0022,\u0022GTime\u0022:\u002204:00\u0022,\u0022MatchH\u0022:82,\u0022MatchA\u0022:86,\u0022AI_ALL\u0022:{\u0022Home\u0022:4,\u0022Away\u0022:0,\u0022Home_HA\u0022:3,\u0022Away_HA\u0022:0,\u0022Over\u0022:0,\u0022Under\u0022:0},\u0022Lid\u0022:\u0022LHSP3MLU160\u0022,\u0022Teamid_A\u0022:\u0022TUg82hXn7L0\u0022,\u0022Teamid_H\u0022:\u0022TeSxqDcAB3E\u0022,\u0022LName_Map\u0022:{\u0022de-DE\u0022:\u0022Europa - Euroleague\u0022,\u0022en-US\u0022:\u0022Europe - Euroleague\u0022,\u0022es-ES\u0022:\u0022Europe - Euroleague\u0022,\u0022fr-FR\u0022:\u0022Europe - EuroLigue\u0022,\u0022ja-JP\u0022:\u0022\\u30E8\\u30FC\\u30ED\\u30C3\\u30D1 - \\u30E6\\u30FC\\u30ED\\u30EA\\u30FC\\u30B0\u0022,\u0022ko-KR\u0022:\u0022\\uC720\\uB7FD - \\uC720\\uB85C \\uB9AC\\uADF8\u0022,\u0022pt-PT\u0022:\u0022\u0022,\u0022th-TH\u0022:\u0022\\u0E22\\u0E38\\u0E42\\u0E23\\u0E1B - \\u0E22\\u0E39\\u0E42\\u0E23\\u0E25\\u0E35\\u0E01\u0022,\u0022vi-VN\u0022:\u0022Ch\\u00E2u \\u00C2u - Euroleague\u0022,\u0022zh-CN\u0022:\u0022\\u6B27\\u6D32\\u7BEE\\u7403\\u8054\\u8D5B\u0022,\u0022zh-TW\u0022:\u0022\\u6B50\\u6D32\\u7C43\\u7403\\u806F\\u8CFD\u0022},\u0022TeamAName_Map\u0022:{\u0022de-DE\u0022:\u0022FC Bayern M\\u00FCnchen\u0022,\u0022en-US\u0022:\u0022Bayern Munich\u0022,\u0022es-ES\u0022:\u0022Bayern Munich\u0022,\u0022fr-FR\u0022:\u0022Bayern Munich\u0022,\u0022ja-JP\u0022:\u0022\\u30D0\\u30A4\\u30A8\\u30EB\\u30F3\\u30FB\\u30DF\\u30E5\\u30F3\\u30D8\\u30F3\u0022,\u0022ko-KR\u0022:\u0022\\uBC14\\uC774\\uC5D0\\uB978 \\uBB8C\\uD5E8\u0022,\u0022pt-PT\u0022:\u0022Bayern Munich\u0022,\u0022th-TH\u0022:\u0022\\u0E1A\\u0E32\\u0E40\\u0E22\\u0E34\\u0E23\\u0E4C\\u0E19\\u0E21\\u0E34\\u0E27\\u0E19\\u0E34\\u0E01\u0022,\u0022vi-VN\u0022:\u0022Bayern Munich\u0022,\u0022zh-CN\u0022:\u0022\\u62DC\\u4EC1\\u6155\\u5C3C\\u9ED1\u0022,\u0022zh-TW\u0022:\u0022\\u62DC\\u4EC1\\u6155\\u5C3C\\u9ED1\u0022},\u0022TeamHName_Map\u0022:{\u0022en-US\u0022:\u0022Paris Basketball\u0022,\u0022zh-CN\u0022:\u0022\\u5DF4\\u9ECE\\u7C43\\u7403\\u968A\u0022,\u0022zh-TW\u0022:\u0022\\u5DF4\\u9ECE\\u7C43\\u7403\\u4FF1\\u6A02\\u90E8\u0022}}"
  },
  "results": {
    "R1": "[{\u0022Mode\u0022:\u00221X2\u0022,\u0022Count\u0022:4,\u0022Win\u0022:3,\u0022Loss\u0022:1,\u0022Sum\u0022:840,\u0022High\u0022:0,\u0022Low\u0022:4,\u0022HighSum\u0022:0,\u0022LowSum\u0022:840,\u0022HighWin\u0022:0,\u0022LowWin\u0022:3,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:1},{\u0022Mode\u0022:\u0022HA\u0022,\u0022Count\u0022:5,\u0022Win\u0022:2,\u0022Loss\u0022:3,\u0022Sum\u0022:-1190,\u0022High\u0022:0,\u0022Low\u0022:1,\u0022HighSum\u0022:0,\u0022LowSum\u0022:-1000,\u0022HighWin\u0022:0,\u0022LowWin\u0022:0,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:1},{\u0022Mode\u0022:\u0022OU\u0022,\u0022Count\u0022:0,\u0022Win\u0022:0,\u0022Loss\u0022:0,\u0022Sum\u0022:0,\u0022High\u0022:0,\u0022Low\u0022:0,\u0022HighSum\u0022:0,\u0022LowSum\u0022:0,\u0022HighWin\u0022:0,\u0022LowWin\u0022:0,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:0}]",
    "R2": "[{\u0022Mode\u0022:\u00221X2\u0022,\u0022Count\u0022:4,\u0022Win\u0022:3,\u0022Loss\u0022:1,\u0022Sum\u0022:840,\u0022High\u0022:0,\u0022Low\u0022:4,\u0022HighSum\u0022:0,\u0022LowSum\u0022:840,\u0022HighWin\u0022:0,\u0022LowWin\u0022:3,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:1},{\u0022Mode\u0022:\u0022HA\u0022,\u0022Count\u0022:3,\u0022Win\u0022:1,\u0022Loss\u0022:2,\u0022Sum\u0022:-1090,\u0022High\u0022:0,\u0022Low\u0022:1,\u0022HighSum\u0022:0,\u0022LowSum\u0022:-1000,\u0022HighWin\u0022:0,\u0022LowWin\u0022:0,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:1},{\u0022Mode\u0022:\u0022OU\u0022,\u0022Count\u0022:0,\u0022Win\u0022:0,\u0022Loss\u0022:0,\u0022Sum\u0022:0,\u0022High\u0022:0,\u0022Low\u0022:0,\u0022HighSum\u0022:0,\u0022LowSum\u0022:0,\u0022HighWin\u0022:0,\u0022LowWin\u0022:0,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:0}]",
    "R3": "[{\u0022Mode\u0022:\u00221X2\u0022,\u0022Count\u0022:0,\u0022Win\u0022:0,\u0022Loss\u0022:0,\u0022Sum\u0022:0,\u0022High\u0022:0,\u0022Low\u0022:0,\u0022HighSum\u0022:0,\u0022LowSum\u0022:0,\u0022HighWin\u0022:0,\u0022LowWin\u0022:0,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:0},{\u0022Mode\u0022:\u0022HA\u0022,\u0022Count\u0022:0,\u0022Win\u0022:0,\u0022Loss\u0022:0,\u0022Sum\u0022:0,\u0022High\u0022:0,\u0022Low\u0022:0,\u0022HighSum\u0022:0,\u0022LowSum\u0022:0,\u0022HighWin\u0022:0,\u0022LowWin\u0022:0,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:0},{\u0022Mode\u0022:\u0022OU\u0022,\u0022Count\u0022:0,\u0022Win\u0022:0,\u0022Loss\u0022:0,\u0022Sum\u0022:0,\u0022High\u0022:0,\u0022Low\u0022:0,\u0022HighSum\u0022:0,\u0022LowSum\u0022:0,\u0022HighWin\u0022:0,\u0022LowWin\u0022:0,\u0022HighLoss\u0022:0,\u0022LowLoss\u0022:0}]"
  },
  "gdate": "2025-11-07",
  "gtype": "BK",
  "lid": "LHSP3MLU160"
}
```

## Table: botarticles

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.botarticles` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, account, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | content | text | 是 | — |  |
| 3 | predict | text | 是 | — |  |
| 4 | gdate | text | 是 | — | PK |
| 5 | gtype | text | 是 | — | CK |
| 6 | account | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": null,
  "content": "TXT",
  "predict": "TXT",
  "gdate": "2025-11-18",
  "gtype": "BK",
  "account": "E0ktyIGH2P5",
  "gid": "12345678"
}
```

## Table: botartsettings

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.botartsettings` |
| 引擎 | cassandra |
| Primary Key | (account) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | aihints | text | 是 | — |  |
| 2 | aimodes | text | 是 | — |  |
| 3 | articlesites | text | 是 | — |  |
| 4 | cansame | boolean | 是 | — |  |
| 5 | enabled | boolean | 是 | — |  |
| 6 | footers | text | 是 | — |  |
| 7 | gtypes | text | 是 | — |  |
| 8 | lastusetime | text | 是 | — |  |
| 9 | maxpost | int | 是 | — |  |
| 10 | mode | int | 是 | — |  |
| 11 | settings | text | 是 | — |  |
| 12 | titles | text | 是 | — |  |
| 13 | todohours | text | 是 | — |  |
| 14 | account | text | 是 | — | PK |

### Sample（first row）

```json
{
  "aihints": "1.\u672C\u6587\u7D04{0}\u5B57\u4EE5\u7E41\u9AD4\u4E2D\u6587\uFF0C\u4F7F\u7528\u53F0\u7063\u5E38\u7528\u8A9E,\u9069\u5408\u767C\u5E03\u5728\u793E\u7FA4\u5E73\u53F0\u7684\u8CBC\u6587\uFF0C\u4F7F\u7528\u8F15\u9B06\u3001\u76F4\u767D\u3001\u5E36\u9EDE\u5410\u69FD,\u907F\u514D\u4F7F\u7528\u8A9E\u6C23\u8A5E.2.\u56DE\u8986\u6587\u7D0410-15\u5B57\u8981\u8F15\u9B06\u3001\u5410\u69FD\u3001\u53CD\u8AF7\u9178\u6587\u7B49\u985E\u578B\u90FD\u6709",
  "aimodes": "0,aigamearticlev2,",
  "articlesites": "ptt",
  "cansame": true,
  "enabled": false,
  "footers": "",
  "gtypes": "BK,BS",
  "lastusetime": "2026-03-08 18:22",
  "maxpost": 1,
  "mode": 1,
  "settings": "RandomWords=0,0;Reply=1;MaxArticlePerGType=2;SmallDots=1",
  "titles": ",,------------------------------------",
  "todohours": "18,23",
  "account": "EslZWCpIKWk"
}
```

## Table: cannedpacks

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.cannedpacks` |
| 引擎 | cassandra |
| Primary Key | (usemode) clustering: (gtype, ptype, otype, version) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | content | text | 是 | — |  |
| 2 | gtype | text | 是 | — | CK |
| 3 | usemode | text | 是 | — | PK |
| 4 | ptype | text | 是 | — | CK |
| 5 | otype | text | 是 | — | CK |
| 6 | version | int | 是 | — | CK |

### Sample（first row）

```json
{
  "content": "\u9084\u7528\u554F\u55CE\uFF1F\u7576\u7136\u662F{0}\u8D0F\u554A\uFF01",
  "gtype": "T",
  "usemode": "3",
  "ptype": "HA",
  "otype": "T",
  "version": 1
}
```

## Table: commonarticles

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.commonarticles` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, account, articleid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | articletype | int | 是 | — |  |
| 3 | content | text | 是 | — |  |
| 4 | gid | text | 是 | — |  |
| 5 | predict | text | 是 | — |  |
| 6 | replies | list<text> | 是 | — |  |
| 7 | scores | int | 是 | — |  |
| 8 | sourcefile | text | 是 | — |  |
| 9 | gdate | text | 是 | — | PK |
| 10 | gtype | text | 是 | — | CK |
| 11 | account | text | 是 | — | CK |
| 12 | articleid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "addtime": 1779895587,
  "articletype": 1,
  "content": "\u4E9E\u7279\u862D\u5927\u5922\u60F3\u9632\u5B88\u806F\u76DF\u524D\u6BB5\u3001\u7C43\u677F\u7B2C1\uFF0C\u4E3B\u58342\u9023\u52DD\u6C23\u52E2\u4F73\uFF1B\u5C71\u8C93\u547D\u4E2D\u7387\u9AD8\u4F46\u5931\u8AA4\u591A\u3002\u770B\u597D\u5922\u60F3\u5B88\u4F4F\u4E3B\u5834\u518D\u4E0B\u4E00\u57CE\u3002",
  "gid": "GXaXoxRsJU0",
  "predict": "{\u0022GameType\u0022:\u0022BK\u0022,\u0022Lid\u0022:\u0022LfIat3iWVEG\u0022,\u0022GDate\u0022:\u00222026-05-28\u0022,\u0022GTime\u0022:null,\u0022Gid\u0022:\u0022GXaXoxRsJU0\u0022,\u0022MainBet\u0022:false,\u0022Mode\u0022:\u00221X2\u0022,\u0022Odd\u0022:0.69,\u0022OddType\u0022:\u0022A\u0022,\u0022Spread\u0022:\u00221X2\u0022,\u0022Point\u0022:1000,\u0022MatchA\u0022:-1,\u0022MatchH\u0022:-1,\u0022ArtcleSite\u0022:\u0022leisu\u0022}",
  "replies": null,
  "scores": 5,
  "sourcefile": "",
  "gdate": "2026-05-28",
  "gtype": "BK",
  "account": "ECxIxbqieIU",
  "articleid": "P5SaFT55iWeFFFVestMBcA"
}
```

## Table: inplayanalys

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.inplayanalys` |
| 引擎 | cassandra |
| Primary Key | (modekey) clustering: (gdate) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | scores | text | 是 | — |  |
| 2 | splits | text | 是 | — |  |
| 3 | spreads | text | 是 | — |  |
| 4 | gdate | text | 是 | — | CK |
| 5 | modekey | text | 是 | — | PK |

### Sample（first row）

```json
{
  "scores": "[{\u0022Key\u0022:\u00223\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022SpearmanRate\u0022:6.57,\u0022Weights\u0022:[1.15,-0.82]},{\u0022Key\u0022:\u00223\\u5206\\u7403\\u9032\\u7403\\u6578_C\u0022,\u0022SpearmanRate\u0022:6.57,\u0022Weights\u0022:[1.15,-0.82]},{\u0022Key\u0022:\u00222\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022SpearmanRate\u0022:0.93,\u0022Weights\u0022:[2.67,0.33]},{\u0022Key\u0022:\u00222\\u5206\\u7403\\u9032\\u7403\\u6578_C\u0022,\u0022SpearmanRate\u0022:0.93,\u0022Weights\u0022:[2.67,0.33]},{\u0022Key\u0022:\u0022\\u7F70\\u7403\\u9032\\u7403\\u6578\u0022,\u0022SpearmanRate\u0022:5.44,\u0022Weights\u0022:[1.67,0.67]},{\u0022Key\u0022:\u0022\\u7F70\\u7403\\u9032\\u7403\\u6578_C\u0022,\u0022SpearmanRate\u0022:5.44,\u0022Weights\u0022:[1.67,0.67]},{\u0022Key\u0022:\u0022\\u5269\\u9918\\u66AB\\u505C\\u6578\u0022,\u0022SpearmanRate\u0022:6.12,\u0022Weights\u0022:[0.63,-0.63]},{\u0022Key\u0022:\u0022\\u5269\\u9918\\u66AB\\u505C\\u6578_C\u0022,\u0022SpearmanRate\u0022:6.12,\u0022Weights\u0022:[0.63,-0.63]},{\u0022Key\u0022:\u0022\\u72AF\\u898F\\u6578\u0022,\u0022SpearmanRate\u0022:5,\u0022Weights\u0022:[0,-1]},{\u0022Key\u0022:\u0022\\u72AF\\u898F\\u6578_C\u0022,\u0022SpearmanRate\u0022:5,\u0022Weights\u0022:[0,-1]},{\u0022Key\u0022:\u0022\\u7F70\\u7403\\u547D\\u4E2D\\u7387\u0022,\u0022SpearmanRate\u0022:3.69,\u0022Weights\u0022:[19.8,-11.87]},{\u0022Key\u0022:\u0022\\u7F70\\u7403\\u547D\\u4E2D\\u7387_C\u0022,\u0022SpearmanRate\u0022:3.69,\u0022Weights\u0022:[19.8,-11.87]},{\u0022Key\u0022:\u0022\\u547D\\u4E2D\\u7387\u0022,\u0022SpearmanRate\u0022:1.92,\u0022Weights\u0022:[0.16,0.08]},{\u0022Key\u0022:\u0022\\u547D\\u4E2D\\u7387_C\u0022,\u0022SpearmanRate\u0022:1.92,\u0022Weights\u0022:[0.16,0.08]},{\u0022Key\u0022:\u00223\\u5206\\u7403\\u547D\\u4E2D\\u7387\u0022,\u0022SpearmanRate\u0022:-3.01,\u0022Weights\u0022:[0.21,0.11]},{\u0022Key\u0022:\u00223\\u5206\\u7403\\u547D\\u4E2D\\u7387_C\u0022,\u0022SpearmanRate\u0022:-3.01,\u0022Weights\u0022:[0.21,0.11]},{\u0022Key\u0022:\u0022\\u9032\\u653B\\u7C43\\u677F\u0022,\u0022SpearmanRate\u0022:4.66,\u0022Weights\u0022:[1,-0.67]},{\u0022Key\u0022:\u0022\\u9032\\u653B\\u7C43\\u677F_C\u0022,\u0022SpearmanRate\u0022:4.66,\u0022Weights\u0022:[1,-0.67]},{\u0022Key\u0022:\u0022\\u9632\\u5B88\\u7C43\\u677F\u0022,\u0022SpearmanRate\u0022:8.33,\u0022Weights\u0022:[2.33,-0.33]},{\u0022Key\u0022:\u0022\\u9632\\u5B88\\u7C43\\u677F_C\u0022,\u0022SpearmanRate\u0022:8.33,\u0022Weights\u0022:[2.33,-0.33]},{\u0022Key\u0022:\u0022\\u52A9\\u653B\u0022,\u0022SpearmanRate\u0022:1.79,\u0022Weights\u0022:[2.33,0.67]},{\u0022Key\u0022:\u0022\\u52A9\\u653B_C\u0022,\u0022SpearmanRate\u0022:1.79,\u0022Weights\u0022:[2.33,0.67]},{\u0022Key\u0022:\u0022\\u6284\\u622A\u0022,\u0022SpearmanRate\u0022:1.11,\u0022Weights\u0022:[0.33,-1.67]},{\u0022Key\u0022:\u0022\\u6284\\u622A_C\u0022,\u0022SpearmanRate\u0022:1.11,\u0022Weights\u0022:[0.33,-1.67]},{\u0022Key\u0022:\u0022\\u963B\\u653B\u0022,\u0022SpearmanRate\u0022:0,\u0022Weights\u0022:[0,0]},{\u0022Key\u0022:\u0022\\u963B\\u653B_C\u0022,\u0022SpearmanRate\u0022:0,\u0022Weights\u0022:[0,0]},{\u0022Key\u0022:\u0022\\u5931\\u8AA4\u0022,\u0022SpearmanRate\u0022:-3.16,\u0022Weights\u0022:[1.33,-2]},{\u0022Key\u0022:\u0022\\u5931\\u8AA4_C\u0022,\u0022SpearmanRate\u0022:-3.16,\u0022Weights\u0022:[1.33,-2]},{\u0022Key\u0022:\u0022\\u72AF\\u898F\u0022,\u0022SpearmanRate\u0022:-7.32,\u0022Weights\u0022:[1.33,-2]},{\u0022Key\u0022:\u0022\\u72AF\\u898F_C\u0022,\u0022SpearmanRate\u0022:-7.32,\u0022Weights\u0022:[1.33,-2]}]",
  "splits": "{\u0022Accuracy\u0022:1,\u0022Rule\u0022:null,\u0022Thresholds\u0022:[14.785],\u0022GameCount\u0022:6}",
  "spreads": "",
  "gdate": "2026-05-04",
  "modekey": "BK_LfIat3iWVEG_11_HA_M"
}
```

## Table: inplaylogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.inplaylogs` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | lid | text | 是 | — |  |
| 2 | logdata | map<text, text> | 是 | — |  |
| 3 | match_a | int | 是 | — |  |
| 4 | match_h | int | 是 | — |  |
| 5 | gdate | text | 是 | — | PK |
| 6 | gtype | text | 是 | — | CK |
| 7 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "lid": "LmQUrjiej3U",
  "logdata": {
    "00:00": "[{\u0022Type\u0022:\u00221X2\u0022,\u0022Home\u0022:217,\u0022Away\u0022:3010},{\u0022Type\u0022:\u0022HA-9\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022OU-165.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0}]",
    "Q1 00": "[{\u0022Type\u0022:\u00223\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:3,\u0022Away\u0022:2},{\u0022Type\u0022:\u00222\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:5,\u0022Away\u0022:5},{\u0022Type\u0022:\u0022\\u7F70\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:2,\u0022Away\u0022:3},{\u0022Type\u0022:\u0022\\u5269\\u9918\\u66AB\\u505C\\u6578\u0022,\u0022Home\u0022:5,\u0022Away\u0022:5},{\u0022Type\u0022:\u0022\\u72AF\\u898F\\u6578\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022\\u7F70\\u7403\\u547D\\u4E2D\\u7387\u0022,\u0022Home\u0022:66.7,\u0022Away\u0022:60},{\u0022Type\u0022:\u0022\\u7E3D\\u66AB\\u505C\\u6578\u0022,\u0022Home\u0022:5,\u0022Away\u0022:5},{\u0022Type\u0022:\u0022\\u7E3D\\u5206\u0022,\u0022Home\u0022:21,\u0022Away\u0022:19},{\u0022Type\u0022:\u0022\\u6BD4\\u5206\u0022,\u0022Home\u0022:21,\u0022Away\u0022:19},{\u0022Type\u0022:\u00221X2\u0022,\u0022Home\u0022:218,\u0022Away\u0022:3000},{\u0022Type\u0022:\u0022HA-8.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022MHA-4\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022MSHA-4.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022OU-167\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022MOU-82\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022MSOU-81.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0}]",
    "Q2 00": "[{\u0022Type\u0022:\u00223\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:5,\u0022Away\u0022:3},{\u0022Type\u0022:\u00222\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:8,\u0022Away\u0022:13},{\u0022Type\u0022:\u0022\\u7F70\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:7,\u0022Away\u0022:10},{\u0022Type\u0022:\u0022\\u5269\\u9918\\u66AB\\u505C\\u6578\u0022,\u0022Home\u0022:3,\u0022Away\u0022:4},{\u0022Type\u0022:\u0022\\u72AF\\u898F\\u6578\u0022,\u0022Home\u0022:5,\u0022Away\u0022:5},{\u0022Type\u0022:\u0022\\u7F70\\u7403\\u547D\\u4E2D\\u7387\u0022,\u0022Home\u0022:77.8,\u0022Away\u0022:76.9},{\u0022Type\u0022:\u0022\\u7E3D\\u66AB\\u505C\\u6578\u0022,\u0022Home\u0022:4,\u0022Away\u0022:4},{\u0022Type\u0022:\u0022\\u7E3D\\u5206\u0022,\u0022Home\u0022:38,\u0022Away\u0022:45},{\u0022Type\u0022:\u0022\\u6BD4\\u5206\u0022,\u0022Home\u0022:38,\u0022Away\u0022:45},{\u0022Type\u0022:\u00221X2\u0022,\u0022Home\u0022:500,\u0022Away\u0022:1485},{\u0022Type\u0022:\u0022HA-4.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022OU-167.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0}]",
    "Q3 00": "[{\u0022Type\u0022:\u00223\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:10,\u0022Away\u0022:3},{\u0022Type\u0022:\u00222\\u5206\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:10,\u0022Away\u0022:19},{\u0022Type\u0022:\u0022\\u7F70\\u7403\\u9032\\u7403\\u6578\u0022,\u0022Home\u0022:11,\u0022Away\u0022:11},{\u0022Type\u0022:\u0022\\u5269\\u9918\\u66AB\\u505C\\u6578\u0022,\u0022Home\u0022:3,\u0022Away\u0022:3},{\u0022Type\u0022:\u0022\\u72AF\\u898F\\u6578\u0022,\u0022Home\u0022:4,\u0022Away\u0022:6},{\u0022Type\u0022:\u0022\\u7F70\\u7403\\u547D\\u4E2D\\u7387\u0022,\u0022Home\u0022:64.7,\u0022Away\u0022:73.3},{\u0022Type\u0022:\u0022\\u7E3D\\u66AB\\u505C\\u6578\u0022,\u0022Home\u0022:3,\u0022Away\u0022:3},{\u0022Type\u0022:\u0022\\u7E3D\\u5206\u0022,\u0022Home\u0022:61,\u0022Away\u0022:58},{\u0022Type\u0022:\u0022\\u6BD4\\u5206\u0022,\u0022Home\u0022:61,\u0022Away\u0022:58},{\u0022Type\u0022:\u00221X2\u0022,\u0022Home\u0022:684,\u0022Away\u0022:1100},{\u0022Type\u0022:\u0022HA-1.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0},{\u0022Type\u0022:\u0022OU-162.5\u0022,\u0022Home\u0022:0,\u0022Away\u0022:0}]"
  },
  "match_a": 76,
  "match_h": 83,
  "gdate": "2025-11-07",
  "gtype": "BK",
  "gid": "G1CSdMnEAd0"
}
```

## Table: inplaysetttings

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.inplaysetttings` |
| 引擎 | cassandra |
| Primary Key | (gdate) clustering: (gtype, lid, gid) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | footer | text | 是 | — |  |
| 2 | title | text | 是 | — |  |
| 3 | gdate | text | 是 | — | PK |
| 4 | gtype | text | 是 | — | CK |
| 5 | lid | text | 是 | — | CK |
| 6 | gid | text | 是 | — | CK |

### Sample（first row）

```json
{
  "footer": "",
  "title": "\u9632\u5B88\u9435\u7246\u5C0D\u6C7A\u706B\u529B\u6230\u8266\uFF01\u5FEB\u8247vs\u7070\u72FC \u51CC\u6668\u6C7A\u6230\u660E\u5C3C\u8607\u9054",
  "gdate": "2026-02-09",
  "gtype": "BK",
  "lid": "LYr9egM00GV",
  "gid": "GAtMrkRTHUU"
}
```

## Table: sports_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.sports_BK` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | content | text | 是 | — |  |
| 3 | date | text | 是 | — |  |
| 4 | lang | text | 是 | — |  |
| 5 | link | text | 是 | — |  |
| 6 | sourcesite | text | 是 | — |  |
| 7 | tag | text | 是 | — |  |
| 8 | title | text | 是 | — |  |
| 9 | id | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: sports_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.sports_BS` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | content | text | 是 | — |  |
| 3 | date | text | 是 | — |  |
| 4 | lang | text | 是 | — |  |
| 5 | link | text | 是 | — |  |
| 6 | sourcesite | text | 是 | — |  |
| 7 | tag | text | 是 | — |  |
| 8 | title | text | 是 | — |  |
| 9 | id | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: sports_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.sports_FL` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | content | text | 是 | — |  |
| 3 | date | text | 是 | — |  |
| 4 | lang | text | 是 | — |  |
| 5 | link | text | 是 | — |  |
| 6 | sourcesite | text | 是 | — |  |
| 7 | tag | text | 是 | — |  |
| 8 | title | text | 是 | — |  |
| 9 | id | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: sports_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.sports_HL` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | content | text | 是 | — |  |
| 3 | date | text | 是 | — |  |
| 4 | lang | text | 是 | — |  |
| 5 | link | text | 是 | — |  |
| 6 | sourcesite | text | 是 | — |  |
| 7 | tag | text | 是 | — |  |
| 8 | title | text | 是 | — |  |
| 9 | id | text | 是 | — | PK |

### Sample（first row）

(empty table)

## Table: sports_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `news.sports_SC` |
| 引擎 | cassandra |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | addtime | bigint | 是 | — |  |
| 2 | content | text | 是 | — |  |
| 3 | date | text | 是 | — |  |
| 4 | lang | text | 是 | — |  |
| 5 | link | text | 是 | — |  |
| 6 | sourcesite | text | 是 | — |  |
| 7 | tag | text | 是 | — |  |
| 8 | title | text | 是 | — |  |
| 9 | id | text | 是 | — | PK |

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
