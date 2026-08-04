---
aidata_db_sync: true
engine: postgresql
db_name: Alert
source: 192.168.9.231:5432
keyspace: Alert
table_count: 23
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-07-28T08:55:53.2968900Z
sync_log_id: 12426
---

# Tables

## Table: alerts

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.alerts` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | character varying | 否 | — |  |
| 2 | created_at | timestamp with time zone | 否 | now() |  |
| 3 | updated_at | timestamp with time zone | 否 | now() |  |
| 4 | rule_code | character varying | 否 | — |  |
| 5 | level | character varying | 否 | — |  |
| 6 | status | character varying | 否 | 'pending'::character varying |  |
| 7 | operator_account | text | 是 | — |  |
| 8 | game_type | character varying | 否 | — |  |
| 9 | source | character varying | 否 | — |  |
| 10 | game_id | character varying | 否 | — |  |
| 11 | league_id | character varying | 是 | — |  |
| 12 | play_mode | character varying | 是 | — |  |
| 13 | spread | character varying | 是 | — |  |
| 14 | selection | character varying | 是 | — |  |
| 15 | detail | jsonb | 否 | — |  |
| 16 | threshold_snapshot | jsonb | 否 | — |  |
| 17 | game_info | jsonb | 是 | — |  |

### Sample（first row）

```json
{
  "id": "WBPMcUfMeZSwmWfoqJTX5d",
  "created_at": "2026-07-28T06:10:44.084211Z",
  "updated_at": "2026-07-28T06:10:44.084211Z",
  "rule_code": "odds_spike",
  "level": "yellow",
  "status": "pending",
  "operator_account": null,
  "game_type": "sc",
  "source": "panda",
  "game_id": "2081982216635707394-2026-07-28",
  "league_id": "289882682225555528",
  "play_mode": "RBOU",
  "spread": "1.5",
  "selection": "U",
  "detail": "{\u0022current\u0022: 0.44, \u0022previous\u0022: 0.09, \u0022change_pct\u0022: 3.889}",
  "threshold_snapshot": "{\u0022red\u0022: 2.5, \u0022yellow\u0022: 2, \u0022dimension\u0022: \u0022postgresql \u002B RBOU\u0022, \u0022play_mode\u0022: \u0022RBOU\u0022}",
  "game_info": "{\u0022odds\u0022: {\u0022RBHA\u0022: {\u00220\u0022: {\u0022A\u0022: 0.43, \u0022H\u0022: 1.33}, \u0022-0.5\u0022: {\u0022A\u0022: 2.04, \u0022H\u0022: 0.16}, \u00220\u002B50\u0022: {\u0022A\u0022: 1.49, \u0022H\u0022: 0.35}}, \u0022RBOU\u0022: {\u00221.5\u0022: {\u0022O\u0022: 1.31, \u0022U\u0022: 0.44}, \u00222\u002B50\u0022: {\u0022O\u0022: 1.81, \u0022U\u0022: 0.23}}}, \u0022league\u0022: \u0022VS- International Friendly (Men) PANDA Exclusive EAFC24\u0022, \u0022source\u0022: \u0022panda\u0022, \u0022team_away\u0022: \u0022Spain\u0022, \u0022team_home\u0022: \u0022Iceland\u0022, \u0022away_score\u0022: 0, \u0022home_score\u0022: 1, \u0022game_status\u0022: \u00220\u0022, \u0022source_game_id\u0022: \u00222081982216635707394-2026-07-28\u0022, \u0022internal_game_id\u0022: null}"
}
```

## Table: alerts_archive

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.alerts_archive` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | character varying | 否 | — |  |
| 2 | created_at | timestamp with time zone | 否 | now() |  |
| 3 | updated_at | timestamp with time zone | 否 | now() |  |
| 4 | rule_code | character varying | 否 | — |  |
| 5 | level | character varying | 否 | — |  |
| 6 | status | character varying | 否 | 'pending'::character varying |  |
| 7 | operator_account | text | 是 | — |  |
| 8 | game_type | character varying | 否 | — |  |
| 9 | source | character varying | 否 | — |  |
| 10 | game_id | character varying | 否 | — |  |
| 11 | league_id | character varying | 是 | — |  |
| 12 | play_mode | character varying | 是 | — |  |
| 13 | spread | character varying | 是 | — |  |
| 14 | selection | character varying | 是 | — |  |
| 15 | detail | jsonb | 否 | — |  |
| 16 | threshold_snapshot | jsonb | 否 | — |  |
| 17 | game_info | jsonb | 是 | — |  |

### Sample（first row）

(empty table)

