---
aidata_db_sync: true
engine: postgresql
db_name: aireviews
source: 192.168.9.231:5432
keyspace: AIReviews
table_count: 9
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-06-07T05:16:42.3034896Z
sync_log_id: 1835
---

# Tables

## Table: ai_conversation_repos

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.ai_conversation_repos` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('ai_conversation_repos_id_seq'::regclass) |  |
| 2 | project_path | character varying | 否 | — |  |
| 3 | service_name | character varying | 是 | — |  |
| 4 | first_seen_at | timestamp with time zone | 否 | now() |  |
| 5 | last_seen_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 7,
  "project_path": "crawleragent/stakeprovider",
  "service_name": null,
  "first_seen_at": "2026-05-28T08:07:04.585097Z",
  "last_seen_at": "2026-05-28T08:07:04.585097Z"
}
```

## Table: ai_conversation_sessions

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.ai_conversation_sessions` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('ai_conversation_sessions_id_seq'::regclass) |  |
| 2 | session_uuid | character varying | 否 | — |  |
| 3 | tool_id | bigint | 否 | — |  |
| 4 | ai_model | character varying | 是 | — |  |
| 5 | project_path | character varying | 否 | — |  |
| 6 | service_name | character varying | 是 | — |  |
| 7 | git_author | character varying | 是 | — |  |
| 8 | git_author_email | character varying | 是 | — |  |
| 9 | file_path | character varying | 否 | — |  |
| 10 | file_hash | character varying | 否 | — |  |
| 11 | session_start_at | timestamp with time zone | 否 | — |  |
| 12 | last_commit_at | timestamp with time zone | 是 | — |  |
| 13 | imported_at | timestamp with time zone | 否 | now() |  |
| 14 | is_deleted | boolean | 否 | false |  |
| 15 | deleted_from_gitlab_at | timestamp with time zone | 是 | — |  |
| 16 | created_at | timestamp with time zone | 否 | now() |  |
| 17 | updated_at | timestamp with time zone | 否 | now() |  |
| 18 | last_commit_sha | character varying | 是 | — |  |

### Sample（first row）

```json
{
  "id": 390,
  "session_uuid": "40a12013-2735-473a-8a0c-eddf68ab4425",
  "tool_id": 2,
  "ai_model": null,
  "project_path": "crawleragent/communityservice",
  "service_name": "communityservice",
  "git_author": "zb05",
  "git_author_email": null,
  "file_path": ".specstory/history/2026-05-26_03-24-45Z-scenario-flows-impact-analysis-requirement.md",
  "file_hash": "4c12e5c998e2b470032b24f6b366b56a4f5f9e1641fb5faafd07a3a8af24ec26",
  "session_start_at": "2026-05-26T03:24:45Z",
  "last_commit_at": "2026-06-04T06:35:13Z",
  "imported_at": "2026-06-04T06:35:20.402272Z",
  "is_deleted": false,
  "deleted_from_gitlab_at": null,
  "created_at": "2026-06-04T06:35:20.402272Z",
  "updated_at": "2026-06-04T06:35:20.402272Z",
  "last_commit_sha": "5af501f7c00b42ee6a51396926f7dac8ab10cc2d"
}
```

## Table: ai_conversation_tools

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.ai_conversation_tools` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('ai_conversation_tools_id_seq'::regclass) |  |
| 2 | tool_code | character varying | 否 | — |  |
| 3 | display_name | character varying | 是 | — |  |
| 4 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 1,
  "tool_code": "claude-code",
  "display_name": "Claude Code",
  "created_at": "2026-05-20T02:15:36.285207Z"
}
```

## Table: ai_conversation_turns

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.ai_conversation_turns` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('ai_conversation_turns_id_seq'::regclass) |  |
| 2 | session_id | bigint | 否 | — |  |
| 3 | sequence_order | integer | 否 | — |  |
| 4 | prompt | text | 否 | — |  |
| 5 | response | text | 否 | ''::text |  |
| 6 | ai_model | character varying | 是 | — |  |
| 7 | turn_at | timestamp with time zone | 否 | — |  |
| 8 | has_precise_timestamp | boolean | 否 | false |  |
| 9 | content_sanitized | boolean | 否 | false |  |
| 10 | has_sidechain | boolean | 否 | false |  |
| 11 | prompt_chars_raw | integer | 是 | — |  |
| 12 | response_chars_raw | integer | 是 | — |  |
| 13 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 1807,
  "session_id": 181,
  "sequence_order": 1,
  "prompt": "\u6AA2\u8996\u5206\u6790\u9019Plan,\u770B\u662F\u5426\u6709\u9700\u8981\u52A0\u5F37\u6216\u662F\u5176\u4ED6\u5F85\u78BA\u8A8D\u554F\u984C,\u5982\u6709\u52A0\u572814\u7AE0",
  "response": "[\u601D\u8003\u904E\u7A0B\u5DF2\u7701\u7565]\n\n---\n\n\u5148\u8B80\u53D6\u9019\u4EFD\u8A08\u756B\u6587\u4EF6\u3002\n\n---\n\n[\u5DE5\u5177: Read\uFF0Ccompleted]\n\n---\n\n[\u601D\u8003\u904E\u7A0B\u5DF2\u7701\u7565]\n\n---\n\n\u5206\u6790\u5B8C\u7562\uFF0C\u627E\u5230\u4EE5\u4E0B\u5E7E\u500B\u9700\u8981\u88DC\u5145\u81F3\u7B2C 14 \u7AE0\u7684\u5F85\u78BA\u8A8D\u554F\u984C\uFF0C\u6DB5\u84CB\uFF1Aidempotency\u3001\u4E26\u767C\u3001API \u8A8D\u8B49\u3001\u5927 diff\u3001\u964D\u7D1A\u7B56\u7565\u7B49\u3002\n\n---\n\n[\u5DE5\u5177: Edit\uFF0Ccompleted]\n\n---\n\n\u7B2C 14 \u7AE0\u65B0\u589E\u4E86 Q13\u2013Q24\uFF0C\u5171 12 \u500B\u5F85\u78BA\u8A8D\u554F\u984C\uFF0C\u5206\u985E\u5982\u4E0B\uFF1A\n\n**\u5DE5\u7A0B\u908A\u754C\u60C5\u6CC1**\n- **Q13** \u2014 Webhook Idempotency\uFF1AGitLab \u91CD\u8A66\u6642\u662F\u5426\u53BB\u91CD\u8907\uFF08\u5EFA\u8B70 unique index on commit_sha \u002B event_type\uFF09\n- **Q14** \u2014 \u4E26\u767C\u63A7\u5236\uFF1A10 \u4EBA\u540C\u6642 push \u6642 AI rate limit \u8207 \u0060MaxConcurrentReviews\u0060 \u9650\u5236\n- **Q18** \u2014 Rules git pull \u5931\u6557\uFF1A\u7528\u820A cache \u9084\u662F\u76F4\u63A5 fail\n\n**\u8A2D\u8A08\u6C7A\u7B56\uFF08\u5F71\u97FF\u5BE6\u4F5C\u8907\u96DC\u5EA6\uFF09**\n- **Q15** \u2014 Review API \u8A8D\u8B49\uFF1AX-API-Key \u6216\u63A5 ECService \u65E2\u6709\u8A8D\u8B49\n- **Q16** \u2014 \u5927 Diff \u8655\u7406\u7B56\u7565\uFF1A\u622A\u65B7 / \u512A\u5148\u53D6\u6A94\u6848 / \u5206\u6279\u5408\u4F75\uFF0C\u4E09\u9078\u4E00\n- **Q17** \u2014 AI \u5168\u639B\u964D\u7D1A\uFF1Apipeline \u8A2D pass \u002B \u901A\u77E5\uFF0C\u907F\u514D\u963B\u64CB\u7DCA\u6025\u4FEE\u5FA9\n- **Q19** \u2014 Push Branch Filter\uFF1A\u0060TriggerBranchPatterns\u0060 \u767D\u540D\u55AE\uFF0C\u907F\u514D\u91CD\u8907\u5BE9\u67E5 main\n\n**\u683C\u5F0F\u8207\u901A\u77E5\u7D30\u7BC0**\n- **Q20** \u2014 MR Comment Markdown \u683C\u5F0F\uFF08\u0060\u003Cdetails\u003E\u0060 \u6298\u758A\u5EFA\u8B70\uFF09\n- **Q21** \u2014 Rocket.Chat \u901A\u77E5\u53BB\u91CD\u8907 key \u5B9A\u7FA9\uFF08project_id \u002B commit_sha \u002B review_type\uFF09\n\n**\u5B89\u5168 / \u54C1\u8CEA**\n- **Q22** \u2014 Sensitive Data \u4E0D\u9032 Log \u7684\u898F\u7BC4\u65B9\u5F0F\n- **Q23** \u2014 Unit Test \u7B56\u7565\uFF08Service \u5C64 mock \u6E2C\u8A66\u7BC4\u570D\uFF09\n- **Q24** \u2014 Docker Volume \u8A2D\u8A08\u6B78\u5C6C\uFF08Plan \u88DC\u5145 vs DevOps \u90E8\u7F72\u6642\u8655\u7406\uFF09\n\n\u6700\u9AD8\u512A\u5148\u78BA\u8A8D\uFF1A**Q16\uFF08\u5927 Diff \u7B56\u7565\uFF09** \u548C **Q17\uFF08AI \u5168\u639B\u964D\u7D1A\uFF09**\uFF0C\u9019\u5169\u500B\u76F4\u63A5\u5F71\u97FF Phase 3 \u7684\u6838\u5FC3\u5BE6\u4F5C\u8DEF\u5F91\u3002",
  "ai_model": "claude-sonnet-4-6",
  "turn_at": "2026-05-05T09:11:28Z",
  "has_precise_timestamp": true,
  "content_sanitized": true,
  "has_sidechain": false,
  "prompt_chars_raw": 35,
  "response_chars_raw": 29978,
  "created_at": "2026-05-20T06:38:21.947212Z"
}
```

## Table: app_settings

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.app_settings` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | config_key | character varying | 否 | — |  |
| 2 | description | text | 否 | ''::text |  |
| 3 | config_json | jsonb | 否 | '{}'::jsonb |  |
| 4 | updated_at | timestamp with time zone | 否 | now() |  |
| 5 | updated_by | character varying | 是 | — |  |

