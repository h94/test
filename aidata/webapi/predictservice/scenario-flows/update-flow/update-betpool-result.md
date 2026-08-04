# 更新奖池结果

## 1. 场景目的

设定奖池赛事（BetPool Game）的获胜选项，并触发后续派彩流程。此 API 仅接受获胜选项键值，由内部计算赢家与奖金，不会由外部直接指定派彩金额。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| PUT | `/api/v1/betpool/games/{id}/result` | 更新奖池赛事结果，设定获胜选项 |

---

## 3. 流程总览

1. 接收结果更新请求，含 `id`（赛事主键）与获胜选项
2. 验证请求身份与权限（需具有管理或结帳权限）
3. 根据 `id` 查询 `predict.betpool_games`，取得赛事资料
4. 校验游戏状态（需为「已关闭」或「待结算」状态，且尚未 payout）
5. 写⼊ `winresult`（获胜选项）至 `predict.betpool_games`，同步更新 `status` 为「结算中」
6. 删除 Redis 快取 `predict:game:{id}:status`，确保前台立即取得最新状态
7. 计算所有注单赢家，更新 `predict.betpool_bets` 的 `winlose` 与 `profitzcoin`
8. 调用外部服务执行真实金流扣款或派彩（由 MemberService / TransactionService 处理，本服务仅保存计算结果）
9. 派彩完成后，设置 `payout` 为 `true`，并再次删除 Redis 快取

---

## 4. 程式流程