## Table: alert_change_log

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.alert_change_log` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('alert_change_log_id_seq'::regclass) |  |
| 2 | alert_id | character varying | 否 | — |  |
| 3 | field_name | text | 否 | — |  |
| 4 | old_value | text | 是 | — |  |
| 5 | new_value | text | 是 | — |  |
| 6 | operator_account | text | 否 | — |  |
| 7 | changed_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

(empty table)

## Table: config_direct_sync

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.config_direct_sync` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('config_direct_sync_id_seq'::regclass) |  |
| 2 | sitegid | text | 是 | — |  |
| 3 | status | text | 否 | 'pending'::text |  |
| 4 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 18115,
  "sitegid": "2076481273940951042-2026-07-13",
  "status": "done",
  "created_at": "2026-07-13T01:40:57.425324Z"
}
```

## Table: debounce_stats

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.debounce_stats` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | event_time | timestamp with time zone | 否 | — |  |
| 2 | source_id | character varying | 否 | — |  |
| 3 | source_game_id | character varying | 否 | — |  |
| 4 | play_mode | character varying | 否 | — |  |
| 5 | spread | character varying | 否 | — |  |
| 6 | selection | character varying | 否 | — |  |
| 7 | events_in_window | integer | 否 | — |  |
| 8 | max_price | numeric | 否 | — |  |
| 9 | min_price | numeric | 否 | — |  |
| 10 | final_price | numeric | 否 | — |  |

### Sample（first row）

```json
{
  "event_time": "2026-07-28T07:07:19.991Z",
  "source_id": "panda",
  "source_game_id": "5536469-2026-07-28",
  "play_mode": "OU",
  "spread": "2.5",
  "selection": "O",
  "events_in_window": 2,
  "max_price": 0.8800,
  "min_price": 0.8800,
  "final_price": 0.8800
}
```

## Table: effective_thresholds

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.effective_thresholds` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('effective_thresholds_id_seq'::regclass) |  |
| 2 | sitegid | text | 否 | — |  |
| 3 | source | text | 否 | — |  |
| 4 | gdate | text | 否 | — |  |
| 5 | sitelid | text | 否 | — |  |
| 6 | game_type | text | 否 | — |  |
| 7 | playmode | jsonb | 否 | — |  |
| 8 | created_at | timestamp with time zone | 否 | CURRENT_TIMESTAMP |  |

### Sample（first row）

```json
{
  "id": 1,
  "sitegid": "0a94ffdef9-2026-07-10",
  "source": "hga.com",
  "gdate": "2026-07-10",
  "sitelid": "\u4E2D\u570B\u8D85\u7D1A\u806F\u8CFD",
  "game_type": "SC",
  "playmode": "{\u0022HA\u0022: {\u0022spike_R\u0022: 0.3, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022OU\u0022: {\u0022spike_R\u0022: 0.2, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBHA\u0022: {\u0022spike_R\u0022: 0.2, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBOU\u0022: {\u0022spike_R\u0022: 0.2, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022Others-HalfHA\u0022: {\u0022spike_R\u0022: 0.2, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022Others-HalfOU\u0022: {\u0022spike_R\u0022: 0.2, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBOthers-HalfRBHA\u0022: {\u0022spike_R\u0022: 0.2, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBOthers-HalfRBOU\u0022: {\u0022spike_R\u0022: 0.2, \u0022spike_Y\u0022: 0.1, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.08, \u0022divergence_Y\u0022: 0.05, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}}",
  "created_at": "2026-07-10T01:23:40.177012Z"
}
```

## Table: export_tasks

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.export_tasks` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | character varying | 否 | — |  |
| 2 | status | character varying | 否 | 'pending'::character varying |  |
| 3 | query_params | jsonb | 否 | — |  |
| 4 | file_path | text | 是 | — |  |
| 5 | file_size_bytes | bigint | 是 | — |  |
| 6 | row_count | integer | 是 | — |  |
| 7 | error_message | text | 是 | — |  |
| 8 | created_at | timestamp with time zone | 否 | now() |  |
| 9 | started_at | timestamp with time zone | 是 | — |  |
| 10 | completed_at | timestamp with time zone | 是 | — |  |
| 11 | operator_account | text | 是 | — |  |

### Sample（first row）

(empty table)

