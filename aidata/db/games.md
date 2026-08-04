---
aidata_db_sync: true
engine: postgresql
db_name: games
source: 192.168.9.231:5432
keyspace: Games
table_count: 139
view_count: 0
trigger_count: 0
procedure_count: 0
function_count: 0
generated_at: 2026-07-07T10:19:33.8477359Z
sync_log_id: 8277
---

# Tables

## Table: aimerge_backtest_runs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_backtest_runs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | backtest_date | text | 否 | — |  |
| 3 | executed_at | timestamp with time zone | 否 | now() |  |
| 4 | sample_count | integer | 否 | — |  |
| 5 | before_error_count | integer | 否 | — |  |
| 6 | before_error_rate | double precision | 否 | — |  |
| 7 | after_error_count | integer | 否 | — |  |
| 8 | after_error_rate | double precision | 否 | — |  |
| 9 | improved_samples | jsonb | 是 | — |  |
| 10 | regression_samples | jsonb | 是 | — |  |

### Sample（first row）

(empty table)

## Table: aimerge_daily_reports

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_daily_reports` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | report_date | text | 否 | — |  |
| 3 | total_predictions | integer | 否 | — |  |
| 4 | auto_confirmed | integer | 否 | — |  |
| 5 | auto_error | integer | 否 | — |  |
| 6 | pending_confirmed | integer | 否 | — |  |
| 7 | pending_rejected | integer | 否 | — |  |
| 8 | inferred_confirmed | integer | 否 | 0 |  |
| 9 | inferred_rejected | integer | 否 | 0 |  |
| 10 | conflict_count | integer | 否 | — |  |
| 11 | error_breakdown | jsonb | 否 | — |  |
| 12 | suggestions | text | 是 | — |  |
| 13 | created_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

(empty table)

## Table: aimerge_historical_runs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_historical_runs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | target_date | text | 否 | — |  |
| 3 | started_at | timestamp with time zone | 否 | now() |  |
| 4 | job_id | text | 否 | — |  |
| 5 | status | text | 否 | — |  |
| 6 | site_a_game_count | integer | 否 | 0 |  |
| 7 | processed_pairs | integer | 否 | 0 |  |
| 8 | label_written | integer | 否 | 0 |  |
| 9 | finished_at | timestamp with time zone | 是 | — |  |
| 10 | error_message | text | 是 | — |  |

### Sample（first row）

(empty table)

## Table: aimerge_label_overrides

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_label_overrides` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | gdate | text | 否 | — |  |
| 3 | prediction_id | text | 否 | — |  |
| 4 | override_label | boolean | 否 | — |  |
| 5 | excluded_from_training | boolean | 否 | false |  |
| 6 | reason | text | 是 | — |  |
| 7 | reviewed_by | text | 是 | — |  |
| 8 | reviewed_at | timestamp with time zone | 否 | now() |  |
| 9 | source_b | text | 是 | — |  |
| 10 | game_a_sitegid | text | 是 | — |  |
| 11 | source_b_sitegid | text | 是 | — |  |

### Sample（first row）

(empty table)

## Table: aimerge_match_predictions

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_match_predictions` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | gdate | text | 否 | — |  |
| 3 | source_b | text | 否 | — |  |
| 4 | game_a_sitegid | text | 否 | — |  |
| 5 | source_b_sitegid | text | 否 | — |  |
| 6 | prediction_id | text | 否 | — |  |
| 7 | score | double precision | 否 | — |  |
| 8 | score_detail | jsonb | 否 | — |  |
| 9 | status | text | 否 | — |  |
| 10 | inferred_via | text | 是 | — |  |
| 11 | predicted_at | timestamp with time zone | 否 | now() |  |
| 12 | reviewed_at | timestamp with time zone | 是 | — |  |
| 13 | reviewed_by | text | 是 | — |  |

### Sample（first row）

(empty table)

## Table: aimerge_runtime_config

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_runtime_config` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | scope | text | 否 | — |  |
| 2 | version_id | uuid | 否 | gen_random_uuid() |  |
| 3 | params | jsonb | 否 | — |  |
| 4 | effective_from | timestamp with time zone | 否 | now() |  |
| 5 | is_active | boolean | 否 | false |  |
| 6 | updated_by | text | 是 | — |  |
| 7 | updated_at | timestamp with time zone | 否 | now() |  |
| 8 | change_reason | text | 是 | — |  |
| 9 | source | text | 是 | — |  |
| 10 | parent_version_id | uuid | 是 | — |  |

### Sample（first row）

(empty table)

## Table: aimerge_source_mapping

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_source_mapping` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | gdate | text | 否 | — |  |
| 3 | game_a_sitegid | text | 否 | — |  |
| 4 | source_b | text | 否 | — |  |
| 5 | source_b_sitegid | text | 否 | — |  |
| 6 | confirmed_at | timestamp with time zone | 否 | now() |  |
| 7 | confirmed_by | text | 是 | — |  |
| 8 | prediction_id | text | 否 | — |  |

### Sample（first row）

(empty table)

## Table: aimerge_team_aliases

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_team_aliases` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | source_id | text | 否 | — |  |
| 3 | alias_text | text | 否 | — |  |
| 4 | language | text | 否 | ''::text |  |
| 5 | canonical_team_id | text | 是 | — |  |
| 6 | confidence | double precision | 是 | — |  |
| 7 | created_from | text | 是 | — |  |

### Sample（first row）

(empty table)

## Table: aimerge_training_labels

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_training_labels` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | gdate | text | 否 | — |  |
| 3 | game_a_sitegid | text | 否 | — |  |
| 4 | source_b | text | 否 | — |  |
| 5 | source_b_sitegid | text | 否 | — |  |
| 6 | prediction_id | text | 否 | — |  |
| 7 | label | boolean | 否 | — |  |
| 8 | features | jsonb | 否 | — |  |
| 9 | label_source | text | 否 | — |  |
| 10 | label_type | text | 否 | — |  |
| 11 | labeled_at | timestamp with time zone | 否 | now() |  |

### Sample（first row）

(empty table)

## Table: aimerge_tuning_pack_exports

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.aimerge_tuning_pack_exports` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_type | text | 否 | — |  |
| 2 | target_date | text | 否 | — |  |
| 3 | started_at | timestamp with time zone | 否 | now() |  |
| 4 | job_id | text | 否 | — |  |
| 5 | status | text | 否 | — |  |
| 6 | filter_mode | text | 是 | — |  |
| 7 | sample_limit | integer | 是 | — |  |
| 8 | include_full_names | boolean | 是 | — |  |
| 9 | total_samples | integer | 否 | 0 |  |
| 10 | processed_samples | integer | 否 | 0 |  |
| 11 | file_path | text | 是 | — |  |
| 12 | finished_at | timestamp with time zone | 是 | — |  |
| 13 | error_message | text | 是 | — |  |

### Sample（first row）

(empty table)

## Table: games_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_bk_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 494,
  "gdate": "2026-06-16",
  "gtime": "20:30:00",
  "team_h": "\uB9BC\uD3EC\uD3EC \uD504\uB77C\uC774\uB4DC",
  "team_a": "\uADF8\uB798\uC11C \uD32C\uB354\uC2A4\uB85C",
  "teamid_h": 8771,
  "teamid_a": 8772,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002220:30\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022\uADF8\uB798\uC11C \uD32C\uB354\uC2A4\uB85C\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022\uB9BC\uD3EC\uD3EC \uD504\uB77C\uC774\uB4DC\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225436185-2026-06-16\\\u0022, \\\u0022SiteLID\\\u0022: \\\u00223133\\\u0022}]\u0022}",
  "match_h": 65,
  "match_a": 87,
  "match_detail": "[[1, 15, 20], [2, 14, 17], [3, 19, 30], [4, 17, 20]]",
  "resultinfo": "[{\u0022Key\u0022: \u0022odd_result\u0022, \u0022Value\u0022: \u0022{\\\u0022Handicap\\\u0022: {\\\u0022Limpopo Pride (\u002B6.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-6.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B7.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-7.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B8.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-8.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B9.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-9.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B10.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-10.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B11.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-11.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B12.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-12.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B13.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-13.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B14.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-14.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B15.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-15.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B16.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-16.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B17.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-17.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B18.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-18.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B19.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-19.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B20.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-20.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B21.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-21.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B22.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-22.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B23.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-23.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B24.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-24.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B25.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-25.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B26.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-26.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B27.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-27.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B28.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-28.5)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022Total Points\\\u0022: {\\\u0022over 122.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 122.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 123.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 123.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 124.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 124.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 125.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 125.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 126.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 126.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 127.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 127.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 128.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 128.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 129.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 129.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 130.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 130.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 131.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 131.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 132.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 132.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 133.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 133.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 134.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 134.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 135.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 135.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 136.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 136.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 137.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 137.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 138.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 138.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 139.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 139.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 140.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 140.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 141.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 141.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 142.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 142.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 143.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 143.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 144.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 144.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 145.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 145.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 146.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 146.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 147.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 147.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 148.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 148.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 149.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 149.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 150.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 150.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 151.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 151.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 152.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 152.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 153.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 153.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 154.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 154.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 155.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 155.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 156.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 156.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Moneyline\\\u0022: {\\\u0022Limpopo Pride\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Limpopo Pride  Total Points\\\u0022: {\\\u0022over 57\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 57\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 57.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 57.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 58\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 58\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 58.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 58.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 59\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 59\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 59.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 59.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 60\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 60\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 60.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 60.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 61\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 61\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 61.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 61.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 62\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 62\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 62.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 62.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 63\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 63\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 63.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 63.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 64\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 64\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 64.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 64.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 65\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 65\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 65.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 65.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 66\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 66\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 66.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 66.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 67\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 67\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 67.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 67.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 68.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 68.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Soweto Panthers  Total Points\\\u0022: {\\\u0022over 65.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 65.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 67\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 67\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 67.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 67.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 68\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 68\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 68.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 68.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 69\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 69\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 69.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 69.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 70\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 70\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 70.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 70.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 71\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 71\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 71.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 71.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 72\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 72\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 72.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 72.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 73\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 73\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 73.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 73.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 74\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 74\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 74.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 74.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 75\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 75\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 75.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 75.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 76\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 76\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 76.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 76.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 77\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 77\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 77.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 77.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 78\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 78\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 78.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 78.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 79\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 79\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 79.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 79.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 80.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 80.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 81\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 81\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 82\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 82\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 82.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 82.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 83\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 83\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 83.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 83.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 84\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 84\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 84.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 84.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 85\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 85\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 85.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 85.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 86\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 86\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 86.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 86.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 87\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 87\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 87.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 87.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 88\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 88\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 88.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 88.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 89\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 89\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 89.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 89.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 90\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 90\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 90.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 90.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 91\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 91\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 91.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 91.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Handicap\\\u0022: {\\\u0022Limpopo Pride (\u002B1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B3.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-3.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B4.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-4.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B5.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-5.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B6.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-6.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B7.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-7.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B8.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-8.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B9.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-9.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B10.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-10.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B11.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-11.5)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00221st half - Total Points\\\u0022: {\\\u0022over 56.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 56.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 58.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 58.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 59.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 59.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 60.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 60.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 61.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 61.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 62.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 62.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 63.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 63.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 64.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 64.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 65.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 65.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 66.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 66.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 67.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 67.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 68.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 68.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Draw No Bet\\\u0022: {\\\u0022Limpopo Pride\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Limpopo Pride Total Points\\\u0022: {\\\u0022over 26.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 26.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 27\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 27\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 27.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 27.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 28\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 28\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 28.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 28.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 29\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 29\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 29.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 29.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 30\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 30\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 31\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 31\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Soweto Panthers Total Points\\\u0022: {\\\u0022over 29\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 29\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 31\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 31\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 31.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 31.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 32\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 32\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 32.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 32.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 33\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 33\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 33.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 33.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 34.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 34.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 35\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 35\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 35.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 35.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 36\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 36\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 36.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 36.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 37\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 37\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 37.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 37.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 38\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 38\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 38.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 38.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st Quarter - Handicap\\\u0022: {\\\u0022Limpopo Pride (\u002B0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B2.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-2.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B3.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-3.5)\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st Quarter - Total Points\\\u0022: {\\\u0022over 28.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 28.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 29.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 29.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 30.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 30.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 31.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 31.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 33.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 33.5\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00221st Quarter - Draw No Bet\\\u0022: {\\\u0022Limpopo Pride\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd Quarter - Handicap\\\u0022: {\\\u0022Limpopo Pride (-0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (\u002B0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B2.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-2.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B3.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-3.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B4.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-4.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B5.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-5.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B6.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-6.5)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd Quarter - Total Points\\\u0022: {\\\u0022over 26.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 26.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 27.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 27.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 28.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 28.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 29.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 29.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 30.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 30.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 31.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 31.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 32.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 32.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 33.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 33.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd Quarter - Draw No Bet\\\u0022: {\\\u0022Limpopo Pride\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00223rd Quarter - Handicap\\\u0022: {\\\u0022Limpopo Pride (\u002B0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B2.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-2.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B3.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-3.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B4.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-4.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B5.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-5.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B6.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-6.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B7.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-7.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B8.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-8.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B9.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-9.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B10.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-10.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B11.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-11.5)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00223rd Quarter - Total Points\\\u0022: {\\\u0022over 31.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 31.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 32.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 32.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 33.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 33.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 34.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 34.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 35.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 35.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 36.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 36.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 37.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 37.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 38.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 38.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 39.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 39.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 40.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 40.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 41.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 41.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 42.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 42.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 43.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 43.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 44.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 44.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 45.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 45.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 46.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 46.5\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00223rd Quarter - Draw No Bet\\\u0022: {\\\u0022Limpopo Pride\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00224th Quarter - Handicap\\\u0022: {\\\u0022Limpopo Pride (-2.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (\u002B2.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (-1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (\u002B1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (-0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (\u002B0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B2.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers (-2.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Limpopo Pride (\u002B3.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-3.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B4.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-4.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B5.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-5.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B6.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-6.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B7.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-7.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B8.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-8.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Limpopo Pride (\u002B9.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Soweto Panthers (-9.5)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00224th Quarter - Total Points\\\u0022: {\\\u0022over 31.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 31.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 32.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 32.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 33.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 33.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 34.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 34.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 35.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 35.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 36.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 36.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 37.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 37.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 38.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 38.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 39.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 39.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 40.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 40.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 41.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 41.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00224th Quarter - Draw No Bet\\\u0022: {\\\u0022Limpopo Pride\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Soweto Panthers\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st Quarter-Limpopo Pride Total Points\\\u0022: {\\\u0022over 13\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 13\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 13.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 13.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 14\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 14.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 15\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 15.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 15.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd Quarter-Limpopo Pride Total Points\\\u0022: {\\\u0022over 11.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 11.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 12\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 12\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 12.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 12.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 13\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 13\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 13.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 13.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 14\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 14\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 14.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 14.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 15\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 15\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 16\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 16\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00223rd Quarter-Limpopo Pride Total Points\\\u0022: {\\\u0022over 13\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 13\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 13.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 13.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 14\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 14.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 15\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 15.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 17\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 17.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 18\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 18\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 18.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 18.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 19\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 19\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 19.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 19.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 20.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 20.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00224th Quarter-Limpopo Pride Total Points\\\u0022: {\\\u0022over 14\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 14.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 15\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 15.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 17\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 17.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 17.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 18\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 18\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 18.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 18.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 19.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 19.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 20\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 20\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st Quarter-Soweto Panthers Total Points\\\u0022: {\\\u0022over 14.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 15.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 17\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 18\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 18\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd Quarter-Soweto Panthers Total Points\\\u0022: {\\\u0022over 14.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 14.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 15\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 15.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 15.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 16.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 17\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 17.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 17.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 18\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 18\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 18.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 18.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00223rd Quarter-Soweto Panthers Total Points\\\u0022: {\\\u0022over 16.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 16.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 17\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 17.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 18\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 18\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 18.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 18.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 19\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 19\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 19.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 19.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 20\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 20\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 20.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 20.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 21\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 21\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 21.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 21.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 22\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 22\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 22.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 22.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 23.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 23.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 24\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 24\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 24.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 24.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 25\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 25\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 25.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 25.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 26\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 26\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 27\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 27\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 27.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 27.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 28\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 28\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 28.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 28.5\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00224th Quarter-Soweto Panthers Total Points\\\u0022: {\\\u0022over 17\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 17\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 17.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 17.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 18\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 18\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 18.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 18.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 19.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 19.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 20\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 20\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 20.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 20.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 21\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 21\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 21.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 21.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 22\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 22\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 22.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 22.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 23\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 23\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 23.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 23.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 24\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 24\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 24.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 24.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st Quarter - Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd Quarter - Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00223rd Quarter - Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00224th Quarter - Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Win Half\\\u0022}}\u0022}]",
  "otherinfo": "{}",
  "status": "Final",
  "create_at": 1782097104777
}
```

## Table: games_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_bm_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 131,
  "gdate": "2026-06-17",
  "gtime": "11:50:00",
  "team_h": "\uC288\uB9AC\uC580\uC2DC \uBC1C\uB9AC\uC170\uD2F0",
  "team_a": "\uD0C0\uC2A4\uB2D8 \uBBF8\uB974",
  "teamid_h": 4400,
  "teamid_a": 4401,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002211:50\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022\uD0C0\uC2A4\uB2D8 \uBBF8\uB974\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022\uC288\uB9AC\uC580\uC2DC \uBC1C\uB9AC\uC170\uD2F0\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225451526-2026-06-17\\\u0022, \\\u0022SiteLID\\\u0022: \\\u002260072\\\u0022}]\u0022}",
  "match_h": null,
  "match_a": null,
  "match_detail": "[]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "InProgress",
  "create_at": 1782097115213
}
```

