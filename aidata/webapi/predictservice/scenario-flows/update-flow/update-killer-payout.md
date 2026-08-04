# 执行Killer派彩

## 1. 场景目的
结算特定Killer周期，根据周期内杀手表现（profitpoint）计算派彩，更新周期派彩状态，并通过 `memberservice` 通知发放奖金给符合条件的杀手。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| PUT | `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}/payout` | 执行指定游戏类型、联赛、周期的Killer派彩 |

---

## 3. 流程總覽

1. 接收派彩请求（`gameType`, `lid`, `cid`）
2. 验证操作者权限（需后管理权限）
3. 验证 `killer_cycle_settings` 周期是否存在且未结束
4. 查询 `killeraccounts_{gameType}` 名列，依 `profitpoint` 排序筛选应得奖者
5. 计算应得奖金
6. 更新周期 `killer_cycle_settings.pay_out` 为 `true`
7. 写入 `activities_winneraccounts`（记录得奖信息）
8. 调用 `memberservice` 派发实际奖金（profitpoint 或 coin）
9. 清除相关 Redis 快取（如 `predict:activity:{site}:{event}:{cid}:leaderboard`、`predict:winners:{cid}`）
10. 记录计算日志至 `calculate_logs`
11. 回传操作成功
12. 若流程失败，不写入任何状态并回传错误（保持幂等重试安全）

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | `PayoutController.PayoutKillerCycle` | 接收请求参数，调用 Service |
| 2 | Validator | `KillerPayoutValidator` | 验证 `gameType`、`lid`、`cid` 非空，周期存在且 `pay_out=false`，请求者有管理权限 |
| 3 | Service | `KillerService.ExecutePayout` | 核心结算逻辑：查询杀手、计算奖金、更新状态 |
| 4 | Provider | `KillerProvider.FetchKillerAccounts` | 从 Cassandra `killeraccounts_{gameType}` 读取杀手列表（WHERE lid=?, cid=? ORDER BY profitpoint DESC） |
| 5 | Provider | `CycleProvider.GetCycle` | 从 `killer_cycle_settings` 读取周期设定（赔率、奖金池等） |
| 6 | Service | `KillerService.CalculatePayout` | 依 cycle payout 规则计算每位杀手应得金额 |
| 7 | Provider | `KillerProvider.MarkCyclePaid` | 更新 `killer_cycle_settings.pay_out=true` |
| 8 | Provider | `WinnerAccountProvider.InsertWinners` | 写入 `activities_winneraccounts`（game_type, lid, cid, account, rank, profitpoint） |
| 9 | Transfer | `MemberServiceTransfer.PayoutRewards` | 呼叫 `memberservice` API 发放奖金（批量或逐个） |
| 10 | Provider | `CalculateLogProvider.AddLog` | 记录 `week_id` 或 `cid` 相关运算日志 |
| 11 | Provider | `CacheProvider.Invalidate` | DEL Redis keys: `predict:killer:{gameType}:{lid}:{cid}` 相关快取 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.killer_cycle_settings` | Read | 读取周期设定（如 pay_out 状态、奖金规则） |
| DB | `predict.killer_cycle_settings` | Update | 设定 `pay_out=true` 防止重复派发 |
| DB | `predict.killeraccounts_{gameType}` | Read | 读取该周期杀手列表和 profitpoint |
| DB | `predict.activities_winneraccounts` | Write | 记录得奖者 rank/profitpoint（注意 account 脱敏） |
| DB | `predict.calculate_logs` | Write | 记录结算日志（week_id / cid, result） |
| Redis | `predict:activity:{site}:{event}:{cid}:leaderboard` | Delete | 清理受影响周期排行榜快取 |
| Redis | `predict:winners:{cid}` | Delete | 清理赢家快取 |
| Queue | `memberservice` API | Call | 通知发放奖金（非 Redis/Kafka，直接 HTTP/gRPC） |

---

## 6. 重要規則

- **權限限制**：仅後台管理員或排程可执行（由 ECFramework 验证 `rank` 或 role）。
- **不可重複派彩**：`killer_cycle_settings.pay_out` 为 `true` 时拒绝操作；此流程必须原子性：`pay_out` 写入成功后才调用 `memberservice`。
- **殺手排名規則**：`killeraccounts_{gameType}` 查询必须依 `lid`, `cid` 过滤，并按 `profitpoint DESC` 排序；仅取有效名次（通常前 N 名，依周期设定）。
- **不可暴露資料**：`activities_winneraccounts` 写入得奖者账户，但对外 API 不可完整回传 account（需脱敏）；profitpoint 可显示。
- **Transaction 規則**：Cassandra 无强事务，流程应确保 `pay_out=true` 设置成功后才进行后继写入和分发；若 `memberservice` 调用失败，需补偿或回写失败日志，不可仅回退 Cassandra（因为已写入不可逆）。
- **Retry 規則**：若 `memberservice` 失败，应记录 `calculate_logs` 为部分失败，并触发重试（或人工介入）。不可再将 `pay_out` 回退为 false，但可设计「派发失败」状态。
- **TTL 規則**：清理 Redis 排行榜相关键，立刻生效，不等 TTL。
- **不可修改欄位**：已结算的 `killeraccounts` 不可修改 `profitpoint`；`activities_winneraccounts` 写入后不可人工调整。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 无杀手或杀手均已出局 | 无得奖者，周期仍标记为 `pay_out=true`，派奖 0 |
| `pay_out` 已为 `true` | 拒絕請求，回傳 409 Conflict |
| 周期不存在 | 回傳 404 Not Found |
| 管理員權限不足 | 回傳 403 Forbidden |
| `memberservice` 调用超时/失败 | 保留 `pay_out=true`，记录错误日志，返回 502 或 200 with warning；需后绪重试机制 |
| `activities_winneraccounts` 写入失败 | 可能中断流程，回传 500（需人工确认，建议将此写入放在 `memberservice` 成功之后） |
| Redis DEL 失败 | 不影响主流程，记录 warn 日志 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| TST-KP-01 | Flow Test | 正常派彩：存在杀手，profitpoint > 0 | 周期 `pay_out=true`，得奖者记录写入，memberservice 被调用一次每个杀手 |
| TST-KP-02 | Permission Test | 非管理员调用 | 403 Forbidden |
| TST-KP-03 | API Test | 周期已派彩，重复请求 | 409 Conflict |
| TST-KP-04 | Integration Test | memberservice 调用失败（模拟超时） | 系统返回部分失败状态，日志记录错误，cycle `pay_out=true` 保持 |
| TST-KP-05 | API Test | 不存在的 lid/cid | 404 Not Found |
| TST-KP-06 | Flow Test | 无杀手名单 | `pay_out=true`，无 winner 写入，不调用 memberservice |
| TST-KP-07 | Flow Test | 周期状态在 payout 同时被修改（并发） | 仅一次成功设置 `pay_out=true`，另一个请求看到 409 |

---

## 9. 高風險區域

- **高風險 table**：`killer_cycle_settings.pay_out`（幂等键，一旦设 true 不可逆）；`activities_winneraccounts`（得奖者记录，敏感数据）。
- **高風險 API**：`PUT /payout` 可能被重放攻击或误触，需 idempotency key 或状态控制。
- **跨服務資料同步**：派发奖金依赖 `memberservice` 健康；无分布式事务，失败后可能数据不一致（杀手已记录得奖但实际钱未发）。
- **Transaction**：Cassandra 批量写入（`pay_out` + `activities_winneraccounts`）非原子；建议先写 `activities_winneraccounts`，再 `pay_out=true`，最后调 `memberservice`；失败时可回滚已写赢家记录（但需补偿逻辑）。
- **Cache consistency**：删除 Redis 键失败不影响数据正确性，但会导致旧排行短暂显示。
- **Idempotency**：强烈建议客户端传入 idempotency key 或用 `cid`+`gameType` 作唯一标识，防止网络重试导致重复派发。

---

## 10. 常見錯誤

- ❌ 在 `memberservice` 调用前就标记 `pay_out=true`，然后 member 服务失败，导致钱未发但状态显示已派发。
- ❌ 未检查杀手周期设定 `payout` 状态直接调用，导致重复发奖。
- ❌ 查询 `killeraccounts` 时不加 `lid` 和 `cid` 过滤，全表扫描影响性能。
- ❌ `activities_winneraccounts` 写入 account 时未脱敏，外泄个资。
- ❌ 忘记清理 Redis 排行榜快取，前台仍显示旧周期信息。
- ❌ 未对 `memberservice` 调用失败做补偿重试，造成实际未发放奖金。
- AI 容易误解为系统直接发放现金或积分，实际必须通过 `memberservice` 代理金流。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | PUT /api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}/payout (README Killer 機制)|
| DB | `predict.killer_cycle_settings` ( pay_out ) |
| DB | `predict.killeraccounts_{gameType}` ( lid, cid, profitpoint ) |
| DB | `predict.activities_winneraccounts` ( rank, profitpoint, account 需脱敏) |
| Service | `KillerService.ExecutePayout` / CalculatePayout |
| 跨服務 | README 服務相依：`memberservice` 发獎金 |
| Rule | predict-detail: `activities_winneraccounts` 值僅由結算排程寫入，不可人工調整 |
| Redis | predict-detail: `predict:activity:{site}:{event}:{cid}:leaderboard`, `predict:winners:{cid}` 需清理 |
| Code | 需人工確認 Controller/Service 具体实现类名（本文依据 README 及 DB 邊界推論） |