## Table: game_status_history

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.game_status_history` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | event_time | timestamp with time zone | 否 | — |  |
| 2 | source_id | character varying | 否 | — |  |
| 3 | source_game_id | character varying | 否 | — |  |
| 4 | old_status | character varying | 否 | — |  |
| 5 | new_status | character varying | 否 | — |  |

### Sample（first row）

```json
{
  "event_time": "2026-07-28T07:08:32.592Z",
  "source_id": "panda",
  "source_game_id": "5541411-2026-07-28",
  "old_status": "0",
  "new_status": "1"
}
```

## Table: monitored_play_modes

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.monitored_play_modes` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | play_mode | jsonb | 否 | — |  |
| 3 | operator_account | text | 是 | — |  |
| 4 | created_at | timestamp with time zone | 否 | now() |  |
| 5 | updated_at | timestamp with time zone | 是 | — |  |

### Sample（first row）

```json
{
  "game_type": "BK",
  "play_mode": "{\u0022HA\u0022: 1, \u0022OU\u0022: 1, \u0022RBHA\u0022: 1, \u0022RBOU\u0022: 1, \u0022Others-HalfHA\u0022: 1, \u0022Others-HalfOU\u0022: 1, \u0022RBOthers-HalfRBHA\u0022: 1, \u0022RBOthers-HalfRBOU\u0022: 1}",
  "operator_account": "ZB05",
  "created_at": "2026-07-09T06:52:06.831188Z",
  "updated_at": null
}
```

## Table: odds_history_tier1

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.odds_history_tier1` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | event_time | timestamp with time zone | 否 | — |  |
| 2 | sport_type | character varying | 否 | — |  |
| 3 | source_id | character varying | 否 | — |  |
| 4 | source_game_id | character varying | 否 | — |  |
| 5 | internal_game_id | character varying | 是 | — |  |
| 6 | league_id | character varying | 否 | — |  |
| 7 | play_mode | character varying | 否 | — |  |
| 8 | spread | character varying | 否 | — |  |
| 9 | selection | character varying | 否 | — |  |
| 10 | price | numeric | 否 | — |  |
| 11 | change_pct | numeric | 是 | — |  |
| 12 | game_status | character varying | 否 | — |  |
| 13 | request_time | timestamp with time zone | 否 | — |  |

### Sample（first row）

```json
{
  "event_time": "2026-07-28T07:07:19.434Z",
  "sport_type": "SC",
  "source_id": "1xbet.com",
  "source_game_id": "0def5473c3-2026-07-28-14",
  "internal_game_id": null,
  "league_id": "FIFA 26. Amateur daily league",
  "play_mode": "RBHA",
  "spread": "1X2",
  "selection": "H",
  "price": 0.9500,
  "change_pct": null,
  "game_status": "0",
  "request_time": "2026-07-28T07:07:25.237118Z"
}
```

## Table: odds_history_tier2

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.odds_history_tier2` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | event_time | timestamp with time zone | 否 | — |  |
| 2 | sport_type | character varying | 否 | — |  |
| 3 | source_id | character varying | 否 | — |  |
| 4 | source_game_id | character varying | 否 | — |  |
| 5 | internal_game_id | character varying | 是 | — |  |
| 6 | league_id | character varying | 否 | — |  |
| 7 | play_mode | character varying | 否 | — |  |
| 8 | spread | character varying | 否 | — |  |
| 9 | selection | character varying | 否 | — |  |
| 10 | price | numeric | 否 | — |  |
| 11 | change_pct | numeric | 是 | — |  |
| 12 | game_status | character varying | 否 | — |  |
| 13 | request_time | timestamp with time zone | 否 | — |  |

### Sample（first row）

```json
{
  "event_time": "2026-07-28T07:07:19.427Z",
  "sport_type": "BK",
  "source_id": "1xbet.com",
  "source_game_id": "0305ea3b75-2026-07-28-14",
  "internal_game_id": null,
  "league_id": "BSKT Cup",
  "play_mode": "RBHA",
  "spread": "-27.5",
  "selection": "H",
  "price": 0.9200,
  "change_pct": null,
  "game_status": "0",
  "request_time": "2026-07-28T07:07:25.240118Z"
}
```

## Table: odds_history_tier3

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.odds_history_tier3` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | event_time | timestamp with time zone | 否 | — |  |
| 2 | sport_type | character varying | 否 | — |  |
| 3 | source_id | character varying | 否 | — |  |
| 4 | source_game_id | character varying | 否 | — |  |
| 5 | internal_game_id | character varying | 是 | — |  |
| 6 | league_id | character varying | 否 | — |  |
| 7 | play_mode | character varying | 否 | — |  |
| 8 | spread | character varying | 否 | — |  |
| 9 | selection | character varying | 否 | — |  |
| 10 | price | numeric | 否 | — |  |
| 11 | change_pct | numeric | 是 | — |  |
| 12 | game_status | character varying | 否 | — |  |
| 13 | request_time | timestamp with time zone | 否 | — |  |

### Sample（first row）

(empty table)

## Table: oddthreshold_game_setting

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.oddthreshold_game_setting` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | sitegid | text | 否 | — |  |
| 2 | source | text | 否 | — |  |
| 3 | gdate | text | 否 | — |  |
| 4 | sitelid | text | 否 | — |  |
| 5 | game_type | text | 否 | — |  |
| 6 | playmode | jsonb | 否 | — |  |
| 7 | operator_account | text | 是 | — |  |
| 8 | created_at | timestamp with time zone | 否 | now() |  |
| 9 | updated_at | timestamp with time zone | 是 | — |  |

