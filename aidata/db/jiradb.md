---
aidata_db_sync: true
engine: mysql
db_name: jiradb
source: 192.168.9.232:3306
keyspace: JiraDB
table_count: 5
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-07-29T01:47:14.2537096Z
sync_log_id: 12578
---

# Tables

## Table: Holidays

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `JiraDB.Holidays` |
| 引擎 | mysql |
| Primary Key | (Holyday) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | Holyday | date | 否 | — | PK |
| 2 | Name | char | 否 | — |  |
| 3 | Workday | int | 否 | 0 |  |

### Sample（first row）

```json
{
  "Holyday": "2023-02-28T00:00:00",
  "Name": "228",
  "Workday": 0
}
```

## Table: Issues

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `JiraDB.Issues` |
| 引擎 | mysql |
| Primary Key | (issuekey) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | issuekey | char | 否 | — | PK |
| 2 | sprintid | int | 否 | — |  |
| 3 | sprintdate | date | 否 | — |  |
| 4 | issuetype | char | 否 | — |  |
| 5 | storypoint | decimal | 否 | — |  |
| 6 | assignee | char | 否 | — |  |
| 7 | status | char | 否 | — |  |
| 8 | description | varchar | 否 | — |  |

### Sample（first row）

```json
{
  "issuekey": "TCZB-1903",
  "sprintid": 75,
  "sprintdate": "2022-08-01T00:00:00",
  "issuetype": "Story",
  "storypoint": 5,
  "assignee": "zb07",
  "status": "None",
  "description": "[\u6392\u884C\u699C] \u6392\u884C\u699CAPIService"
}
```

## Table: Sprints

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `JiraDB.Sprints` |
| 引擎 | mysql |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | int | 否 | — | PK |
| 2 | name | char | 否 | — |  |
| 3 | startdate | date | 否 | — |  |
| 4 | state | char | 否 | — |  |

### Sample（first row）

```json
{
  "id": 110,
  "name": "TCZB Sprint 103",
  "startdate": "2023-03-06T00:00:00",
  "state": "closed"
}
```

## Table: Subtasks

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `JiraDB.Subtasks` |
| 引擎 | mysql |
| Primary Key | (taskkey) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | taskkey | char | 否 | — | PK |
| 2 | issuekey | char | 否 | — |  |
| 3 | sprintid | int | 否 | — |  |
| 4 | tasktype | char | 否 | — |  |
| 5 | assignee | char | 否 | — |  |
| 6 | estimate | int | 否 | — |  |
| 7 | timespent | int | 否 | — |  |
| 8 | summary | varchar | 否 | — |  |

### Sample（first row）

```json
{
  "taskkey": "TCZB-1638",
  "issuekey": "TCZB-1583",
  "sprintid": 54,
  "tasktype": "Coding",
  "assignee": "zb07",
  "estimate": 300,
  "timespent": 300,
  "summary": "codeing - Ruei"
}
```

## Table: Worklogs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `JiraDB.Worklogs` |
| 引擎 | mysql |
| Primary Key | (id) |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | char | 否 | — | PK |
| 2 | author | char | 否 | — |  |
| 3 | logtype | char | 否 | — |  |
| 4 | timespent | int | 否 | — |  |
| 5 | created | datetime | 否 | — |  |
| 6 | comment | varchar | 否 | — |  |
| 7 | week | int | 否 | — |  |

### Sample（first row）

```json
{
  "id": "23385",
  "author": "zb09",
  "logtype": "Project",
  "timespent": 120,
  "created": "2022-06-02T16:00:45",
  "comment": "\u6587\u4EF6",
  "week": 22
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