| 顺序 | Layer | Class / Method | 动作 |
|---|---|---|---|
| 1 | Controller | `BetPoolController.UpdateResult` | 接收 HTTP PUT 请求，验证模型合法性 |
| 2 | Validator | `BetPoolValidator` | 检查 `id` 不为空、获胜选项为合法选单键 |
| 3 | Service | `BetPoolService.SetResultAsync` | 查询赛事资料，验证状态与权限 |
| 4 | Provider | `BetPoolDataProvider` | 读取 `betpool_games`，写入 `winresult` 与状态 |
| 5 | Provider | `RedisProvider` | 删除 `predict:game:{id}:status` 快取 |
| 6 | Service | `PayoutCalculatorService` | 迭代所有 `betpool_bets`，标记赢家与计算利润 |
| 7 | Provider | `BetPoolDataProvider` | 更新 `betpool_bets` 的 `winlose` 与 `profitzcoin` |
| 8 | Provider | `ExternalServiceProxy` | 通知 MemberService 执行余额变动（加钱或扣钱） |
| 9 | Provider | `BetPoolDataProvider` | 设置 `payout = true` |
| 10 | Provider | `RedisProvider` | 再次删除 `predict:game:{id}:status` 快取 |

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.betpool_games` | Read | 依主键 `id` 查询赛事，取得 `status`、`payout`、`betoptions` |
| DB | `predict.betpool_games` | Write | 设定 `winresult`，更新 `status` 至「结算中」 |
| DB | `predict.betpool_games` | Write | 派彩完成后设定 `payout = true` |
| DB | `predict.betpool_bets` | Read | 查詢所有此游戏 `gid` 的注单，读取 `betoption`、`betzcoin` |
| DB | `predict.betpool_bets` | Write | 更新每笔注单的 `winlose`（赢/输）、`profitzcoin`（赢分） |
| Cache | Redis `predict:game:{id}:status` | Delete | 设定 `winresult` 或 `payout` 后立即失效，防止前台继续显示旧状态 |

---

## 6. 重要规则

- **权限限制**：仅結算相關服務或具有管理权限的账户（如 pricebackendservice 代理）可以调用此 API。
- **不可修改字段**：`betpool_bets.profitzcoin`、`betpool_bets.winlose` 仅可由結算程序回填，外部不可直接 UPDATE。
- **状态流转限制**：`status` 变更只能由「关闭」→「结算」，或「结算」→「已完成」，且须通过内部结算排程，不可由外部 API 一次性设至终态。
- **赢家计算规则**：如果 `betoption` 等于 `winresult`，则 `winlose = 'win'`，`profitzcoin = betzcoin + (betzcoin * feedrate)`，否则 `winlose = 'lose'`，`profitzcoin = 0`。
- **不可回传字段**：`betpool_bets.account` 在排行榜或公开 API 绝不可暴露。
- **TTL 规则**：`predict:game:{id}:status` 的 TTL 为 30 秒，但必须在更新 `winresult` 或 `payout` 时主动删除，不可只依赖 TTL 过期。
- **Transaction 规则**：写入 `betpool_games.winresult` 与 `status` 应为原子操作；若其中一项失败，必须回滚。
- **Retry 规则**：计算 `profitzcoin` 与调用 MemberService 派金属于关键路径，若失败需有重试机制，但须保证幂等性（同一笔注单不可重复加钱）。
- **状态值限制**：只有 `status = 1`（关闭）且 `payout = false` 的游戏才可接受 `winresult`。

---

## 7. 错误情境

| 情境 | 预期结果 |
|---|---|
| 游戏 ID 不存在 | 回传 404 Not Found |
| 游戏状态尚未关闭（`status = 0`） | 回传 400 Bad Request，提示赛事仍开放中 |
| 游戏已 `payout = true` | 回传 409 Conflict，提示结果已被设定 |
| 获胜选项不在 `betoptions` 映射中 | 回传 400 Bad Request，提示选项非法 |
| 无权限调用 API | 回传 403 Forbidden |
| Redis 写入或删除失败 | 不阻塞主流程，但需输出错误日志；快取将在 30 秒后自然过期 |
| DB 写入 `betpool_games` 超时 | 回传 503 Service Unavailable，原注单状态不变 |
| 计算赢家后，MemberService 扣款/加钱失败 | 保持 `payout = false`，回传 502 Bad Gateway，等待排程重试 |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预期结果 |
|---|---|---|---|
| BP-001 | API Test | 对一个已关闭的赛事发送有效获胜选项 | 回传 200，DB 中 `winresult` 被设定 |
| BP-002 | Integration Test | 在结果设定后立刻查询游戏详情 | `winresult` 字段有值，且 Redis 快取被清除 |
| BP-003 | Flow Test | 检查注单赢家资料正确性 | `betoption` 匹配 `winresult` 的注单 `winlose='win'`，其余为 'lose' |
| BP-004 | Permission Test | 使用无权限的 Token 调用 API | 回传 403 |
| BP-005 | Validation Test | 传入不存在的选项 | 回传 400 |
| BP-006 | Idempotency Test | 对同一个赛事发送两次结果更新 | 第一次成功，第二次回传 409 Conflict |

---

## 9. 高风险区域

- **betpool_games**：错误写入 `winresult` 将导致全服金流错误，且 `payout` 一旦为 `true` 不可逆。
- **Cache consistency**：更新 DB 后未即时删除 Redis 快取，将导致前台与实际状态不一致长达 30 秒，可能造成用户困惑。
- **Idempotency**：派彩写入 MemberService 必须保证幂等，否则同一赢家可能被重复加钱。
- **Cross-service coordination**：本服务写 `winlose` 与 `profitzcoin` 后，需依赖 MemberService 完成真实扣款。若 MemberService 断线，注单将永久停留在「已计算但未发款」状态。
- **Direct UPDATE prohibition**：`profitzcoin` 与 `winlose` 被外部服务或其他人误改是高危操作，必须在程序层面限制（仅允许内部结算服务写入）。

---

## 10. 常见错误

- ❌ 在外部 API 直接 UPDATE `betpool_games.winresult` 或 `status` → ✅ 必须通过 Service 层统一处理，以执行状态检查与快取失效。
- ❌ 忘记清除 `predict:game:{id}:status` → ✅ 更新结果或派彩后必须删除快取。
- ❌ 直接在 Controller 里写 SQL → ✅ 应通过 Provider / Repository 操作 DB。
- ❌ 将 `profitzcoin` 或 `winlose` 作为 API 参数开放 → ✅ 仅接受获胜选项，利润由系统计算。
- ❌ 公开 API 回传 `betpool_bets.account` → ✅ 排行榜或任何非本人查询必须脱敏。

---

## 11. Evidence

| 类型 | 来源 |
|---|---|
| API | `PUT /api/v1/betpool/games/{id}/result` |
| DB | `predict.betpool_games`、`predict.betpool_bets` |
| Redis | `predict:game:{id}:status` |
| 规则 | `predict-detail.md` 章节：写⼊限制、不可回传栏位、跨服务限制 |
| 规则 | `member-detail.md` 彩金派发由 TransactionService/WalletService 执行 |
| 测试 | 无独立测试脚本，但根据 OpenAPI 与 DB 写⼊限制设计测试重点 |