## Table: games_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_bs_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 18,
  "gdate": "2026-06-17",
  "gtime": "07:45:00",
  "team_h": "St Louis Cardinals",
  "team_a": "San Diego Padres",
  "teamid_h": 218,
  "teamid_a": 215,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002207:45\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022San Diego Padres\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022St Louis Cardinals\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225436418-2026-06-17\\\u0022, \\\u0022SiteLID\\\u0022: \\\u0022295\\\u0022}]\u0022}",
  "match_h": 3,
  "match_a": 2,
  "match_detail": "[[1, 0, 0], [2, 2, 0], [3, 0, 0], [4, 0, 0], [5, 1, 1], [6, 0, 1], [7, 0, 0], [8, 0, 0], [9, 0, 0]]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "Final",
  "create_at": 1782097102714
}
```

## Table: games_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_ck_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 3,
  "source": "panda",
  "lid": 107,
  "gdate": "2026-06-17",
  "gtime": "16:00:00",
  "team_h": "\uC778\uB3C4",
  "team_a": "\uC544\uD504\uAC00\uB2C8\uC2A4\uD0C4",
  "teamid_h": 982,
  "teamid_a": 983,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002216:00\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022\uC544\uD504\uAC00\uB2C8\uC2A4\uD0C4\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022\uC778\uB3C4\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225446551-2026-06-17\\\u0022, \\\u0022SiteLID\\\u0022: \\\u002239565\\\u0022}]\u0022}",
  "match_h": 402,
  "match_a": 232,
  "match_detail": "[[1, 402, 232]]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "Final",
  "create_at": 1782097118007
}
```

## Table: games_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_es_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 357,
  "gdate": "2026-06-17",
  "gtime": "12:00:00",
  "team_h": "Team Refuser",
  "team_a": "Game Master",
  "teamid_h": 6516,
  "teamid_a": 6511,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002212:00\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022Game Master\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022Team Refuser\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225606933227311207-2026-06-17\\\u0022, \\\u0022SiteLID\\\u0022: \\\u00226565430023311918\\\u0022}]\u0022}",
  "match_h": 2,
  "match_a": 0,
  "match_detail": "[[1, 2, 0]]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "Final",
  "create_at": 1782097108828
}
```

## Table: games_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_fl_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 11,
  "source": "panda",
  "lid": 7,
  "gdate": "2026-06-28",
  "gtime": "07:00:00",
  "team_h": "British Columbia Lions",
  "team_a": "Calgary Stampeders",
  "teamid_h": 141,
  "teamid_a": 143,
  "teams": "{}",
  "siteidmaps": "[]",
  "match_h": 0,
  "match_a": 0,
  "match_detail": "[]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "PreGame",
  "create_at": 1782428489884
}
```