### Sample（first row）

(empty table)

## Table: oddthreshold_league_setting

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.oddthreshold_league_setting` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | sitelid | text | 否 | — |  |
| 2 | source | text | 否 | — |  |
| 3 | game_type | text | 否 | — |  |
| 4 | playmode | jsonb | 否 | — |  |
| 5 | operator_account | text | 是 | — |  |
| 6 | created_at | timestamp with time zone | 否 | now() |  |
| 7 | updated_at | timestamp with time zone | 是 | — |  |

### Sample（first row）

(empty table)

## Table: oddthreshold_sport_setting

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.oddthreshold_sport_setting` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | playmode | jsonb | 否 | — |  |
| 3 | operator_account | text | 是 | — |  |
| 4 | created_at | timestamp with time zone | 否 | now() |  |
| 5 | updated_at | timestamp with time zone | 是 | — |  |

### Sample（first row）

```json
{
  "game_type": "SC",
  "playmode": "{\u0022HA\u0022: {\u0022spike_R\u0022: 2, \u0022spike_Y\u0022: 1.5, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.45, \u0022divergence_Y\u0022: 0.35, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022OU\u0022: {\u0022spike_R\u0022: 2, \u0022spike_Y\u0022: 1.5, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.45, \u0022divergence_Y\u0022: 0.35, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBHA\u0022: {\u0022spike_R\u0022: 2.5, \u0022spike_Y\u0022: 2, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.65, \u0022divergence_Y\u0022: 0.45, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBOU\u0022: {\u0022spike_R\u0022: 2.5, \u0022spike_Y\u0022: 2, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.65, \u0022divergence_Y\u0022: 0.45, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022Others-HalfHA\u0022: {\u0022spike_R\u0022: 2, \u0022spike_Y\u0022: 1.5, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.45, \u0022divergence_Y\u0022: 0.35, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022Others-HalfOU\u0022: {\u0022spike_R\u0022: 2, \u0022spike_Y\u0022: 1.5, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.45, \u0022divergence_Y\u0022: 0.35, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBOthers-HalfRBHA\u0022: {\u0022spike_R\u0022: 2.5, \u0022spike_Y\u0022: 2, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.65, \u0022divergence_Y\u0022: 0.45, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}, \u0022RBOthers-HalfRBOU\u0022: {\u0022spike_R\u0022: 2.5, \u0022spike_Y\u0022: 2, \u0022flutter_R\u0022: 20, \u0022flutter_Y\u0022: 15, \u0022divergence_R\u0022: 0.65, \u0022divergence_Y\u0022: 0.45, \u0022flutter_window_sec\u0022: 30, \u0022odds_stale_minutes\u0022: 10, \u0022source_stale_minutes\u0022: 5}}",
  "operator_account": "ZB05",
  "created_at": "2026-07-09T07:10:12.880561Z",
  "updated_at": "2026-07-13T03:31:32.086767Z"
}
```

## Table: scorethreshold_setting

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.scorethreshold_setting` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | setting | jsonb | 否 | — |  |
| 3 | operator_account | text | 是 | — |  |
| 4 | created_at | timestamp with time zone | 否 | now() |  |
| 5 | updated_at | timestamp with time zone | 是 | — |  |

### Sample（first row）

```json
{
  "game_type": "BK",
  "setting": "{\u0022divergence_R\u0022: 5.0, \u0022divergence_Y\u0022: 3.0, \u0022score_correction\u0022: 20.0, \u0022divergence_buffer_sec\u0022: 30.0}",
  "operator_account": "ZB05",
  "created_at": "2026-07-09T07:07:23.341172Z",
  "updated_at": "2026-07-09T07:07:47.560397Z"
}
```

## Table: score_history

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.score_history` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | event_time | timestamp with time zone | 否 | — |  |
| 2 | sport_type | character varying | 否 | — |  |
| 3 | source_id | character varying | 否 | — |  |
| 4 | source_game_id | character varying | 否 | — |  |
| 5 | home_score | integer | 否 | — |  |
| 6 | away_score | integer | 否 | — |  |
| 7 | total_score | integer | 否 | — |  |

