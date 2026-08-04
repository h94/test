---
aidata_db_sync: true
engine: postgresql
db_name: bussinessmember
source: 192.168.9.231:5432
keyspace: BusinessMember
table_count: 3
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-06-10T06:22:14.9340338Z
sync_log_id: 2484
---

# Tables

## Table: admins

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `BusinessMember.public.admins` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | account | text | 否 | — |  |
| 2 | password | text | 否 | — |  |
| 3 | username | text | 否 | — |  |
| 5 | level | integer | 否 | 0 |  |
| 6 | active | boolean | 否 | true |  |
| 7 | last_login_at | timestamp with time zone | 是 | — |  |
| 9 | deleted_at | timestamp with time zone | 是 | — |  |
| 10 | updated_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "account": "itest_kick_75620",
  "password": "***",
  "username": "Kick Target",
  "level": 10,
  "active": false,
  "last_login_at": null,
  "deleted_at": null,
  "updated_at": "2026-06-05T01:10:14.907773Z"
}
```

## Table: admin_login_logs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `BusinessMember.public.admin_login_logs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('admin_login_logs_id_seq'::regclass) |  |
| 2 | admin_account | text | 是 | — |  |
| 3 | account | text | 否 | — |  |
| 4 | success | boolean | 否 | — |  |
| 5 | failure_reason | text | 是 | — |  |
| 6 | login_ip | text | 是 | — |  |
| 7 | user_agent | text | 是 | — |  |
| 8 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 1,
  "admin_account": "superadmin",
  "account": "superadmin",
  "success": true,
  "failure_reason": null,
  "login_ip": "127.0.0.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
  "created_at": "2026-06-04T06:19:16.173925Z"
}
```

## Table: admin_operation_logs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `BusinessMember.public.admin_operation_logs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('admin_operation_logs_id_seq'::regclass) |  |
| 2 | admin_account | text | 是 | — |  |
| 3 | username | text | 是 | — |  |
| 4 | action | text | 否 | — |  |
| 5 | target_type | text | 是 | — |  |
| 6 | target_account | text | 是 | — |  |
| 7 | target_key | text | 是 | — |  |
| 8 | before_data | jsonb | 是 | — |  |
| 9 | after_data | jsonb | 是 | — |  |
| 10 | request_ip | text | 是 | — |  |
| 11 | user_agent | text | 是 | — |  |
| 12 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 1,
  "admin_account": "superadmin",
  "username": "Super Admin",
  "action": "admin.create",
  "target_type": "admin",
  "target_account": "apitest_6676",
  "target_key": null,
  "before_data": "null",
  "after_data": "{\u0022email\u0022: null, \u0022level\u0022: 50, \u0022active\u0022: true, \u0022account\u0022: \u0022apitest_6676\u0022, \u0022username\u0022: \u0022API Test Admin\u0022}",
  "request_ip": "127.0.0.1",
  "user_agent": "python-requests/2.32.5",
  "created_at": "2026-06-04T08:47:56.516722Z"
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