## Table: games_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_hb_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: games_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_hl_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 116,
  "gdate": "2026-06-19",
  "gtime": "07:00:00",
  "team_h": "Toronto Marlies",
  "team_a": "Chicago Wolves",
  "teamid_h": 1741,
  "teamid_a": 1719,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002207:00\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022Chicago Wolves\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022Toronto Marlies\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225447231-2026-06-19-REGULATION TIME\\\u0022, \\\u0022SiteLID\\\u0022: \\\u0022658-REGULATION TIME\\\u0022}]\u0022}",
  "match_h": 3,
  "match_a": 3,
  "match_detail": "[[1, 2, 1], [2, 1, 0], [3, 0, 2]]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "Final",
  "create_at": 1782105175666
}
```

## Table: games_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_ma_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: games_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_sc_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 1103,
  "gdate": "2026-06-16",
  "gtime": "21:00:00",
  "team_h": "AL Ahed",
  "team_a": "Sagesse SC",
  "teamid_h": 26875,
  "teamid_a": 26880,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002221:00\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022Sagesse SC\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022AL Ahed\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225438655-2026-06-16\\\u0022, \\\u0022SiteLID\\\u0022: \\\u00222702\\\u0022}]\u0022}",
  "match_h": 1,
  "match_a": 0,
  "match_detail": "[[1, 0, 0], [2, 1, 0]]",
  "resultinfo": "[{\u0022Key\u0022: \u0022odd_result\u0022, \u0022Value\u0022: \u0022{\\\u0022O/U\\\u0022: {\\\u0022over 0.5/1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5/1\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 1\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 1/1.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 1/1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1.5/2\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1.5/2\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 2\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 2\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 2/2.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 2/2.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 2.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 2.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 2.5/3\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 2.5/3\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 3\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 3\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 3/3.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 3/3.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 3.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 3.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-1.5/2)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (\u002B1.5/2)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022AL Ahed (-1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (\u002B1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022AL Ahed (-1/1.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B1/1.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (-1)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (\u002B1)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022AL Ahed (-0.5/1)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (\u002B0.5/1)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022AL Ahed (-0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (\u002B0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (-0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (\u002B0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (-0.5)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00221st half - O/U\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 0.5/1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5/1\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1/1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1/1.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-0.5/1)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (\u002B0.5/1)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022AL Ahed (-0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (\u002B0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022AL Ahed (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221x2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - 1x2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Correct Score\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00220-4\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-4\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-4\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-4\\\u0022: \\\u0022Win\\\u0022, \\\u00224-0\\\u0022: \\\u0022Win\\\u0022, \\\u00224-1\\\u0022: \\\u0022Win\\\u0022, \\\u00224-2\\\u0022: \\\u0022Win\\\u0022, \\\u00224-3\\\u0022: \\\u0022Win\\\u0022, \\\u00224-4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Inverse Correct Score\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00220-4\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-4\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-4\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-4\\\u0022: \\\u0022Win\\\u0022, \\\u00224-0\\\u0022: \\\u0022Win\\\u0022, \\\u00224-1\\\u0022: \\\u0022Win\\\u0022, \\\u00224-2\\\u0022: \\\u0022Win\\\u0022, \\\u00224-3\\\u0022: \\\u0022Win\\\u0022, \\\u00224-4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u0022High Odd Correct Score\\\u0022: {\\\u00220-5\\\u0022: \\\u0022Win\\\u0022, \\\u00221-5\\\u0022: \\\u0022Win\\\u0022, \\\u00222-5\\\u0022: \\\u0022Win\\\u0022, \\\u00223-5\\\u0022: \\\u0022Win\\\u0022, \\\u00224-5\\\u0022: \\\u0022Win\\\u0022, \\\u00225-5\\\u0022: \\\u0022Win\\\u0022, \\\u00225-0\\\u0022: \\\u0022Win\\\u0022, \\\u00225-1\\\u0022: \\\u0022Win\\\u0022, \\\u00225-2\\\u0022: \\\u0022Win\\\u0022, \\\u00225-3\\\u0022: \\\u0022Win\\\u0022, \\\u00225-4\\\u0022: \\\u0022Win\\\u0022, \\\u00220-6\\\u0022: \\\u0022Win\\\u0022, \\\u00221-6\\\u0022: \\\u0022Win\\\u0022, \\\u00222-6\\\u0022: \\\u0022Win\\\u0022, \\\u00223-6\\\u0022: \\\u0022Win\\\u0022, \\\u00226-6\\\u0022: \\\u0022Win\\\u0022, \\\u00226-0\\\u0022: \\\u0022Win\\\u0022, \\\u00226-1\\\u0022: \\\u0022Win\\\u0022, \\\u00226-2\\\u0022: \\\u0022Win\\\u0022, \\\u00226-3\\\u0022: \\\u0022Win\\\u0022, \\\u00220-7\\\u0022: \\\u0022Win\\\u0022, \\\u00221-7\\\u0022: \\\u0022Win\\\u0022, \\\u00222-7\\\u0022: \\\u0022Win\\\u0022, \\\u00227-0\\\u0022: \\\u0022Win\\\u0022, \\\u00227-1\\\u0022: \\\u0022Win\\\u0022, \\\u00227-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-8\\\u0022: \\\u0022Win\\\u0022, \\\u00221-8\\\u0022: \\\u0022Win\\\u0022, \\\u00228-0\\\u0022: \\\u0022Win\\\u0022, \\\u00228-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-9\\\u0022: \\\u0022Win\\\u0022, \\\u00229-0\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Win Either Half\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Win Both Halves\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Both team to score in both halves (2 way)\\\u0022: {\\\u0022Yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022No\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Last Teams to Score\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - Correct Score\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - Inverse Correct Score\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u00221H - High Odd Correct Score\\\u0022: {\\\u00220-4\\\u0022: \\\u0022Win\\\u0022, \\\u00221-4\\\u0022: \\\u0022Win\\\u0022, \\\u00222-4\\\u0022: \\\u0022Win\\\u0022, \\\u00223-4\\\u0022: \\\u0022Win\\\u0022, \\\u00224-4\\\u0022: \\\u0022Win\\\u0022, \\\u00224-0\\\u0022: \\\u0022Win\\\u0022, \\\u00224-1\\\u0022: \\\u0022Win\\\u0022, \\\u00224-2\\\u0022: \\\u0022Win\\\u0022, \\\u00224-3\\\u0022: \\\u0022Win\\\u0022, \\\u00220-5\\\u0022: \\\u0022Win\\\u0022, \\\u00221-5\\\u0022: \\\u0022Win\\\u0022, \\\u00222-5\\\u0022: \\\u0022Win\\\u0022, \\\u00223-5\\\u0022: \\\u0022Win\\\u0022, \\\u00224-5\\\u0022: \\\u0022Win\\\u0022, \\\u00225-0\\\u0022: \\\u0022Win\\\u0022, \\\u00225-1\\\u0022: \\\u0022Win\\\u0022, \\\u00225-2\\\u0022: \\\u0022Win\\\u0022, \\\u00225-3\\\u0022: \\\u0022Win\\\u0022, \\\u00225-4\\\u0022: \\\u0022Win\\\u0022, \\\u00225-5\\\u0022: \\\u0022Win\\\u0022, \\\u00226-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-6\\\u0022: \\\u0022Win\\\u0022, \\\u00221-6\\\u0022: \\\u0022Win\\\u0022, \\\u00226-1\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - Correct Score\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - Inverse Correct Score\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u00222H - High Odd Correct Score\\\u0022: {\\\u00220-4\\\u0022: \\\u0022Win\\\u0022, \\\u00221-4\\\u0022: \\\u0022Win\\\u0022, \\\u00222-4\\\u0022: \\\u0022Win\\\u0022, \\\u00223-4\\\u0022: \\\u0022Win\\\u0022, \\\u00224-4\\\u0022: \\\u0022Win\\\u0022, \\\u00224-0\\\u0022: \\\u0022Win\\\u0022, \\\u00224-1\\\u0022: \\\u0022Win\\\u0022, \\\u00224-2\\\u0022: \\\u0022Win\\\u0022, \\\u00224-3\\\u0022: \\\u0022Win\\\u0022, \\\u00220-5\\\u0022: \\\u0022Win\\\u0022, \\\u00221-5\\\u0022: \\\u0022Win\\\u0022, \\\u00222-5\\\u0022: \\\u0022Win\\\u0022, \\\u00223-5\\\u0022: \\\u0022Win\\\u0022, \\\u00224-5\\\u0022: \\\u0022Win\\\u0022, \\\u00225-0\\\u0022: \\\u0022Win\\\u0022, \\\u00225-1\\\u0022: \\\u0022Win\\\u0022, \\\u00225-2\\\u0022: \\\u0022Win\\\u0022, \\\u00225-3\\\u0022: \\\u0022Win\\\u0022, \\\u00225-4\\\u0022: \\\u0022Win\\\u0022, \\\u00225-5\\\u0022: \\\u0022Win\\\u0022, \\\u00226-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-6\\\u0022: \\\u0022Win\\\u0022, \\\u00221-6\\\u0022: \\\u0022Win\\\u0022, \\\u00226-1\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Correct Score (Multi Bet)\\\u0022: {\\\u00221:0/2:0/3:0\\\u0022: \\\u0022Win\\\u0022, \\\u00224:0/5:0/6:0\\\u0022: \\\u0022Win\\\u0022, \\\u00222:1/3:1/4:1\\\u0022: \\\u0022Win\\\u0022, \\\u00223:2/4:2/4:3/5:1\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL AhedWinOthers\\\u0022: \\\u0022Win\\\u0022, \\\u0022DrawOthers\\\u0022: \\\u0022Win\\\u0022, \\\u00220:1/0:2/0:3\\\u0022: \\\u0022Win\\\u0022, \\\u00220:4/0:5/0:6\\\u0022: \\\u0022Win\\\u0022, \\\u00221:2/1:3/1:4\\\u0022: \\\u0022Win\\\u0022, \\\u00222:3/2:4/3:4/1:5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SCWinOthers\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Total Goals Range\\\u0022: {\\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00224-6\\\u0022: \\\u0022Win\\\u0022, \\\u00227\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\\\u0022: \\\u0022Win\\\u0022, \\\u00224\\\u0022: \\\u0022Win\\\u0022, \\\u00225\\\u0022: \\\u0022Win\\\u0022, \\\u00226\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u0022AL Ahed Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Sagesse SC Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - AL Ahed Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - Sagesse SC Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Both Teams to Score\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Both Team to Score\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd half - Both Team to Score\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Half Time/Full-Time\\\u0022: {\\\u0022AL Ahed/AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Winning Margin\\\u0022: {\\\u0022AL Ahed--Win By 1 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed--Win By 2 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed--Win By 3 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed--Win By 4\u002B Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 1 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 2 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 3 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw and Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 4\u002B Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022No Goal\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - Winning Margin\\\u0022: {\\\u0022AL Ahed--Win By 1 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed--Win By 2\u002B Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 1 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 2\u002B Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw and Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022No Goal\\\u0022: \\\u0022Win\\\u0022}, \\\u00223-Way Handicap\\\u0022: {\\\u0022AL Ahed (-1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw (AL Ahed)-1\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC (\u002B1)\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - 3-Way Handicap\\\u0022: {\\\u0022AL Ahed (-1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw (-1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC (\u002B1)\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Double Chance\\\u0022: {\\\u0022AL Ahed or draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed or Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC or draw\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - Double Chance\\\u0022: {\\\u0022AL Ahed or draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed or Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC or draw\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Draw No Bet\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00221st half - Draw No Bet\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Draw\\\u0022}, \\\u00222nd half - Draw No Bet\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022Odd/Even\\\u0022: {\\\u0022Odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Even\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00221st half - Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd Half AL Ahed Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd Half Sagesse SC Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022AL Ahed Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 0.5/1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5/1\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 1\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 1/1.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 1/1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1.5/2\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1.5/2\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 2\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 2\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Sagesse SC Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 0.5/1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5/1\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022AL Ahed Clean Sheet\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022Sagesse SC Clean Sheet\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st Half AL Ahed To Win to Nil\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st Half Sagesse SC To Win to Nil\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd Half - AL Ahed To Win to Nil\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd Half - Sagesse SC To Win to Nil\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022AL Ahed to Win to Nil\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022Sagesse SC to Win to Nil\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022FT - Win From Behind\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Draw\\\u0022}, \\\u0022Highest Scoring Half - 1X2\\\u0022: {\\\u00221st half\\\u0022: \\\u0022Win\\\u0022, \\\u00222nd half\\\u0022: \\\u0022Win\\\u0022, \\\u0022Both Halves Draw\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Time of  1st Goal\\\u0022: {\\\u0022Start-14 mins 59s\\\u0022: \\\u0022Win\\\u0022, \\\u002215 mins-29 mins 59s\\\u0022: \\\u0022Win\\\u0022, \\\u002230 mins-1H\\\u0022: \\\u0022Win\\\u0022, \\\u00222H Start-59 mins 59s\\\u0022: \\\u0022Win\\\u0022, \\\u002260 mins-74 mins 59s\\\u0022: \\\u0022Win\\\u0022, \\\u002275 mins-FT\\\u0022: \\\u0022Win\\\u0022, \\\u0022none\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st Goal (1x2)\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022none\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd Goal (1x2)\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022none\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st Goal (DNB)\\\u0022: {\\\u0022AL Ahed \\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC \\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd Goal (DNB)\\\u0022: {\\\u0022AL Ahed \\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC \\\u0022: \\\u0022Draw\\\u0022}, \\\u0022FT - Odd/Even \u0026 Total\\\u0022: {\\\u0022odd \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022odd \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022even \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022even \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022odd \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022odd \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022even \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022even \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022odd \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022odd \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022even \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022even \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022}, \\\u00221x2 \u0026 Odd/Even\\\u0022: {\\\u0022AL Ahed \u0026 Odd\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Odd\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Even\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Even\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Even\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Total Goals \u0026 Both Teams to Score\\\u0022: {\\\u0022over 0.5 \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022under 0.5 \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022over 0.5 \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022under 0.5 \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022over 1.5 \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022under 1.5 \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022over 1.5 \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022under 1.5 \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022over 2.5 \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022under 2.5 \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022over 2.5 \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022under 2.5 \u0026 no\\\u0022: \\\u0022Win\\\u0022}, \\\u00221x2 \u0026 Total Goals\\\u0022: {\\\u0022AL Ahed \u0026 Over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Under 2.5\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - 1x2 \u0026 Total\\\u0022: {\\\u0022AL Ahed \u0026 Over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Under 1.5\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - 1x2 \u0026 Total\\\u0022: {\\\u0022AL Ahed \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022}, \\\u00221x2 \u0026 Both Teams to Score\\\u0022: {\\\u0022AL Ahed \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 No\\\u0022: \\\u0022Win\\\u0022}, \\\u00221st half - 1X2 \u0026 Both Teams to Score\\\u0022: {\\\u0022AL Ahed \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 No\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - 1X2 \u0026 Both Teams to Score\\\u0022: {\\\u0022AL Ahed \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 no\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - 1X2 \u0026 First Team To Score\\\u0022: {\\\u0022AL Ahed \u0026 AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw \u0026 Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022No Goal\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Double Chance \u0026 Both Teams to Score\\\u0022: {\\\u0022AL Ahed/draw \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 no\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/Sagesse SC \u0026 yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/Sagesse SC \u0026 no\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Double Chance \u0026 Total\\\u0022: {\\\u0022AL Ahed/draw \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 over 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 under 0.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Halftime/Fulltime Odd/Even\\\u0022: {\\\u0022odd/odd\\\u0022: \\\u0022Win\\\u0022, \\\u0022odd/even\\\u0022: \\\u0022Win\\\u0022, \\\u0022even/odd\\\u0022: \\\u0022Win\\\u0022, \\\u0022even/even\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Halftime/Fulltime \u0026 Total\\\u0022: {\\\u0022AL Ahed/AL Ahed \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/AL Ahed \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/AL Ahed \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/draw \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/draw \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/Sagesse SC \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/Sagesse SC \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC \u0026 over 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC \u0026 under 1.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/draw \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/AL Ahed \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/AL Ahed \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/draw \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/draw \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/Sagesse SC \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw/Sagesse SC \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/draw \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC \u0026 over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC \u0026 under 2.5\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Halftime/Fulltime \u0026 Exact Goals\\\u0022: {\\\u0022AL Ahed/AL Ahed 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/AL Ahed 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/AL Ahed 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/AL Ahed 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/AL Ahed 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/AL Ahed 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/AL Ahed 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/AL Ahed 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Draw 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Draw 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Draw 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Draw 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Draw 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Draw 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Sagesse SC 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Sagesse SC 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Sagesse SC 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Sagesse SC 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Sagesse SC 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw/Sagesse SC 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/AL Ahed 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw 5\u002B\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC 0\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC 1\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC 2\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC 3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC 4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Sagesse SC 5\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u0022AL Ahed No Bet\\\u0022: {\\\u0022draw\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Draw\\\u0022}, \\\u0022Sagesse SC No Bet\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022AL Ahed Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022Sagesse SC Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022AL Ahed to Win Both Halves\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Sagesse SC to Win Both Halves\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022AL Ahed to Win Either Half\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022Sagesse SC to Win Either Half\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022AL Ahed Highest Scoring Half\\\u0022: {\\\u00221st half\\\u0022: \\\u0022Win\\\u0022, \\\u00222nd half\\\u0022: \\\u0022Win\\\u0022, \\\u0022equal\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Sagesse SC Highest Scoring Half\\\u0022: {\\\u00221st half\\\u0022: \\\u0022Win\\\u0022, \\\u00222nd half\\\u0022: \\\u0022Win\\\u0022, \\\u0022equal\\\u0022: \\\u0022Win\\\u0022}, \\\u0022AL Ahed to Score in Both Halves\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Sagesse SC to Score in Both Halves\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022FT - First Goal Half\\\u0022: {\\\u00221st half\\\u0022: \\\u0022Win\\\u0022, \\\u00222nd half\\\u0022: \\\u0022Win\\\u0022, \\\u0022no goal\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - AL Ahed First Goal Half\\\u0022: {\\\u00221st half\\\u0022: \\\u0022Win\\\u0022, \\\u00222nd half\\\u0022: \\\u0022Win\\\u0022, \\\u0022no goal\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Sagesse SC First Goal Half\\\u0022: {\\\u00221st half\\\u0022: \\\u0022Win\\\u0022, \\\u00222nd half\\\u0022: \\\u0022Win\\\u0022, \\\u0022no goal\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Race To 2 Goal\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022none\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u0022FT - Race To 3 Goal\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022none\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Both team to score in both halves\\\\uff084 way)\\\u0022: {\\\u0022yes/yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022yes/no\\\u0022: \\\u0022Win\\\u0022, \\\u0022no/yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022no/no\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Both Halves More Than 1.5 Goals\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Both Halves Less Than 1.5 Goals\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00221st half - AL Ahed Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 0.5/1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5/1\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - Sagesse SC Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00221st half - AL Ahed Clean Sheet\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00221st half - Sagesse SC Clean Sheet\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd half - Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 0.5/1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5/1\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1.0\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 1.0\\\u0022: \\\u0022Draw\\\u0022, \\\u0022over 1/1.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 1/1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 1.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1.5/2\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 1.5/2\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd half - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-1)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (\u002B1)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022AL Ahed (-0.5/1)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (\u002B0.5/1)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022AL Ahed (-0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (\u002B0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (-0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (\u002B0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (-0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (\u002B0.5/1)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (-0.5/1)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd half - 1x2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - Handicap 3 Way\\\u0022: {\\\u0022AL Ahed (-1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw (-1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC (\u002B1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed (\u002B1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw (\u002B1)\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC (-1)\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - Double Chance\\\u0022: {\\\u0022AL Ahed or draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed or Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC or draw\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd Half - Winning Margin\\\u0022: {\\\u0022AL Ahed--Win By 1 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed--Win By 2\u002B Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 1 Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC--Win By 2\u002B Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022Draw and Goal\\\u0022: \\\u0022Win\\\u0022, \\\u0022No Goal\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd Half - AL Ahed Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd Half - Sagesse SC Exact Goals\\\u0022: {\\\u00220\\\u0022: \\\u0022Win\\\u0022, \\\u00221\\\u0022: \\\u0022Win\\\u0022, \\\u00222\\\u0022: \\\u0022Win\\\u0022, \\\u00223\u002B\\\u0022: \\\u0022Win\\\u0022}, \\\u00222nd half - Odd/Even\\\u0022: {\\\u0022odd\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022even\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd half - AL Ahed Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 0.5/1\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5/1\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022over 1\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 1\\\u0022: \\\u0022Draw\\\u0022}, \\\u00222nd half - Sagesse SC Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u00222nd half - AL Ahed Clean Sheet\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Win Half\\\u0022}, \\\u00222nd half - Sagesse SC Clean Sheet\\\u0022: {\\\u0022yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022no\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Total Corners\\\u0022: {\\\u0022over 8\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 8\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 8.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 8.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022over 9\\\u0022: \\\u0022Draw\\\u0022, \\\u0022under 9\\\u0022: \\\u0022Draw\\\u0022}, \\\u002215 Minutes (begins~14:59) - 1X2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u002215 Minutes (15:00~29:59) - 1X2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u002215 Minutes (30:00~End of the first half) - 1X2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u002215 Minutes (start of the second half~59:59) - 1X2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u002215 Minutes (60:00~74:59) - 1X2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u002215 Minutes (75:00~End of the game) - 1X2\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022draw\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u002215 Minutes (15:00~29:59) - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Draw\\\u0022}, \\\u002215 Minutes (75:00~End of the game) - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022AL Ahed (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u002215 Minutes (30:00~End of the first half) - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Draw\\\u0022}, \\\u002215 Minutes (begins~14:59) - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Draw\\\u0022}, \\\u002215 Minutes (60:00~74:59) - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (\u002B0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (-0/0.5)\\\u0022: \\\u0022Win Half\\\u0022}, \\\u002215 Minutes (start of the second half~59:59) - Handicap(0-0)\\\u0022: {\\\u0022AL Ahed (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022AL Ahed (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC (0)\\\u0022: \\\u0022Draw\\\u0022, \\\u0022AL Ahed (\u002B0/0.5)\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022Sagesse SC (-0/0.5)\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u002215 Minutes (begins~14:59) - Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u002215 Minutes (15:00~29:59) - Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u002215 Minutes (30:00~End of the first half) - Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u002215 Minutes (start of the second half~59:59) - Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u002215 Minutes (60:00~74:59) - Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Win Half\\\u0022}, \\\u002215 Minutes (75:00~End of the game) - Total Goals\\\u0022: {\\\u0022over 0.5\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022under 0.5\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Last Teams to Score\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022none\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Double Chance \u0026 1H Both Teams To Score\\\u0022: {\\\u0022AL Ahed/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 No\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Double Chance \u0026 2H Both Teams To Score\\\u0022: {\\\u0022AL Ahed/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 No\\\u0022: \\\u0022Win\\\u0022}, \\\u0022First Goal Scoring Team \u0026 Goal Score Over/Under\\\u0022: {\\\u0022AL Ahed \u0026 Over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Over 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed \u0026 Under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC \u0026 Under 2.5\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Double Chance \u0026 First Goal Team\\\u0022: {\\\u0022AL Ahed/Draw \u0026 AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw \u0026 Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 Sagesse SC\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u00221H-Double Chance \u0026 Both Teams To Score\\\u0022: {\\\u0022AL Ahed/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 No\\\u0022: \\\u0022Win\\\u0022}, \\\u00222H-Double Chance \u0026 Both Teams To Score\\\u0022: {\\\u0022AL Ahed/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC/Draw \u0026 No\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed/Sagesse SC \u0026 No\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Number of Scoring Teams\\\u0022: {\\\u0022Two\\\u0022: \\\u0022Win\\\u0022, \\\u0022One\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Team To Win\\\u0022: {\\\u0022AL Ahed  Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL Ahed  No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC  Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC  No\\\u0022: \\\u0022Win\\\u0022, \\\u0022Either Team  Yes\\\u0022: \\\u0022Win\\\u0022, \\\u0022Either Team No\\\u0022: \\\u0022Win\\\u0022}, \\\u0022Which Team To Score\\\u0022: {\\\u0022AL Ahed only\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC only\\\u0022: \\\u0022Win\\\u0022, \\\u0022Both\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u00221H-First Goal/Last Goal\\\u0022: {\\\u0022AL AhedFirst\\\u0022: \\\u0022Win\\\u0022, \\\u0022AL AhedLast\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SCFirst\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SCLast\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022}, \\\u00221H-1st Goal - 3way\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u00221H-1st Goal no bet -2way\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Draw\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Draw\\\u0022}, \\\u00222H-1st Goal - 3way\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Win\\\u0022, \\\u0022None\\\u0022: \\\u0022Win\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win\\\u0022}, \\\u00222H-1st Goal no bet -2way\\\u0022: {\\\u0022AL Ahed\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022Sagesse SC\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022AL Ahed Win\\\u0022: {\\\u0022Yes\\\u0022: \\\u0022Lose Half\\\u0022, \\\u0022No\\\u0022: \\\u0022Win Half\\\u0022}, \\\u0022Sagesse SC Win\\\u0022: {\\\u0022Yes\\\u0022: \\\u0022Win Half\\\u0022, \\\u0022No\\\u0022: \\\u0022Lose Half\\\u0022}, \\\u0022Win If Any Selected Correct Score Hits\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00220-4\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-4\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-4\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-4\\\u0022: \\\u0022Win\\\u0022, \\\u00224-0\\\u0022: \\\u0022Win\\\u0022, \\\u00224-1\\\u0022: \\\u0022Win\\\u0022, \\\u00224-2\\\u0022: \\\u0022Win\\\u0022, \\\u00224-3\\\u0022: \\\u0022Win\\\u0022, \\\u00224-4\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u00221H - Win If Any Selected Correct Score Hits\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}, \\\u00222H - Win If Any Selected Correct Score Hits\\\u0022: {\\\u00220-0\\\u0022: \\\u0022Win\\\u0022, \\\u00220-1\\\u0022: \\\u0022Win\\\u0022, \\\u00220-2\\\u0022: \\\u0022Win\\\u0022, \\\u00220-3\\\u0022: \\\u0022Win\\\u0022, \\\u00221-0\\\u0022: \\\u0022Win\\\u0022, \\\u00221-1\\\u0022: \\\u0022Win\\\u0022, \\\u00221-2\\\u0022: \\\u0022Win\\\u0022, \\\u00221-3\\\u0022: \\\u0022Win\\\u0022, \\\u00222-0\\\u0022: \\\u0022Win\\\u0022, \\\u00222-1\\\u0022: \\\u0022Win\\\u0022, \\\u00222-2\\\u0022: \\\u0022Win\\\u0022, \\\u00222-3\\\u0022: \\\u0022Win\\\u0022, \\\u00223-0\\\u0022: \\\u0022Win\\\u0022, \\\u00223-1\\\u0022: \\\u0022Win\\\u0022, \\\u00223-2\\\u0022: \\\u0022Win\\\u0022, \\\u00223-3\\\u0022: \\\u0022Win\\\u0022, \\\u0022Others\\\u0022: \\\u0022Win\\\u0022}}\u0022}]",
  "otherinfo": "{}",
  "status": "Final",
  "create_at": 1782097107351
}
```