### Sample（first row）

```json
{
  "config_key": "Core",
  "description": "Review \u4E3B\u4F47\u5217\u5BB9\u91CF\uFF08QueueCapacity\uFF09",
  "config_json": "{\u0022QueueCapacity\u0022: 100}",
  "updated_at": "2026-05-21T07:24:22.290912Z",
  "updated_by": "seed"
}
```

## Table: app_settings_meta

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.app_settings_meta` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | smallint | 否 | 1 |  |
| 2 | revision | bigint | 否 | 1 |  |
| 3 | updated_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 1,
  "revision": 53,
  "updated_at": "2026-06-07T02:51:11.945611Z"
}
```

## Table: review_events

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.review_events` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('review_events_id_seq'::regclass) |  |
| 2 | source_system | character varying | 否 | — |  |
| 3 | event_type | character varying | 否 | — |  |
| 4 | project_key | character varying | 否 | — |  |
| 5 | project_name | character varying | 是 | — |  |
| 6 | repository_url | text | 是 | — |  |
| 7 | branch_name | character varying | 是 | — |  |
| 8 | target_branch | character varying | 是 | — |  |
| 9 | commit_sha | character varying | 是 | — |  |
| 10 | merge_request_id | character varying | 是 | — |  |
| 11 | triggered_by | character varying | 是 | — |  |
| 12 | triggered_at | timestamp with time zone | 否 | now() |  |
| 13 | status | character varying | 否 | 'pending'::character varying |  |
| 14 | raw_payload | jsonb | 是 | — |  |
| 15 | last_notified_at | timestamp with time zone | 是 | — |  |
| 16 | created_at | timestamp with time zone | 否 | now() |  |
| 17 | updated_at | timestamp with time zone | 否 | now() |  |
| 18 | aidata_commit_sha | character varying | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source_system": "gitlab",
  "event_type": "push",
  "project_key": "biz/newlotterybackendservice",
  "project_name": "NewLotteryBackEndService",
  "repository_url": "https://git.zbdigital.net/biz/newlotterybackendservice.git",
  "branch_name": "master",
  "target_branch": null,
  "commit_sha": "209e53709c9ae6719b2f75170783fa299982ec71",
  "merge_request_id": null,
  "triggered_by": "zb00",
  "triggered_at": "2026-05-07T05:36:25.296264Z",
  "status": "completed",
  "raw_payload": "{\u0022ref\u0022: \u0022refs/heads/master\u0022, \u0022after\u0022: \u0022209e53709c9ae6719b2f75170783fa299982ec71\u0022, \u0022before\u0022: \u00221914927f8c367b0abf5528f3b6120907226a5369\u0022, \u0022commits\u0022: [{\u0022id\u0022: \u0022209e53709c9ae6719b2f75170783fa299982ec71\u0022, \u0022url\u0022: \u0022https://git.zbdigital.net/biz/newlotterybackendservice/-/commit/209e53709c9ae6719b2f75170783fa299982ec71\u0022, \u0022added\u0022: [\u0022NewLotteryBackEndService.DomainService/MemberService.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/DataAccess/MemberProvider.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/DataValidator/MemberValidator.cs\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IMemberService.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataAccess/IMemberProvider.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataValidator/IMemberValidator.cs\u0022, \u0022NewLotteryBackEndService.Model/Member/CoinWalletTransaction.cs\u0022, \u0022NewLotteryBackEndService.Model/Member/User.cs\u0022, \u0022NewLotteryBackEndService/Controllers/MemberController.cs\u0022], \u0022title\u0022: \u0022Merge branch \u0027pre\u0027 into \u0027master\u0027\u0022, \u0022author\u0022: {\u0022name\u0022: \u0022zb07\u0022, \u0022email\u0022: \u0022zbdigital007@gmail.com\u0022}, \u0022message\u0022: \u0022Merge branch \u0027pre\u0027 into \u0027master\u0027\\n\\nPre\\n\\nSee merge request biz/newlotterybackendservice!18\u0022, \u0022removed\u0022: [], \u0022modified\u0022: [\u0022NewLotteryBackEndService.DomainService/PaymentService.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/DataAccess/PaymentProvider.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/NewLotteryBackEndService.Infrastructure.csproj\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IBetPoolService.cs\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IChampionshipService.cs\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IPaymentService.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataAccess/IPaymentProvider.cs\u0022, \u0022NewLotteryBackEndService.Interface/NewLotteryBackEndService.Interface.csproj\u0022, \u0022NewLotteryBackEndService/Properties/launchSettings.json\u0022, \u0022NewLotteryBackEndService/appsettings.Local.json\u0022, \u0022NewLotteryBackEndService/appsettings.PRD.json\u0022], \u0022timestamp\u0022: \u00222026-03-17T14:20:46\u002B08:00\u0022}, {\u0022id\u0022: \u0022bf8758e03ac3cb19a510870d0cf1953c26890ad6\u0022, \u0022url\u0022: \u0022https://git.zbdigital.net/biz/newlotterybackendservice/-/commit/bf8758e03ac3cb19a510870d0cf1953c26890ad6\u0022, \u0022added\u0022: [\u0022NewLotteryBackEndService.DomainService/MemberService.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/DataAccess/MemberProvider.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/DataValidator/MemberValidator.cs\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IMemberService.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataAccess/IMemberProvider.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataValidator/IMemberValidator.cs\u0022, \u0022NewLotteryBackEndService.Model/Member/CoinWalletTransaction.cs\u0022, \u0022NewLotteryBackEndService.Model/Member/User.cs\u0022, \u0022NewLotteryBackEndService/Controllers/MemberController.cs\u0022], \u0022title\u0022: \u0022Merge branch \u0027local\u0027 into \u0027pre\u0027\u0022, \u0022author\u0022: {\u0022name\u0022: \u0022zb07\u0022, \u0022email\u0022: \u0022zbdigital007@gmail.com\u0022}, \u0022message\u0022: \u0022Merge branch \u0027local\u0027 into \u0027pre\u0027\\n\\nLocal\\n\\nSee merge request biz/newlotterybackendservice!17\u0022, \u0022removed\u0022: [], \u0022modified\u0022: [\u0022NewLotteryBackEndService.DomainService/PaymentService.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/DataAccess/PaymentProvider.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/NewLotteryBackEndService.Infrastructure.csproj\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IBetPoolService.cs\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IChampionshipService.cs\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IPaymentService.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataAccess/IPaymentProvider.cs\u0022, \u0022NewLotteryBackEndService.Interface/NewLotteryBackEndService.Interface.csproj\u0022, \u0022NewLotteryBackEndService/Properties/launchSettings.json\u0022, \u0022NewLotteryBackEndService/appsettings.Local.json\u0022, \u0022NewLotteryBackEndService/appsettings.PRD.json\u0022], \u0022timestamp\u0022: \u00222026-03-17T14:19:13\u002B08:00\u0022}, {\u0022id\u0022: \u00221914927f8c367b0abf5528f3b6120907226a5369\u0022, \u0022url\u0022: \u0022https://git.zbdigital.net/biz/newlotterybackendservice/-/commit/1914927f8c367b0abf5528f3b6120907226a5369\u0022, \u0022added\u0022: [\u0022NewLotteryBackEndService.Infrastructure/DataValidator/PaymentValidator.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataValidator/IPaymentValidator.cs\u0022, \u0022NewLotteryBackEndService.Model/Payment/NewLotteryRechargePlan.cs\u0022, \u0022NewLotteryBackEndService.Model/Payment/NewLotteryRechargePlanDTO.cs\u0022, \u0022NewLotteryBackEndService.Model/Payment/SportTradeOrder.cs\u0022, \u0022NewLotteryBackEndService/Controllers/PaymentController.cs\u0022], \u0022title\u0022: \u0022Merge branch \u0027local\u0027 of 192.168.9.234:biz/newlotterybackendservice into local\u0022, \u0022author\u0022: {\u0022name\u0022: \u0022zb07\u0022, \u0022email\u0022: \u0022zbdigital007@gmail.com\u0022}, \u0022message\u0022: \u0022Merge branch \u0027local\u0027 of 192.168.9.234:biz/newlotterybackendservice into local\\n\\n# Conflicts:\\n#\\tNewLotteryBackEndService.DomainService/PaymentService.cs\\n#\\tNewLotteryBackEndService.Interface/DomainService/IPaymentService.cs\\n#\\tNewLotteryBackEndService/appsettings.Local.json\\n#\\tNewLotteryBackEndService/appsettings.PRD.json\\n\u0022, \u0022removed\u0022: [], \u0022modified\u0022: [\u0022NewLotteryBackEndService.DomainService/PaymentService.cs\u0022, \u0022NewLotteryBackEndService.Infrastructure/DataAccess/PaymentProvider.cs\u0022, \u0022NewLotteryBackEndService.Interface/DomainService/IPaymentService.cs\u0022, \u0022NewLotteryBackEndService.Interface/Infrastructure/DataAccess/IPaymentProvider.cs\u0022, \u0022NewLotteryBackEndService/appsettings.Local.json\u0022, \u0022NewLotteryBackEndService/appsettings.PRD.json\u0022], \u0022timestamp\u0022: \u00222026-03-17T14:16:38\u002B08:00\u0022}], \u0022message\u0022: null, \u0022project\u0022: {\u0022id\u0022: 620, \u0022name\u0022: \u0022NewLotteryBackEndService\u0022, \u0022ssh_url\u0022: \u0022git@git.zbdigital.net:biz/newlotterybackendservice.git\u0022, \u0022web_url\u0022: \u0022https://git.zbdigital.net/biz/newlotterybackendservice\u0022, \u0022git_http_url\u0022: \u0022https://git.zbdigital.net/biz/newlotterybackendservice.git\u0022, \u0022path_with_namespace\u0022: \u0022biz/newlotterybackendservice\u0022}, \u0022user_id\u0022: 4, \u0022user_name\u0022: \u0022zb00\u0022, \u0022event_name\u0022: \u0022push\u0022, \u0022project_id\u0022: 620, \u0022repository\u0022: {\u0022url\u0022: \u0022git@git.zbdigital.net:biz/newlotterybackendservice.git\u0022, \u0022name\u0022: \u0022NewLotteryBackEndService\u0022, \u0022homepage\u0022: \u0022https://git.zbdigital.net/biz/newlotterybackendservice\u0022, \u0022description\u0022: \u0022\u0022, \u0022git_ssh_url\u0022: \u0022git@git.zbdigital.net:biz/newlotterybackendservice.git\u0022, \u0022git_http_url\u0022: \u0022https://git.zbdigital.net/biz/newlotterybackendservice.git\u0022, \u0022visibility_level\u0022: 10}, \u0022user_email\u0022: \u0022\u0022, \u0022object_kind\u0022: \u0022push\u0022, \u0022user_avatar\u0022: \u0022https://secure.gravatar.com/avatar/db299a91224aeeaf55da0c5dbc235c0e?s=80\u0026d=identicon\u0022, \u0022checkout_sha\u0022: \u0022209e53709c9ae6719b2f75170783fa299982ec71\u0022, \u0022push_options\u0022: {}, \u0022user_username\u0022: \u0022zb00\u0022, \u0022total_commits_count\u0022: 3}",
  "last_notified_at": null,
  "created_at": "2026-05-07T05:36:25.296264Z",
  "updated_at": "2026-05-07T05:36:32.337342Z",
  "aidata_commit_sha": null
}
```