### Sample（first row）

```json
{
  "event_time": "2026-07-28T07:07:19.434Z",
  "sport_type": "SC",
  "source_id": "1xbet.com",
  "source_game_id": "0def5473c3-2026-07-28-14",
  "home_score": 3,
  "away_score": 3,
  "total_score": 6
}
```

## Table: source_type

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.source_type` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | source | text | 否 | — |  |
| 2 | support_type | jsonb | 否 | — |  |
| 3 | operator_account | text | 否 | — |  |
| 4 | created_at | timestamp with time zone | 否 | now() |  |
| 5 | updated_at | timestamp with time zone | 是 | — |  |

### Sample（first row）

```json
{
  "source": "hga.com",
  "support_type": "{\u0022BK\u0022: \u0022full\u0022, \u0022BS\u0022: \u0022full\u0022, \u0022SC\u0022: \u0022full\u0022}",
  "operator_account": "ZB05",
  "created_at": "2026-07-09T06:58:34.422572Z",
  "updated_at": null
}
```

## Table: sport_alert_sources

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.sport_alert_sources` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | primary_source | text | 否 | — |  |
| 3 | secondary_sources | jsonb | 否 | '[]'::jsonb |  |
| 4 | operator_account | text | 是 | — |  |
| 5 | created_at | timestamp with time zone | 否 | now() |  |
| 6 | updated_at | timestamp with time zone | 是 | — |  |

### Sample（first row）

```json
{
  "game_type": "SC",
  "primary_source": "hga.com",
  "secondary_sources": "[\u0022panda\u0022, \u00221xbet.com\u0022]",
  "operator_account": "ZB05",
  "created_at": "2026-07-09T07:04:18.831632Z",
  "updated_at": null
}
```

## Table: threshold_changelog

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.threshold_changelog` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('threshold_changelog_id_seq'::regclass) |  |
| 2 | table_name | text | 否 | — |  |
| 3 | record_key | jsonb | 否 | — |  |
| 4 | play_mode | text | 是 | — |  |
| 5 | old_value | jsonb | 是 | — |  |
| 6 | new_value | jsonb | 是 | — |  |
| 7 | operator_account | text | 否 | — |  |
| 8 | changed_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

```json
{
  "id": 1,
  "table_name": "scorethreshold_setting",
  "record_key": "{\u0022game_type\u0022: \u0022SC\u0022}",
  "play_mode": null,
  "old_value": null,
  "new_value": "{\u0022divergence_R\u0022: 5.0, \u0022divergence_Y\u0022: 3.0, \u0022score_correction\u0022: 20.0, \u0022divergence_buffer_sec\u0022: 30.0}",
  "operator_account": "ZB05",
  "changed_at": "2026-07-06T08:14:54.201887Z"
}
```

## Table: threshold_sync_pending

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.threshold_sync_pending` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('threshold_sync_pending_id_seq'::regclass) |  |
| 2 | table_name | text | 否 | — |  |
| 3 | record_key | text | 否 | — |  |
| 4 | status | text | 否 | 'pending'::text |  |
| 5 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

(empty table)

## Table: webhook_logs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.webhook_logs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('webhook_logs_id_seq'::regclass) |  |
| 3 | trigger_event | text | 否 | — |  |
| 4 | alert_id | character varying | 是 | — |  |
| 5 | sent_at | timestamp with time zone | 否 | — |  |
| 6 | received_at | timestamp with time zone | 是 | — |  |
| 7 | request_payload | jsonb | 否 | — |  |
| 8 | success | boolean | 否 | — |  |
| 9 | http_status | integer | 是 | — |  |
| 10 | response_body | text | 是 | — |  |
| 11 | response_time_ms | integer | 是 | — |  |
| 12 | error_message | text | 是 | — |  |
| 13 | target_url | text | 否 | — |  |

### Sample（first row）

(empty table)

## Table: webhook_pending

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Alert.public.webhook_pending` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('webhook_pending_id_seq'::regclass) |  |
| 3 | alert_id | character varying | 否 | — |  |
| 4 | payload | jsonb | 否 | — |  |
| 5 | attempts | integer | 否 | 0 |  |
| 6 | next_retry_at | timestamp with time zone | 否 | now() |  |
| 7 | status | character varying | 否 | 'pending'::character varying |  |
| 8 | created_at | timestamp with time zone | 否 | now() |  |
| 9 | target_url | text | 否 | — |  |

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