## Table: games_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_tb_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 82,
  "gdate": "2026-06-22",
  "gtime": "11:25:00",
  "team_h": "Grzegorz Felkel",
  "team_a": "Tibor Spanik",
  "teamid_h": 4468,
  "teamid_a": 4469,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002211:25\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022Tibor Spanik\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022Grzegorz Felkel\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225462475-2026-06-22\\\u0022, \\\u0022SiteLID\\\u0022: \\\u002217638\\\u0022}]\u0022}",
  "match_h": 0,
  "match_a": 0,
  "match_detail": "[]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "PreGame",
  "create_at": 1782097169673
}
```

## Table: games_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_tn_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 4,
  "source": "panda",
  "lid": 1250,
  "gdate": "2026-06-17",
  "gtime": "12:46:00",
  "team_h": "Mao Mushika",
  "team_a": "Yu Chen Lin",
  "teamid_h": 51498,
  "teamid_a": 51509,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002212:46\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022Yu Chen Lin\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022Mao Mushika\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225449674-2026-06-17\\\u0022, \\\u0022SiteLID\\\u0022: \\\u002236135\\\u0022}]\u0022}",
  "match_h": 0,
  "match_a": 0,
  "match_detail": "[[1, 0, 0]]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "InProgress",
  "create_at": 1782097107605
}
```

## Table: games_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_vb_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "panda",
  "lid": 363,
  "gdate": "2026-06-17",
  "gtime": "14:00:00",
  "team_h": "Neftika (4\u04454)",
  "team_a": "Kuzbass (4\u04454)",
  "teamid_h": 4634,
  "teamid_a": 4635,
  "teams": "{}",
  "siteidmaps": "{\u0022panda\u0022: \u0022[{\\\u0022Site\\\u0022: \\\u0022panda\\\u0022, \\\u0022GTime\\\u0022: \\\u002214:00\\\u0022, \\\u0022Team_A\\\u0022: \\\u0022Kuzbass (4\u04454)\\\u0022, \\\u0022Team_H\\\u0022: \\\u0022Neftika (4\u04454)\\\u0022, \\\u0022SiteGID\\\u0022: \\\u00225451738-2026-06-17\\\u0022, \\\u0022SiteLID\\\u0022: \\\u002226088\\\u0022}]\u0022}",
  "match_h": null,
  "match_a": null,
  "match_detail": "[]",
  "resultinfo": null,
  "otherinfo": "{}",
  "status": "InProgress",
  "create_at": 1782097110194
}
```

## Table: games_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.games_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('games_wp_id_seq'::regclass) |  |
| 2 | source | text | 否 | 'panda'::character varying |  |
| 3 | lid | bigint | 是 | — |  |
| 4 | gdate | date | 否 | — |  |
| 5 | gtime | time without time zone | 否 | — |  |
| 6 | team_h | text | 是 | — |  |
| 7 | team_a | text | 是 | — |  |
| 8 | teamid_h | bigint | 是 | — |  |
| 9 | teamid_a | bigint | 是 | — |  |
| 10 | teams | jsonb | 否 | '{}'::jsonb |  |
| 11 | siteidmaps | jsonb | 否 | '[]'::jsonb |  |
| 13 | match_h | bigint | 是 | — |  |
| 14 | match_a | bigint | 是 | — |  |
| 15 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 16 | resultinfo | jsonb | 是 | — |  |
| 17 | otherinfo | jsonb | 是 | — |  |
| 18 | status | text | 是 | — |  |
| 20 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: leagues_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_bk_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "FIBA Eurobasket Women",
  "en_name": null,
  "name_map": "{\u0022en-US\u0022: \u0022FIBA Eurobasket Women\u0022, \u0022ko-KR\u0022: \u0022FIBA Eurobasket Women\u0022, \u0022th-TH\u0022: \u0022FIBA Eurobasket Women\u0022, \u0022vi-VN\u0022: \u0022FIBA Eurobasket Women\u0022, \u0022zh-CN\u0022: \u0022FIBA\u6B27\u6D32\u5973\u5B50\u7BEE\u7403\u9526\u6807\u8D5B\u0022, \u0022zh-TW\u0022: \u0022FIBA\u6B50\u6D32\u5973\u5B50\u7C43\u7403\u9326\u6A19\u8CFD\u0022}",
  "abbr_map": "{}",
  "create_at": 1751264327611
}
```