## Table: review_issues

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.review_issues` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('review_issues_id_seq'::regclass) |  |
| 2 | run_id | bigint | 否 | — |  |
| 3 | rule_id | character varying | 是 | — |  |
| 4 | severity | character varying | 否 | — |  |
| 5 | category | character varying | 是 | — |  |
| 6 | file_path | text | 是 | — |  |
| 7 | line_start | integer | 是 | — |  |
| 8 | line_end | integer | 是 | — |  |
| 9 | title | character varying | 是 | — |  |
| 10 | description | text | 是 | — |  |
| 11 | suggestion | text | 是 | — |  |
| 12 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 1,
  "run_id": 3,
  "rule_id": null,
  "severity": "critical",
  "category": null,
  "file_path": null,
  "line_start": null,
  "line_end": null,
  "title": "\u5F85\u78BA\u8A8D\u554F\u984C\u672A\u89E3\u6C7A",
  "description": "Q1 \u72C0\u614B\u70BA \u2B1C \u5F85\u78BA\u8A8D\uFF0C\u6839\u64DA\u901A\u7528\u6AA2\u67E5\u898F\u7BC4\uFF0Ccommit \u6642\u4E0D\u5F97\u5B58\u5728\u672A\u78BA\u8A8D\u554F\u984C\u3002\u9700\u78BA\u8A8D pricecenterservice.json \u5BE6\u969B\u6A94\u6848\u8DEF\u5F91\u4E26\u66F4\u65B0\u72C0\u614B\u70BA \u2705 \u5DF2\u78BA\u8A8D\u6216 \uD83D\uDEAB \u4E0D\u9069\u7528\u3002",
  "suggestion": null,
  "created_at": "2026-05-09T02:46:18.577962Z"
}
```

