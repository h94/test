# 整包更新监控玩法设定

## 1. 场景目的
后台运维人员使用此API，以完整覆盖的方式更新指定球种（game_type）的监控玩法配置，确保该球种所有受监控玩法清单被替换为新设定，并触发下游同步与稽核记录。

## 2. 入口 API
| Method | Path | 说明 |
|---|---|---|
| PUT | /api/monitored_play_modes/{game_type} | 更新指定球种的监控玩法设定，请求体为完整的新玩法清单与操作者账号。 |

## 3. 流程总览
1. 接收PUT请求，提取路径参数 `game_type` 与请求体（含 `play_mode`、`operator_account`）。
2. 参数校验：`play_mode` 必填且为合法JSON数组，`operator_account` 不可为空。
3. 查询 `monitored_play_modes` 表获取当前记录（取旧值用于变更记录）。
4. 执行UPDATE（或UPSERT）**整包替换** `play_mode` 与 `operator_account`，更新 `updated_at`。
5. 写入 `threshold_changelog` 表记录变更详情（old_value / new_value）。
6. 写入 `threshold_sync_pending` 表产生同步任务，供后台Worker排程推播下游。
7. 返回成功响应（200）。

## 4. 程式流程
| 顺序 | Layer | Class / Method | 动作 |
|---|---|---|---|
| 1 | Controller | `MonitoredPlayModesResource.put(game_type)` | 接收请求，调用Service层。 |
| 2 | Service | `MonitoredPlayModesService.update(game_type, play_mode, operator_account)` | 调用Provider获取当前记录，执行业务更新逻辑，触发稽核与同步。 |
| 3 | Provider | `MonitoredPlayModesProvider.get_by_game_type(game_type)` | 执行 `SELECT ... FROM monitored_play_modes WHERE game_type = $1` 获取整行数据（含旧play_mode）。 |
| 4 | Provider | `MonitoredPlayModesProvider.replace(game_type, play_mode, operator_account)` | 执行 `INSERT ... ON CONFLICT (game_type) DO UPDATE SET ...` 或直接 `UPDATE`，覆盖play_mode与operator_account，并刷新 `updated_at`。 |
| 5 | Provider | `ThresholdChangeLogProvider.insert(...)` | 向 `threshold_changelog` 写入一笔变更日志（table_name='monitored_play_modes'，record_key，old_value，new_value，operator_account）。 |
| 6 | Provider | `ThresholdSyncPendingProvider.enqueue(...)` | 向 `threshold_sync_pending` 写入待同步记录（table_name='monitored_play_modes'，record_key=game_type）。 |

> **注**：以上类名与方法名基于项目分层命名惯例推断，实际代码可能略有差异。

## 5. DB / Cache / Queue 使用
| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB | `monitored_play_modes` | Read (SELECT) | 获取当前play_mode值，用于稽核比对。 |
| DB | `monitored_play_modes` | Write (INSERT/UPDATE) | 整包覆盖play_mode与operator_account。 |
| DB | `threshold_changelog` | Write (INSERT) | 记录设定变更，包含旧值、新值及操作者，满足稽核要求。 |
| DB | `threshold_sync_pending` | Write (INSERT) | 产出同步任务（pending），后续由Worker消费并通过Kafka或其他通道通知下游。 |

> 当前流程未使用Redis或直接操作Kafka；同步通知依赖于 `threshold_sync_pending` 表与后台Worker的搭配。

## 6. 重要规则
- **整包覆盖**：请求体的 `play_mode` 会完全取代现有记录的 `play_mode` 字段，非增量合并。
- **操作者必填**：`operator_account` 不可为空，用于稽核与责任追溯。
- **稽核强制性**：依据系统整体设计，所有阀值设定异动都必须写入 `threshold_changelog`。*(证据：README - “阀值異動皆寫入 changelog，並將變更排入同步佇列供下游消费”)*
- **同步触发**：必须写入 `threshold_sync_pending` 以确保监控引擎及时获取最新配置。
- **幂等性**：重复发送相同请求不会破坏数据，但每次都会产生新的changelog记录（时间戳不同）。
- **存在性需求**：**需人工确认**：若指定的 `game_type` 不存在，系统应返回404还是自动建立新记录（类似UPSERT）。

## 7. 错误情境
| 情境 | 预判结果 |
|---|---|
| 请求体格式错误（play_mode非JSON数组） | HTTP 422 参数校验失败 |
| `operator_account`缺失或为空 | HTTP 422 参数校验失败 |
| `game_type`不存在 | 需人工确认：推测返回404或自动建立（若建立则返回200） |
| 数据库连接失败 / 写入超时 | HTTP 500 内部服务器错误 |
| `threshold_sync_pending`写入失败 | 可能回滚主表更新（需确认事务边界）；或记录错误日志并触发告警 |

## 8. 测试重点
| Test ID | 类型 | 情境 | 预判结果 |
|---|---|---|---|
| TC01 | API Test | 正常更新已有球种，提供合法`play_mode`与`operator_account` | 200，DB记录更新，changelog与同步记录生成 |
| TC02 | API Test | 更新一个不存在的`game_type` | 需确认返回404或201/200（若自动创建） |
| TC03 | API Test | 请求体`operator_account`字段缺失 | 422 |
| TC04 | Integration Test | 验证changelog记录的`old_value`和`new_value`一致 | 变更日志内容与请求相符 |
| TC05 | Flow Test | 验证同步任务被后台Worker消费，并向监控引擎发送更新 | 同步任务状态转为done，下游收到最新玩法清单 |

## 9. 高風險區域
- **误覆盖原有玩法**：整包替换意味着未在新清单中出现的玩法将立即失效，可能导致线上监控遗漏，前端应要求二次确认。
- **同步队列一致性**：若主表更新成功但写入`threshold_sync_pending`失败（且不在同一事务中），将导致下游配置过时，监控产生缺口。
- **变更日志堆积**：频繁修改可能使`threshold_changelog`急速增长，需确保定期清理机制（如每日清理过期记录）有效运作。

## 10. 常見錯誤
- **混淆POST与PUT**：POST用于新建（已存在则409），PUT用于整包更新；误用可能导致意外报错。
- **遗漏操作者信息**：未在请求体中提供`operator_account`，导致校验失败。
- **未查看历史配置**：直接覆盖前未查询当前值以备份，恢复困难。
- **误解幂等性**：认为重复请求不会产生额外日志，实际每次都会新增changelog。

## 11. Evidence
| 类型 | 来源 |
|---|---|
| API | OpenAPI `PUT /api/monitored_play_modes/{game_type}` (description: “整包覆蓋更新監控玩法”) |
| DB Schema | `migrations/001_create_core_tables.sql` - `monitored_play_modes` |
| DB Schema | `migrations/002_create_supplement_tables.sql` - `threshold_changelog` |
| DB Schema | `migrations/003_create_sync_tables.sql` - `threshold_sync_pending` |
| 业务规则 | README § 資料完整性與稽核 |
| 代码推断 | Provider/MonitoredPlayModes.py (基于专案分层约定) |