## Table: leagues_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_bm_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "Polish International - Men Doubles",
  "en_name": null,
  "name_map": "{\u0022ko-KR\u0022: \u0022\uD3F4\uB780\uB4DC \uAD6D\uC81C - \uB0A8\uC790 \uBCF5\uC2DD\u0022, \u0022th-TH\u0022: \u0022Polish International - Men Doubles\u0022, \u0022vi-VN\u0022: \u0022Polish International - Men Doubles\u0022, \u0022zh-CN\u0022: \u0022\u6CE2\u5170\u56FD\u9645\u8D5B - \u7537\u53CC\u0022, \u0022zh-TW\u0022: \u0022\u6CE2\u862D\u570B\u969B\u8CFD - \u7537\u96D9\u0022}",
  "abbr_map": "{}",
  "create_at": 1758459475665
}
```

## Table: leagues_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_bs_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "MLB All Star Game",
  "en_name": null,
  "name_map": "{\u0022en-US\u0022: \u0022MLB All Star Game\u0022, \u0022ko-KR\u0022: \u0022MLB \uC62C\uC2A4\uD0C0\uAC8C\uC784\u0022, \u0022th-TH\u0022: \u0022MLB All Star Game\u0022, \u0022vi-VN\u0022: \u0022MLB All Star Game\u0022, \u0022zh-CN\u0022: \u0022MLB \u7F8E\u56FD\u804C\u68D2 - \u5168\u660E\u661F\u8D5B\u0022, \u0022zh-TW\u0022: \u0022MLB \u7F8E\u570B\u8077\u68D2 - \u5168\u660E\u661F\u8CFD\u0022}",
  "abbr_map": "{}",
  "create_at": 1752639534008
}
```

## Table: leagues_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_ck_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "Australia Century Champions League Mackay T20",
  "en_name": null,
  "name_map": "{}",
  "abbr_map": "{}",
  "create_at": 1754141870005
}
```

## Table: leagues_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_es_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "LOL-LJL Ignite",
  "en_name": null,
  "name_map": "{\u0022en-US\u0022: \u0022LOL-LJL Ignite\u0022}",
  "abbr_map": "{}",
  "create_at": 1750523997953
}
```

## Table: leagues_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_fl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "NFL Preseason",
  "en_name": null,
  "name_map": "{\u0022en-US\u0022: \u0022NFL Preseason\u0022, \u0022ko-KR\u0022: \u0022NFL \uD504\uB9AC\uC2DC\uC98C\u0022, \u0022th-TH\u0022: \u0022NFL Preseason\u0022, \u0022vi-VN\u0022: \u0022NFL Preseason\u0022, \u0022zh-CN\u0022: \u0022NFL \u7F8E\u56FD\u804C\u4E1A\u7F8E\u5F0F\u8DB3\u7403 - \u5B63\u524D\u8D5B\u0022, \u0022zh-TW\u0022: \u0022NFL \u7F8E\u570B\u8077\u696D\u7F8E\u5F0F\u8DB3\u7403 - \u5B63\u524D\u8CFD\u0022}",
  "abbr_map": "{}",
  "create_at": 1754008170160
}
```

## Table: leagues_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_hb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: leagues_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_hl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "Western Hockey League",
  "en_name": null,
  "name_map": "{\u0022en-US\u0022: \u0022Western Hockey League\u0022}",
  "abbr_map": "{}",
  "create_at": 1757911871482
}
```

## Table: leagues_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_ma_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: leagues_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_sc_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "Algeria Cup",
  "en_name": null,
  "name_map": "{\u0022en-US\u0022: \u0022Algeria Cup\u0022, \u0022ko-KR\u0022: \u0022\uC54C\uC81C\uB9AC \uCEF5\u0022, \u0022th-TH\u0022: \u0022Algeria Cup\u0022, \u0022vi-VN\u0022: \u0022Algeria Cup\u0022, \u0022zh-CN\u0022: \u0022\u963F\u5C14\u53CA\u5229\u4E9A\u676F\u0022, \u0022zh-TW\u0022: \u0022\u963F\u723E\u53CA\u5229\u4E9E\u76C3\u0022}",
  "abbr_map": "{}",
  "create_at": 1751744664211
}
```

## Table: leagues_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_tb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "WTT Contender Almaty - Women Doubles",
  "en_name": null,
  "name_map": "{\u0022ko-KR\u0022: \u0022WTT \uC54C\uB9C8\uD2F0 \uCC4C\uB9B0\uC9C0 - \uC5EC\uC790 \uBCF5\uC2DD\u0022, \u0022th-TH\u0022: \u0022WTT Contender Almaty - Women Doubles\u0022, \u0022vi-VN\u0022: \u0022WTT Contender Almaty - Women Doubles\u0022, \u0022zh-CN\u0022: \u0022WTT\u963F\u62C9\u6728\u56FE\u6311\u6218\u8D5B - \u5973\u53CC\u0022, \u0022zh-TW\u0022: \u0022WTT\u963F\u62C9\u6728\u5716\u6311\u6230\u8CFD - \u5973\u96D9\u0022}",
  "abbr_map": "{}",
  "create_at": 1757242719431
}
```

## Table: leagues_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_tn_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "ITF M15 Duffel - Men Singles",
  "en_name": null,
  "name_map": "{\u0022en-US\u0022: \u0022ITF M15 Duffel - Men Singles\u0022, \u0022ko-KR\u0022: \u0022ITF M15 \uB354\uD50C\uBC31 - \uB0A8\uC131 \uC2F1\uAE00\u0022, \u0022th-TH\u0022: \u0022ITF M15 Duffel - Men Singles\u0022, \u0022vi-VN\u0022: \u0022ITF M15 Duffel - Men Singles\u0022, \u0022zh-CN\u0022: \u0022ITF M15\u8FEA\u5F17\u5C14 - \u7537\u5355\u0022, \u0022zh-TW\u0022: \u0022ITF M15\u8FEA\u5F17\u723E - \u7537\u55AE\u0022}",
  "abbr_map": "{}",
  "create_at": 1750607965170
}
```

## Table: leagues_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_vb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "source_name": "Brazil Superliga Serie C Women",
  "en_name": null,
  "name_map": "{\u0022ko-KR\u0022: \u0022\uBE0C\uB77C\uC9C8 \uC218\uD398\uB974\uB9AC\uAC00 \uC138\uB9AC\uC5D0 C \uC5EC\uC790\u0022, \u0022th-TH\u0022: \u0022Brazil Superliga Serie C Women\u0022, \u0022vi-VN\u0022: \u0022Brazil Superliga Serie C Women\u0022, \u0022zh-CN\u0022: \u0022\u5DF4\u897F\u5973\u5B50\u6392\u7403\u8D85\u7EA7\u8054\u8D5B\u0022, \u0022zh-TW\u0022: \u0022\u5DF4\u897F\u5973\u5B50\u6392\u7403\u8D85\u7D1A\u806F\u8CFD\u0022}",
  "abbr_map": "{}",
  "create_at": 1759503563559
}
```

## Table: leagues_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.leagues_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('leagues_wp_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | source_name | text | 否 | — |  |
| 4 | en_name | text | 是 | — |  |
| 5 | name_map | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: merge_game_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | — |  |
| 2 | lid | bigint | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: merge_game_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.merge_game_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | integer | 否 | — |  |
| 2 | lid | integer | 否 | — |  |
| 3 | gdate | date | 否 | — |  |
| 4 | gtime | time without time zone | 否 | — |  |
| 5 | siteidmaps | text | 否 | '[]'::text |  |

### Sample（first row）

(empty table)

## Table: openclaw_merge_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.openclaw_merge_BK` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: openclaw_merge_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.openclaw_merge_BS` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: openclaw_merge_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.openclaw_merge_FL` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: openclaw_merge_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.openclaw_merge_HL` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: openclaw_merge_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.openclaw_merge_SC` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: sitegames_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_bk_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 195242,
  "source": "panda",
  "external_game_id": "5454605-2026-06-17",
  "league_id": 1110,
  "home_team_id": 33695,
  "away_team_id": 45046,
  "gdate": "2026-06-17",
  "gtime": "22:30:00",
  "status": "Final",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 84,
  "match_a": 66,
  "gid": 104,
  "league_name": "Israel Youth League",
  "home_name": "Hapoel Givatayim (Youth)",
  "away_name": "Hapoel Tel Aviv Ossish North (Youth)",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022Final\u0022}]",
  "match_detail": "[[1, 84, 66]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781709073839,
  "updated_at": 1781738802479
}
```

## Table: sitegames_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_bm_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 238259,
  "source": "panda",
  "external_game_id": "5464625-2026-06-24",
  "league_id": 308,
  "home_team_id": 3453,
  "away_team_id": 2038,
  "gdate": "2026-06-24",
  "gtime": "00:00:00",
  "status": "PreGame",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 0,
  "match_a": 0,
  "gid": 180,
  "league_name": "US Open - Men Singles",
  "home_name": "Mark Shelley Alcala",
  "away_name": "Matthias Kicklitz",
  "playbyplay": "[]",
  "match_detail": "[]",
  "result": null,
  "other_info": "{}",
  "created_at": 1782191344250,
  "updated_at": 1782211391647
}
```

## Table: sitegames_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_bs_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 218871,
  "source": "panda",
  "external_game_id": "5456865-2026-06-19",
  "league_id": 99,
  "home_team_id": 1038,
  "away_team_id": 1029,
  "gdate": "2026-06-19",
  "gtime": "07:05:00",
  "status": "PreGame",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 0,
  "match_a": 0,
  "gid": 71,
  "league_name": "MiLB Triple A International League",
  "home_name": "Gwinnett Stripers",
  "away_name": "Louisville Bats",
  "playbyplay": "[]",
  "match_detail": "[]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781813864182,
  "updated_at": 1781823186146
}
```

## Table: sitegames_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_ck_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 133571,
  "source": "1xbet.com",
  "external_game_id": "2e5295ae41-2026-06-20-15",
  "league_id": 511,
  "home_team_id": 3062,
  "away_team_id": 3063,
  "gdate": "2026-06-20",
  "gtime": "15:15:00",
  "status": "Final",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 100,
  "match_a": 99,
  "gid": null,
  "league_name": "Nepal. PL Singh Memorial Cup",
  "home_name": "Pokhara Metropolitan",
  "away_name": "Biratnagar Metropolitan",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022Final\u0022}]",
  "match_detail": "[[1, 100, 99]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781873191610,
  "updated_at": 1782026119736
}
```

## Table: sitegames_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_es_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 26771,
  "source": "1xbet.com",
  "external_game_id": "9f5369fdc8-2026-06-17-01",
  "league_id": 1298,
  "home_team_id": 2325,
  "away_team_id": 5506,
  "gdate": "2026-06-17",
  "gtime": "01:00:00",
  "status": "Final",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 2,
  "match_a": 0,
  "gid": null,
  "league_name": "CS 2. POWER Ligaen",
  "home_name": "Linx Legacy Esport",
  "away_name": "Fortress",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022Final\u0022}]",
  "match_detail": "[[1, 13, 10], [2, 13, 2]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781681900764,
  "updated_at": 1781715173084
}
```

## Table: sitegames_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_fl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 2701,
  "source": "1xbet.com",
  "external_game_id": "d2f3a7deba-2026-06-21-07",
  "league_id": 32,
  "home_team_id": 1208,
  "away_team_id": 1213,
  "gdate": "2026-06-21",
  "gtime": "07:00:00",
  "status": "PreGame",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 0,
  "match_a": 0,
  "gid": null,
  "league_name": "CFL",
  "home_name": "Calgary Stampeders",
  "away_name": "Saskatchewan Roughriders",
  "playbyplay": "[]",
  "match_detail": "[]",
  "result": null,
  "other_info": "{\u0022wind\u0022: \u00228.9 NNW\u0022, \u0022country\u0022: \u0022Canada\u0022, \u0022weather\u0022: \u0022Gloomy\u0022, \u0022humidity\u0022: \u002256\u0022, \u0022location\u0022: \u0022McMahon (Calgary)\u0022, \u0022pressure\u0022: \u0022752\u0022, \u0022away_logo\u0022: \u0022{\\\u0022player1\\\u0022: {\\\u0022file_path\\\u0022: \\\u0022logo/FL/1xbet.com/10787.png\\\u0022, \\\u0022file_url\\\u0022: \\\u0022https://v2l.traincdn.com/sfiles/logo_teams/10787.png\\\u0022}}\u0022, \u0022home_logo\u0022: \u0022{\\\u0022player1\\\u0022: {\\\u0022file_path\\\u0022: \\\u0022logo/FL/1xbet.com/10781.png\\\u0022, \\\u0022file_url\\\u0022: \\\u0022https://v2l.traincdn.com/sfiles/logo_teams/10781.png\\\u0022}}\u0022, \u0022temperature\u0022: \u0022\u002B18\u00B0C\u0022}",
  "created_at": 1781823623367,
  "updated_at": 1781996354952
}
```