## Table: review_runs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `AIReviews.public.review_runs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('review_runs_id_seq'::regclass) |  |
| 2 | event_id | bigint | 否 | — |  |
| 3 | review_type | character varying | 否 | — |  |
| 4 | status | character varying | 否 | — |  |
| 5 | rule_profile | character varying | 是 | — |  |
| 6 | rules_version | character varying | 是 | — |  |
| 7 | ai_provider | character varying | 是 | — |  |
| 8 | ai_model | character varying | 是 | — |  |
| 9 | started_at | timestamp with time zone | 是 | — |  |
| 10 | finished_at | timestamp with time zone | 是 | — |  |
| 11 | duration_ms | integer | 是 | — |  |
| 12 | summary | text | 是 | — |  |
| 13 | ai_feedback | text | 是 | — |  |
| 14 | ai_raw_response | jsonb | 是 | — |  |
| 15 | total_issues | integer | 否 | 0 |  |
| 16 | critical_count | integer | 否 | 0 |  |
| 17 | high_count | integer | 否 | 0 |  |
| 18 | medium_count | integer | 否 | 0 |  |
| 19 | low_count | integer | 否 | 0 |  |
| 20 | error_message | text | 是 | — |  |
| 21 | created_at | timestamp with time zone | 否 | now() |  |
| 22 | selected_rule_sources | jsonb | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "event_id": 1,
  "review_type": "code",
  "status": "passed",
  "rule_profile": "csharp_default",
  "rules_version": "local",
  "ai_provider": "deepseek",
  "ai_model": "deepseek-reasoner",
  "started_at": "2026-05-07T05:36:25.998686Z",
  "finished_at": "2026-05-07T05:36:32.300657Z",
  "duration_ms": 6301,
  "summary": "No diff or context provided. Unable to perform code review. Please ensure that the GitLab token is configured or the hook payload contains the diff.",
  "ai_feedback": "No diff or context provided. Unable to perform code review. Please ensure that the GitLab token is configured or the hook payload contains the diff.",
  "ai_raw_response": null,
  "total_issues": 0,
  "critical_count": 0,
  "high_count": 0,
  "medium_count": 0,
  "low_count": 0,
  "error_message": null,
  "created_at": "2026-05-07T05:36:25.97629Z",
  "selected_rule_sources": null
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