## Table: sitegames_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_hb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 否 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1967,
  "source": "1xbet.com",
  "external_game_id": "98d1889156-2026-06-17-07",
  "league_id": 290,
  "home_team_id": 2795,
  "away_team_id": 2791,
  "gdate": "2026-06-17",
  "gtime": "07:00:00",
  "status": "Final",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 39,
  "match_a": 9,
  "gid": null,
  "league_name": "Central and South America Clubs Championship. Women",
  "home_name": "Portugues (Women)",
  "away_name": "Deportivo Internacional (Women)",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022Final\u0022}]",
  "match_detail": "[[1, 19, 4], [2, 20, 5]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781681901138,
  "updated_at": 1781736079483
}
```

## Table: sitegames_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_hl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 35880,
  "source": "1xbet.com",
  "external_game_id": "60499dc783-2026-06-17-21",
  "league_id": 364,
  "home_team_id": 1905,
  "away_team_id": 1906,
  "gdate": "2026-06-17",
  "gtime": "21:00:00",
  "status": "InProgress",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 3,
  "match_a": 8,
  "gid": null,
  "league_name": "Russia. MNHL",
  "home_name": "Gladiators",
  "away_name": "Wild Vikings",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022 15:00\u0022}]",
  "match_detail": "[[1, 1, 1], [2, 2, 3], [3, 0, 4]]",
  "result": null,
  "other_info": "{\u0022country\u0022: \u0022Russia\u0022}",
  "created_at": 1781700829834,
  "updated_at": 1781702505547
}
```

## Table: sitegames_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_ma_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 355199,
  "source": "1xbet.com",
  "external_game_id": "198ffcfeb0-2026-06-27-08",
  "league_id": 56,
  "home_team_id": 13528,
  "away_team_id": 3314,
  "gdate": "2026-06-27",
  "gtime": "08:00:00",
  "status": "PreGame",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 0,
  "match_a": 0,
  "gid": null,
  "league_name": "Combatsport. CFFC",
  "home_name": "Matt Gawlik",
  "away_name": "Billy Ray Valdez",
  "playbyplay": "[]",
  "match_detail": "[]",
  "result": null,
  "other_info": "{\u0022location\u0022: \u0022Hard Rock Casino (Rockford)\u0022, \u0022away_logo\u0022: \u0022{\\\u0022player1\\\u0022: {\\\u0022file_path\\\u0022: \\\u0022logo/MA/1xbet.com/22ee6f761bd45a1c16de7525959c16e0.png\\\u0022, \\\u0022file_url\\\u0022: \\\u0022https://v2l.traincdn.com/sfiles/logo_teams/22ee6f761bd45a1c16de7525959c16e0.png\\\u0022}}\u0022, \u0022home_logo\u0022: \u0022{\\\u0022player1\\\u0022: {\\\u0022file_path\\\u0022: \\\u0022logo/MA/1xbet.com/01717a947c716e6ba183eff8400bcf61.png\\\u0022, \\\u0022file_url\\\u0022: \\\u0022https://v2l.traincdn.com/sfiles/logo_teams/01717a947c716e6ba183eff8400bcf61.png\\\u0022}}\u0022}",
  "created_at": 1782383363555,
  "updated_at": 1782384066076
}
```

## Table: sitegames_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_sc_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 否 | — |  |
| 24 | updated_at | bigint | 否 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 4669570,
  "source": "panda",
  "external_game_id": "2067838509107920897-2026-06-19",
  "league_id": 287,
  "home_team_id": 100262,
  "away_team_id": 138677,
  "gdate": "2026-06-19",
  "gtime": "13:16:00",
  "status": "InProgress",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 0,
  "match_a": 0,
  "gid": 2513,
  "league_name": "VS- England Premier League PANDA Exclusive EAFC24",
  "home_name": "Manchester City",
  "away_name": "Burnley",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u00222H 85:14\u0022}, {\u0022Key\u0022: \u0022YellowCard\u0022, \u0022Value\u0022: \u0022[0, 0]\u0022}, {\u0022Key\u0022: \u0022RedCard\u0022, \u0022Value\u0022: \u0022[0, 0]\u0022}, {\u0022Key\u0022: \u0022Corner\u0022, \u0022Value\u0022: \u0022[0, 0]\u0022}]",
  "match_detail": "[[1, 0, 0], [2, 0, 0]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781846178176,
  "updated_at": 1781847011864
}
```

## Table: sitegames_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_tb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 6025583,
  "source": "panda",
  "external_game_id": "5463675-2026-06-23",
  "league_id": 3,
  "home_team_id": 8384,
  "away_team_id": 9025,
  "gdate": "2026-06-23",
  "gtime": "09:30:00",
  "status": "InProgress",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": null,
  "match_a": null,
  "gid": null,
  "league_name": "Czech Liga Pro - Men Singles",
  "home_name": "Ales Bayer",
  "away_name": "Karel Brozik",
  "playbyplay": "[]",
  "match_detail": "[]",
  "result": null,
  "other_info": "{}",
  "created_at": 1782141189371,
  "updated_at": 1782179971711
}
```

## Table: sitegames_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_tn_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 427702,
  "source": "panda",
  "external_game_id": "5454268-2026-06-18",
  "league_id": 3986,
  "home_team_id": 14116,
  "away_team_id": 27707,
  "gdate": "2026-06-18",
  "gtime": "09:15:00",
  "status": "InProgress",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 0,
  "match_a": 0,
  "gid": 581,
  "league_name": "ITF W15 Sapporo - Women Singles",
  "home_name": "Gaeul Jang",
  "away_name": "Himari Sato",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022Set 1\u0022}]",
  "match_detail": "[[1, 0, 0]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781718659593,
  "updated_at": 1781748246094
}
```

## Table: sitegames_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_vb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 11138,
  "source": "1xbet.com",
  "external_game_id": "52d33152bb-2026-06-16-19",
  "league_id": 9,
  "home_team_id": 101,
  "away_team_id": 117,
  "gdate": "2026-06-16",
  "gtime": "19:40:00",
  "status": "Final",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 2,
  "match_a": 1,
  "gid": null,
  "league_name": "UPVL. Nations League",
  "home_name": "France (Pro)",
  "away_name": "Portugal (Pro)",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022Final\u0022}]",
  "match_detail": "[[1, 22, 25], [2, 25, 13], [3, 15, 12]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781681900871,
  "updated_at": 1781696237103
}
```

## Table: sitegames_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.sitegames_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('sitegames_wp_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_game_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | home_team_id | bigint | 否 | — |  |
| 6 | away_team_id | bigint | 否 | — |  |
| 7 | gdate | date | 否 | — |  |
| 8 | gtime | time without time zone | 否 | — |  |
| 9 | status | text | 是 | — |  |
| 10 | gmode | text | 是 | — |  |
| 11 | is_fixed | boolean | 否 | false |  |
| 12 | is_swap | boolean | 否 | false |  |
| 13 | match_h | smallint | 是 | — |  |
| 14 | match_a | smallint | 是 | — |  |
| 15 | gid | bigint | 是 | — |  |
| 16 | league_name | text | 是 | — |  |
| 17 | home_name | text | 是 | — |  |
| 18 | away_name | text | 是 | — |  |
| 19 | playbyplay | jsonb | 否 | '{}'::jsonb |  |
| 20 | match_detail | jsonb | 否 | '[]'::jsonb |  |
| 21 | result | jsonb | 是 | — |  |
| 22 | other_info | jsonb | 否 | '{}'::jsonb |  |
| 23 | created_at | bigint | 是 | — |  |
| 24 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 2837,
  "source": "1xbet.com",
  "external_game_id": "ee4aebc347-2026-06-20-03",
  "league_id": 1,
  "home_team_id": 10,
  "away_team_id": 9,
  "gdate": "2026-06-20",
  "gtime": "03:00:00",
  "status": "Final",
  "gmode": null,
  "is_fixed": false,
  "is_swap": false,
  "match_h": 10,
  "match_a": 14,
  "gid": null,
  "league_name": "Italy. Serie A1",
  "home_name": "Rari Nantes Savona",
  "away_name": "Associazione Nuotatori Brescia",
  "playbyplay": "[{\u0022Key\u0022: \u0022Time\u0022, \u0022Value\u0022: \u0022Final\u0022}]",
  "match_detail": "[[1, 1, 4], [2, 2, 2], [3, 4, 4], [4, 3, 4]]",
  "result": null,
  "other_info": "{}",
  "created_at": 1781722853619,
  "updated_at": 1781982006805
}
```

## Table: siteleagues_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_bk_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 957,
  "source": "panda",
  "external_id": "12482",
  "display_name": "Bulgaria BBL",
  "lid": 370,
  "names": "{\u0022en-US\u0022: \u0022Bulgaria BBL\u0022}",
  "created_at": 1780775748643,
  "updated_at": 1781681557710
}
```

## Table: siteleagues_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_bm_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "Belgian International. Mixed",
  "display_name": "Belgian International. Mixed",
  "lid": null,
  "names": "{\u0022de-DE\u0022: \u0022Belgian International. Gemischtes Doppel\u0022, \u0022es-ES\u0022: \u0022Torneo Internacional. B\u00E9lgica. Parejas mixtas\u0022, \u0022fr-FR\u0022: \u0022Tournoi international. Belgique. Doubles mixtes\u0022, \u0022ja-JP\u0022: \u0022Belgian International. Mixed\u0022, \u0022ko-KR\u0022: \u0022\uC694\uB125\uC2A4 \uBCA8\uAE30\uC5D0 \uC778\uD130\uB0B4\uC154\uB110. \uD63C\uD569\u0022, \u0022pt-PT\u0022: \u0022Torneio Internacional. B\u00E9lgica. Duplas Mistas\u0022, \u0022th-TH\u0022: \u0022Belgian International. Mixed\u0022, \u0022vi-VN\u0022: \u0022Gi\u1EA3i \u0111\u1EA5u qu\u1ED1c t\u1EBF. B\u1EC9. Tr\u00F2 ch\u01A1i h\u1ED7n h\u1EE3p.\u0022, \u0022zh-CN\u0022: \u0022YONEX \u676F\u6BD4\u5229\u65F6\u7FBD\u6BDB\u7403\u56FD\u9645\u8D5B. \u6DF7\u53CC\u0022, \u0022zh-TW\u0022: \u0022YONEX \u676F\u6BD4\u5229\u65F6\u7FBD\u6BDB\u7403\u56FD\u9645\u8D5B. \u6DF7\u53CC\u0022}",
  "created_at": 1757769714185,
  "updated_at": 1781681591345
}
```

## Table: siteleagues_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_bs_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "MLB. 2025. Draft",
  "display_name": "MLB. 2025. Draft",
  "lid": null,
  "names": "{\u0022de-DE\u0022: \u0022MLB. 2025. Draft\u0022, \u0022es-ES\u0022: \u0022MLB. 2025. Draft\u0022, \u0022fr-FR\u0022: \u0022MLB. 2025. Draft\u0022, \u0022ja-JP\u0022: \u0022MLB. 2025. Draft\u0022, \u0022ko-KR\u0022: \u0022MLB. 2025. Draft\u0022, \u0022pt-PT\u0022: \u0022MLB. 2025. Draft\u0022, \u0022th-TH\u0022: \u0022MLB. 2025. Draft\u0022, \u0022vi-VN\u0022: \u0022MLB. 2025. Draft\u0022, \u0022zh-CN\u0022: \u0022MLB. 2025. Draft\u0022, \u0022zh-TW\u0022: \u0022MLB. 2025. Draft\u0022}",
  "created_at": 1752361227000,
  "updated_at": 1781681619490
}
```

## Table: siteleagues_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_ck_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "MAX60 Caribbean",
  "display_name": "MAX60 Caribbean",
  "lid": null,
  "names": "{\u0022de-DE\u0022: \u0022MAX60 Karibik\u0022, \u0022en-US\u0022: \u0022MAX60 Caribbean\u0022, \u0022es-ES\u0022: \u0022MAX60 Caribbean\u0022, \u0022fr-FR\u0022: \u0022MAX60 Cara\u00EFbes\u0022, \u0022ja-JP\u0022: \u0022MAX60 Caribbean\u0022, \u0022ko-KR\u0022: \u0022MAX60 Caribbean\u0022, \u0022pt-PT\u0022: \u0022MAX60 Caribbean\u0022, \u0022th-TH\u0022: \u0022MAX60 Caribbean\u0022, \u0022vi-VN\u0022: \u0022MAX60 Caribbean\u0022, \u0022zh-CN\u0022: \u0022MAX60 Caribbean\u0022, \u0022zh-TW\u0022: \u0022MAX60 Caribbean\u0022}",
  "created_at": 1752777393978,
  "updated_at": 1781681634426
}
```

## Table: siteleagues_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_es_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "external_id": "29096671554801538",
  "display_name": "LOL-LJL Ignite",
  "lid": 1,
  "names": "{\u0022en-US\u0022: \u0022LOL-LJL Ignite\u0022}",
  "created_at": 1750523997953,
  "updated_at": 1781681670907
}
```

## Table: siteleagues_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_fl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "external_id": "1555",
  "display_name": "NFL Preseason",
  "lid": 1,
  "names": "{\u0022en-US\u0022: \u0022NFL Preseason\u0022, \u0022ko-KR\u0022: \u0022NFL \uD504\uB9AC\uC2DC\uC98C\u0022, \u0022th-TH\u0022: \u0022NFL Preseason\u0022, \u0022vi-VN\u0022: \u0022NFL Preseason\u0022, \u0022zh-CN\u0022: \u0022NFL \u7F8E\u56FD\u804C\u4E1A\u7F8E\u5F0F\u8DB3\u7403 - \u5B63\u524D\u8D5B\u0022, \u0022zh-TW\u0022: \u0022NFL \u7F8E\u570B\u8077\u696D\u7F8E\u5F0F\u8DB3\u7403 - \u5B63\u524D\u8CFD\u0022}",
  "created_at": 1754008170160,
  "updated_at": 1781681764002
}
```

## Table: siteleagues_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_hb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "Denmark Super Cup",
  "display_name": "Denmark Super Cup",
  "lid": null,
  "names": "{\u0022de-DE\u0022: \u0022D\u00E4nemark. Superpokal\u0022, \u0022en-US\u0022: \u0022Denmark Super Cup\u0022, \u0022es-ES\u0022: \u0022Dinamarca. Supercopa\u0022, \u0022fr-FR\u0022: \u0022Supercoupe du Danemark\u0022, \u0022ja-JP\u0022: \u0022\u30C7\u30F3\u30DE\u30FC\u30AF\u30B9\u30FC\u30D1\u30FC\u30AB\u30C3\u30D7\u0022, \u0022ko-KR\u0022: \u0022\uB374\uB9C8\uD06C \uC288\uD37C \uCEF5\u0022, \u0022pt-PT\u0022: \u0022Supercopa da Dinamarca\u0022, \u0022th-TH\u0022: \u0022\u0E40\u0E14\u0E19\u0E21\u0E32\u0E23\u0E4C\u0E01 \u0E0B\u0E39\u0E40\u0E1B\u0E2D\u0E23\u0E4C\u0E04\u0E31\u0E1E\u0022, \u0022vi-VN\u0022: \u0022Si\u00EAu C\u00FAp \u0110an M\u1EA1ch\u0022, \u0022zh-CN\u0022: \u0022\u4E39\u9EA6\u8D85\u7EA7\u676F\u0022, \u0022zh-TW\u0022: \u0022\u4E39\u9EA6\u8D85\u7EA7\u676F\u0022}",
  "created_at": 1756072617364,
  "updated_at": 1781681775180
}
```

## Table: siteleagues_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_hl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "NHL. All-Star Game",
  "display_name": "NHL. All-Star Game",
  "lid": null,
  "names": "{\u0022en-US\u0022: \u0022NHL. All-Star Game\u0022}",
  "created_at": 1750398406000,
  "updated_at": 1781681798977
}
```

## Table: siteleagues_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_ma_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "UFC Fight Night. 13.07.25. Special bets",
  "display_name": "UFC Fight Night. 13.07.25. Special bets",
  "lid": null,
  "names": "{\u0022de-DE\u0022: \u0022UFC Fight Night. 13.07.25. Spezialwetten\u0022}",
  "created_at": 1752342505000,
  "updated_at": 1781681842731
}
```

## Table: siteleagues_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_sc_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | double precision | 否 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 2,
  "source": "1xbet.com",
  "external_id": "NM Cup",
  "display_name": "NM Cup",
  "lid": null,
  "names": "{\u0022de-DE\u0022: \u0022Norwegischer Fu\u00DFballpokal\u0022, \u0022en-US\u0022: \u0022NM Cup\u0022, \u0022es-ES\u0022: \u0022Noruega. Copa de Noruega\u0022, \u0022fr-FR\u0022: \u0022Norv\u00E8ge. NM Cup\u0022, \u0022ja-JP\u0022: \u0022\u30CE\u30EB\u30A6\u30A7\u30FC\u30AB\u30C3\u30D7\u0022, \u0022ko-KR\u0022: \u0022NM \uCEF5\u0022, \u0022pt-PT\u0022: \u0022Copa da Noruega\u0022, \u0022th-TH\u0022: \u0022\u0E0A\u0E34\u0E07\u0E16\u0E49\u0E27\u0E22\u0E19\u0E2D\u0E23\u0E4C\u0E40\u0E27\u0E22\u0E4C\u0022, \u0022vi-VN\u0022: \u0022Cu\u0301p Na Uy\u0022, \u0022zh-CN\u0022: \u0022NM \u676F\u0022, \u0022zh-TW\u0022: \u0022NM \u676F\u0022}",
  "created_at": 1750294273425,
  "updated_at": 1781681867136
}
```

## Table: siteleagues_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_tb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 8,
  "source": "1xbet.com",
  "external_id": "Setka Cup",
  "display_name": "Setka Cup",
  "lid": null,
  "names": "{}",
  "created_at": 1781681900763,
  "updated_at": 1781681900693
}
```

## Table: siteleagues_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_tn_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 3122,
  "source": "playbet.com",
  "external_id": "89736052",
  "display_name": "Portugal ATP Challenger Oeiras - Clay",
  "lid": null,
  "names": "{}",
  "created_at": 1778948971865,
  "updated_at": 1781682498859
}
```

## Table: siteleagues_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_vb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 3,
  "source": "panda",
  "external_id": "26088",
  "display_name": "Orange Cup",
  "lid": null,
  "names": "{}",
  "created_at": 1781681900763,
  "updated_at": 1781681900613
}
```

## Table: siteleagues_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteleagues_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteleagues_wp_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | display_name | text | 否 | — |  |
| 5 | lid | bigint | 是 | — |  |
| 6 | names | jsonb | 否 | '{}'::jsonb |  |
| 7 | created_at | bigint | 是 | — |  |
| 8 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "Italy. Serie A1",
  "display_name": "Italy. Serie A1",
  "lid": null,
  "names": "{}",
  "created_at": 1781681901137,
  "updated_at": 1781681900910
}
```

## Table: siteodds_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 37785,
  "market_type": "T12nd QuarterScore",
  "updated_at": 1781721002735,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: 0.85, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022O\u0022}, {\u0022Odd\u0022: 0.85, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022U\u0022}], \u0022Spread\u0022: \u002220\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 10943,
  "market_type": "RBHA",
  "updated_at": 1781681900863,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: true, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 12996,
  "market_type": "T1 Score",
  "updated_at": 1781686769730,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: 0.9, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022O\u0022}, {\u0022Odd\u0022: 0.8, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022U\u0022}], \u0022Spread\u0022: \u00223.5\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 否 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 4513,
  "market_type": "HA",
  "updated_at": 1781683169250,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: true, \u0022Odds\u0022: [{\u0022Odd\u0022: 0.12, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: 5.25, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 29184,
  "market_type": "HA",
  "updated_at": 1781685549711,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: true, \u0022Odds\u0022: [{\u0022Odd\u0022: 0.13, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: 4.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 14598,
  "market_type": "HA",
  "updated_at": 1782071974978,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: true, \u0022Odds\u0022: [{\u0022Odd\u0022: 0.4, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}, {\u0022Odd\u0022: 1.7, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 10407,
  "market_type": "HA",
  "updated_at": 1781970728816,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022N\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022N\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00220\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u0022T\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00225.5\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 15126,
  "market_type": "RBHA",
  "updated_at": 1781771020560,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221.5\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00222.0\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00222.5\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 1680,
  "market_type": "HA",
  "updated_at": 1781703466615,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: true, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 否 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 221521,
  "market_type": "RBCorrect Score",
  "updated_at": 1781686749124,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00222-1\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00223-1\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00223-2\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00224-1\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00224-2\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00224-3\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00221-1\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00222-2\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00223-3\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00224-4\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u0022Other\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00221-2\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00221-3\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00222-3\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00221-4\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00222-4\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u0022Value\u0022}], \u0022Spread\u0022: \u00223-4\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 168159,
  "market_type": "2nd PointRBHA",
  "updated_at": 1781681902973,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00226.5\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 34918,
  "market_type": "RBHA",
  "updated_at": 1781681902939,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: true, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 11064,
  "market_type": "RBHA",
  "updated_at": 1781683054838,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: true, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteodds_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteodds_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | game_id | bigint | 否 | — |  |
| 2 | market_type | text | 否 | — |  |
| 6 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |
| 7 | odds | jsonb | 否 | '{}'::jsonb |  |

### Sample（first row）

```json
{
  "game_id": 702,
  "market_type": "HA",
  "updated_at": 1781805551214,
  "odds": "{\u0022Prices\u0022: [{\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00220\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221.5\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u0022T\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00221X2\u0022, \u0022OriginSpread\u0022: null}, {\u0022Main\u0022: false, \u0022Odds\u0022: [{\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022L\u0022, \u0022OddType\u0022: \u00221\u0022}, {\u0022Odd\u0022: -1.0, \u0022Result\u0022: \u0022W\u0022, \u0022OddType\u0022: \u00222\u0022}], \u0022Spread\u0022: \u00222.5\u0022, \u0022OriginSpread\u0022: null}]}"
}
```

## Table: siteteams_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_bk_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 984,
  "source": "panda",
  "external_id": "126980",
  "league_id": 47,
  "display_name": "Suwon KT Sonicboom B",
  "tid": 472,
  "names": "{\u0022en-US\u0022: \u0022Suwon KT Sonicboom B\u0022}",
  "created_at": 1763732250247,
  "updated_at": 1781681476612
}
```

## Table: siteteams_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_bm_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "Abbygael-Harris-Oliver Butler",
  "league_id": 1,
  "display_name": "Abbygael Harris/Oliver Butler",
  "tid": null,
  "names": "{\u0022de-DE\u0022: \u0022Abbygael Harris/Oliver Butler\u0022, \u0022es-ES\u0022: \u0022Abbygael Harris/Oliver Butler\u0022, \u0022fr-FR\u0022: \u0022Abbygael Harris/Oliver Butler\u0022, \u0022ja-JP\u0022: \u0022\u30A2\u30D3\u30FC\u30AC\u30A8\u30EB\u30FB\u30CF\u30EA\u30B9/Oliver Butler\u0022, \u0022ko-KR\u0022: \u0022\uC560\uBE44\uAC8C\uC77C \uD574\uB9AC\uC2A4/\uC62C\uB9AC\uBC84 \uBC84\uD2C0\uB7EC\u0022, \u0022pt-PT\u0022: \u0022Abbygael Harris/Oliver Butler\u0022, \u0022th-TH\u0022: \u0022Abbygael Harris/Oliver Butler\u0022, \u0022vi-VN\u0022: \u0022Abbygael Harris/Oliver Butler\u0022, \u0022zh-CN\u0022: \u0022\u827E\u6BD4\u76D6\u5C14\u00B7\u54C8\u91CC\u65AF/\u5965\u5229\u5F17\u00B7\u5DF4\u7279\u52D2\u0022, \u0022zh-TW\u0022: \u0022\u827E\u6BD4\u84CB\u723E\u00B7\u54C8\u91CC\u65AF/\u5967\u5229\u4F5B\u00B7\u5DF4\u7279\u52D2\u0022}",
  "created_at": 1757665065597,
  "updated_at": 1781681591345
}
```

## Table: siteteams_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_bs_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "MLB. 2025. Number 1 Overall Draft Pick",
  "league_id": 1,
  "display_name": "MLB. 2025. Number 1 Overall Draft Pick",
  "tid": null,
  "names": "{\u0022de-DE\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022es-ES\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022fr-FR\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022ja-JP\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022ko-KR\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022pt-PT\u0022: \u0022MLB. 2025. Primeiro jogador selecionado no Draft\u0022, \u0022th-TH\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022vi-VN\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022zh-CN\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022, \u0022zh-TW\u0022: \u0022MLB. 2025. Number 1 Overall Draft Pick\u0022}",
  "created_at": 1752361227000,
  "updated_at": 1781681619490
}
```

## Table: siteteams_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_ck_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "Boca Raton Trailblazers",
  "league_id": 1,
  "display_name": "Boca Raton Trailblazers",
  "tid": null,
  "names": "{\u0022de-DE\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022en-US\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022es-ES\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022fr-FR\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022ja-JP\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022ko-KR\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022pt-PT\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022th-TH\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022vi-VN\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022zh-CN\u0022: \u0022Boca Raton Trailblazers\u0022, \u0022zh-TW\u0022: \u0022Boca Raton Trailblazers\u0022}",
  "created_at": 1752762319059,
  "updated_at": 1781681634426
}
```

## Table: siteteams_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_es_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 7451,
  "source": "1xbet.com",
  "external_id": "ZANSIDE GAMING",
  "league_id": 1341,
  "display_name": "ZANSIDE GAMING",
  "tid": null,
  "names": "{}",
  "created_at": 1781683243462,
  "updated_at": 1781683243449
}
```

## Table: siteteams_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_fl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1340,
  "source": "panda",
  "external_id": "316849",
  "league_id": 24,
  "display_name": "Saskatchewan Roughriders",
  "tid": 147,
  "names": "{}",
  "created_at": 1782349248272,
  "updated_at": 1782349248258
}
```

## Table: siteteams_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_hb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "Aalborg",
  "league_id": 1,
  "display_name": "Aalborg",
  "tid": null,
  "names": "{\u0022de-DE\u0022: \u0022Aalborg H\u00E5ndbold\u0022, \u0022en-US\u0022: \u0022Aalborg\u0022, \u0022es-ES\u0022: \u0022GK Aalborg\u0022, \u0022fr-FR\u0022: \u0022Aalborg\u0022, \u0022ja-JP\u0022: \u0022\u30AA\u30FC\u30EB\u30DC\u30FC\u30B0\u0022, \u0022ko-KR\u0022: \u0022\uC62C\uBC84\uADF8\u0022, \u0022pt-PT\u0022: \u0022Aalborg\u0022, \u0022th-TH\u0022: \u0022Aalborg\u0022, \u0022vi-VN\u0022: \u0022Aalborg\u0022, \u0022zh-CN\u0022: \u0022\u5965\u5C14\u5821\u0022, \u0022zh-TW\u0022: \u0022\u5967\u723E\u5821\u0022}",
  "created_at": 1756072617365,
  "updated_at": 1781681775180
}
```

## Table: siteteams_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_hl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "Team MacKinnon",
  "league_id": 1,
  "display_name": "Team MacKinnon",
  "tid": null,
  "names": "{\u0022en-US\u0022: \u0022Team MacKinnon\u0022}",
  "created_at": 1707101829000,
  "updated_at": 1781681798977
}
```

## Table: siteteams_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_ma_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "UFC Fight Night. 13.07.25. Fight of the night",
  "league_id": 1,
  "display_name": "UFC Fight Night. 13.07.25. Fight of the night",
  "tid": null,
  "names": "{\u0022de-DE\u0022: \u0022UFC Fight Night. 13.07.25. Fight of the night\u0022}",
  "created_at": 1752342505000,
  "updated_at": 1781681842731
}
```

## Table: siteteams_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_sc_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 否 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 102018,
  "source": "panda",
  "external_id": "313439",
  "league_id": 3270,
  "display_name": "Guangdong Chenxingjuli",
  "tid": 23120,
  "names": "{\u0022ko-KR\u0022: \u0022\uAD11\uB465 \uBAA8\uB2DD\uC2A4\uD0C0 \uD30C\uC6CC\u0022, \u0022th-TH\u0022: \u0022Guangdong Chenxingjuli\u0022, \u0022vi-VN\u0022: \u0022Guangdong Chenxingjuli\u0022, \u0022zh-CN\u0022: \u0022\u5E7F\u4E1C\u6668\u661F\u805A\u529B\u0022, \u0022zh-TW\u0022: \u0022\u5EE3\u6771\u6668\u661F\u805A\u529B\u0022}",
  "created_at": 1781178005995,
  "updated_at": 1781682165622
}
```

## Table: siteteams_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_tb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 7603,
  "source": "1xbet.com",
  "external_id": "Zinaida Drak",
  "league_id": 30,
  "display_name": "Zinaida Drak",
  "tid": null,
  "names": "{}",
  "created_at": 1781682437521,
  "updated_at": 1781682437515
}
```

## Table: siteteams_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_tn_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 41146,
  "source": "1xbet.com",
  "external_id": "Lekomtseva-Jialin",
  "league_id": 3051,
  "display_name": "Lekomtseva/Jialin",
  "tid": null,
  "names": "{\u0022de-DE\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022en-US\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022es-ES\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022fr-FR\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022ja-JP\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022ko-KR\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022pt-PT\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022th-TH\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022vi-VN\u0022: \u0022Lekomtseva/Jialin\u0022, \u0022zh-CN\u0022: \u0022\u83B1\u79D1\u59C6\u91C7\u5A03/\u5BB6\u6797\u0022, \u0022zh-TW\u0022: \u0022\u840A\u79D1\u59C6\u63A1\u5A03/\u5BB6\u6797\u0022}",
  "created_at": 1758629771212,
  "updated_at": 1781682497076
}
```

## Table: siteteams_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_vb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 11037,
  "source": "1xbet.com",
  "external_id": "Canada (Women)",
  "league_id": 7,
  "display_name": "Canada (Women)",
  "tid": null,
  "names": "{}",
  "created_at": 1781683075939,
  "updated_at": 1781683075934
}
```

## Table: siteteams_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.siteteams_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('siteteams_wp_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | external_id | text | 否 | — |  |
| 4 | league_id | bigint | 否 | — |  |
| 5 | display_name | text | 否 | — |  |
| 6 | tid | bigint | 是 | — |  |
| 7 | names | jsonb | 否 | '{}'::jsonb |  |
| 8 | created_at | bigint | 是 | — |  |
| 9 | updated_at | bigint | 是 | ((EXTRACT(epoch FROM now()) * (1000)::numeric))::bigint |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "1xbet.com",
  "external_id": "R.N. Salerno",
  "league_id": 1,
  "display_name": "R.N. Salerno",
  "tid": null,
  "names": "{}",
  "created_at": 1781681901155,
  "updated_at": 1781681900910
}
```

## Table: teams_bk

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_bk` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_bk_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Czech Republic (W)",
  "namemap": "{\u0022en-US\u0022: \u0022Czech Republic (W)\u0022, \u0022ko-KR\u0022: \u0022\uCCB4\uCF54 (W)\u0022, \u0022th-TH\u0022: \u0022Czech Republic (W)\u0022, \u0022vi-VN\u0022: \u0022Czech Republic (W)\u0022, \u0022zh-CN\u0022: \u0022\u6377\u514B(\u5973)\u0022, \u0022zh-TW\u0022: \u0022\u6377\u514B(\u5973)\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1751252239881
}
```

## Table: teams_bm

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_bm` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_bm_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Mio Molin / Max Svensson",
  "namemap": "{}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1758338818810
}
```

## Table: teams_bs

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_bs` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_bs_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "National League All Stars",
  "namemap": "{\u0022en-US\u0022: \u0022National League All Stars\u0022, \u0022ko-KR\u0022: \u0022\uB0B4\uC154\uB110 \uB9AC\uADF8 \uC62C\uC2A4\uD0C0\u0022, \u0022th-TH\u0022: \u0022National League All Stars\u0022, \u0022vi-VN\u0022: \u0022National League All Stars\u0022, \u0022zh-CN\u0022: \u0022\u56FD\u5BB6\u8054\u76DF\u5168\u660E\u661F\u0022, \u0022zh-TW\u0022: \u0022\u570B\u5BB6\u806F\u76DF\u5168\u660E\u661F\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1752639534009
}
```

## Table: teams_ck

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_ck` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_ck_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "266666",
  "namemap": "{}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1754030521788
}
```

## Table: teams_es

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_es` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_es_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Bamboo Juice",
  "namemap": "{\u0022en-US\u0022: \u0022Bamboo Juice\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1749182101574
}
```

## Table: teams_fl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_fl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_fl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Los Angeles Chargers",
  "namemap": "{\u0022en-US\u0022: \u0022Los Angeles Chargers\u0022, \u0022ko-KR\u0022: \u0022\uB85C\uC2A4\uC564\uC824\uB808\uC2A4 \uCC28\uC800\uC2A4\u0022, \u0022th-TH\u0022: \u0022Los Angeles Chargers\u0022, \u0022vi-VN\u0022: \u0022Los Angeles Chargers\u0022, \u0022zh-CN\u0022: \u0022\u6D1B\u6749\u77F6\u95EA\u7535\u0022, \u0022zh-TW\u0022: \u0022\u6D1B\u6749\u78EF\u96FB\u5149\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1763450425000
}
```

## Table: teams_hb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_hb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_hb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: teams_hl

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_hl` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_hl_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Portland Winter Hawks",
  "namemap": "{\u0022en-US\u0022: \u0022Portland Winter Hawks\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1757653547472
}
```

## Table: teams_ma

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_ma` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_ma_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: teams_sc

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_sc` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_sc_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "ES Mostaganem",
  "namemap": "{\u0022en-US\u0022: \u0022ES Mostaganem\u0022, \u0022ko-KR\u0022: \u0022ES \uBAA8\uC2A4\uD0C0\uAC00\uB134\u0022, \u0022th-TH\u0022: \u0022ES Mostaganem\u0022, \u0022vi-VN\u0022: \u0022ES Mostaganem\u0022, \u0022zh-CN\u0022: \u0022\u83AB\u65AF\u5854\u52A0\u5185\u59C6\u0022, \u0022zh-TW\u0022: \u0022\u83AB\u65AF\u5854\u52A0\u5167\u59C6\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1743042658894
}
```

## Table: teams_tb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_tb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_tb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Tianyi Qian / Xunyao Shi",
  "namemap": "{\u0022ko-KR\u0022: \u0022\uCCB8 \uD150\uC774 / \uC2DC \uC21C\uC57C\uC624\u0022, \u0022th-TH\u0022: \u0022Tianyi Qian / Xunyao Shi\u0022, \u0022vi-VN\u0022: \u0022Tianyi Qian / Xunyao Shi\u0022, \u0022zh-CN\u0022: \u0022\u94B1\u5929\u4E00 / \u77F3\u6D35\u7476\u0022, \u0022zh-TW\u0022: \u0022\u9322\u5929\u4E00 / \u77F3\u6D35\u7464\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1757242719433
}
```

## Table: teams_tn

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_tn` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_tn_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Tibo Colson",
  "namemap": "{\u0022en-US\u0022: \u0022Tibo Colson\u0022, \u0022ko-KR\u0022: \u0022\uC2A4\uD305 \uCF5C\uC2A8\u0022, \u0022th-TH\u0022: \u0022Tibo Colson\u0022, \u0022vi-VN\u0022: \u0022Tibo Colson\u0022, \u0022zh-CN\u0022: \u0022\u8482\u535A\u00B7\u79D1\u5C14\u68EE\u0022, \u0022zh-TW\u0022: \u0022\u8482\u535A\u00B7\u79D1\u723E\u68EE\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1764726297000
}
```

## Table: teams_vb

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_vb` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_vb_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

```json
{
  "id": 1,
  "source": "panda",
  "lid": 1,
  "tname": "Sesi Volei Bauru (W)",
  "namemap": "{\u0022ko-KR\u0022: \u0022\uC138\uC2DC \uBCFC\uB808\uC774 \uBC14\uC6B0\uB8E8 (W)\u0022, \u0022th-TH\u0022: \u0022Sesi Volei Bauru (W)\u0022, \u0022vi-VN\u0022: \u0022Sesi Volei Bauru (W)\u0022, \u0022zh-CN\u0022: \u0022\u5305\u9C81(\u5973)\u0022, \u0022zh-TW\u0022: \u0022\u5305\u9B6F(\u5973)\u0022}",
  "abbr_map": "{}",
  "namemapcount": 0,
  "otherinfo": "{}",
  "create_at": 1759442375707
}
```

## Table: teams_wp

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.teams_wp` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | bigint | 否 | nextval('teams_wp_id_seq'::regclass) |  |
| 2 | source | text | 否 | — |  |
| 3 | lid | bigint | 否 | — |  |
| 4 | tname | text | 否 | — |  |
| 5 | namemap | jsonb | 否 | '{}'::jsonb |  |
| 6 | abbr_map | jsonb | 否 | '{}'::jsonb |  |
| 7 | namemapcount | bigint | 否 | 0 |  |
| 8 | otherinfo | jsonb | 否 | '{}'::jsonb |  |
| 9 | create_at | bigint | 是 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_mergeleague_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_mergeleague_BK` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | site | text | 否 | — |  |
| 2 | sitelid | text | 否 | — |  |
| 3 | league | text | 否 | — |  |
| 4 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_mergeleague_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_mergeleague_BS` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | site | text | 否 | — |  |
| 2 | sitelid | text | 否 | — |  |
| 3 | league | text | 否 | — |  |
| 4 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_mergeleague_ES

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_mergeleague_ES` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | site | text | 否 | — |  |
| 2 | sitelid | text | 否 | — |  |
| 3 | league | text | 否 | — |  |
| 4 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_mergeleague_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_mergeleague_FL` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | site | text | 否 | — |  |
| 2 | sitelid | text | 否 | — |  |
| 3 | league | text | 否 | — |  |
| 4 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_mergeleague_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_mergeleague_HL` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | site | text | 否 | — |  |
| 2 | sitelid | text | 否 | — |  |
| 3 | league | text | 否 | — |  |
| 4 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_mergeleague_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_mergeleague_SC` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | site | text | 否 | — |  |
| 2 | sitelid | text | 否 | — |  |
| 3 | league | text | 否 | — |  |
| 4 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_mergeleague_TN

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_mergeleague_TN` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | site | text | 否 | — |  |
| 2 | sitelid | text | 否 | — |  |
| 3 | league | text | 否 | — |  |
| 4 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_merge_BK

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_merge_BK` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_merge_BS

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_merge_BS` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_merge_FL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_merge_FL` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_merge_HL

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_merge_HL` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

### Sample（first row）

(empty table)

## Table: test_openclaw_merge_SC

| 屬性 | 值 |
|------|-----|
| 完整名稱 | `Games.public.test_openclaw_merge_SC` |
| 引擎 | postgresql |
| Primary Key | — |

### Columns

| # | 欄位 | 型態 | Nullable | 預設 | 備註 |
|---|------|------|:--------:|------|------|
| 1 | id | text | 否 | — |  |
| 2 | gdate | date | 否 | — |  |
| 3 | gtime | time without time zone | 否 | — |  |
| 4 | lid | text | 否 | — |  |
| 5 | siteidmaps | jsonb | 否 | — |  |

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
