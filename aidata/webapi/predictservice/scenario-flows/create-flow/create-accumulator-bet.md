# 建立串关下注

## 1. 场景目的
用户选择一个或多个赛事，合并为一张串关（过关）注单。系统验证所有赛事及用户的合法性后，一次性写入注单记录。此流程不涉及开奖与派彩，仅为注单创建。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| POST | `/api/v1/bets/accumulator` | 建立串关下注 |

---

## 3. 流程总览
1. 接收前端传入的串关注单请求（包含多个赛事的投注项）。
2. 通过验证框架（ECFramework.ECService）校验用户身份。
3. 调用 MemberService 验证账号状态（是否启用、是否被封禁）。
4. 检查用户 VIP 状态与游戏设定（如 `viponly`）的匹配性。
5. 验证所有投注选项的合法性（赛事存在、玩法开放、赔率有效）。
6. 计算所需总金额，调用 MemberService 进行扣款/冻结资金。
7. 将注单写入 Cassandra `predict` keyspace。
8. 返回下注成功结果。

---

## 4. 程式流程

| 顺序 | Layer | Class / Method | 动作 |
|---|---|---|---|
| 1 | Controller | `BetController.PostAccumulator` | 接收 `PredictBet` 请求体，委托给 Service。 |
| 2 | Service | `AccumulatorService.Create` | 协调验证、扣款、持久化流程。 |
| 3 | Provider | `MemberProvider` | 调用 `memberservice` 验证用户状态与余额。 |
| 4 | Provider | `PredictProvider` | 查询 `predict_settings` 验证玩法与赛事。 |
| 5 | Provider | `PredictProvider` | 写入 `predict_bets` 注单数据。 |

**注**：具体类名与方法名需人工确认。

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read | 校验账户 `status=1`，确认未被停用/冻结。 |
| DB | `member.gamesublogs` | Read | 验证 VIP 订阅有效期 (`subendtime`)。 |
| DB | `predict.predict_settings` | Read | 验证 `game_type` 与 `play_modes` 是否开放。 |
| DB | `predict.predict_bets` | Write | 持久化下注记录 (`game_type`, `lid`, `g_date`, `gid`, `account`, `amount`) |
| Redis | `GameUser:{authkey}` | Read | 获取高频用户资料快取，加速身份/状态验证。 |
| Redis | - | Delete | 无需主动删除。 |

---

## 6. 重要规则
- **權限限制**：必须认证用户；`predictservice` 仅读 `member` keyspace，无权修改用户余额（扣款由 MemberService 完成）。
- **不可暴露資料**：API 回传不可包含 `member.gameusers.password`、`authkey`、`email`。
- **狀態值限制**：用户状态必须为 `status=1`；`gameusers_banned` 中不可存在有效封禁记录。
- **欄位限制**：`predict.predict_bets` 的 `amount` 与 `result` 字段，一旦写入不可修改。
- **權責分離**：实际金流（扣款/加款）由 `TransactionService` 或 `WalletService` 负责，`predictservice` 仅做记录。

---

## 7. 错误情境

| 情境 | 预期结果 |
|---|---|
| 用户未认证或 token 无效 | 返回 401 Unauthorized |
| 账户 `status != 1` (停用/冻结) | 返回 403 Forbidden 或业务错误码 |
| 账户存在于 `gameusers_banned` 且封禁未到期 | 返回 403 Forbidden |
| 赛事 ID 不存在或已关闭 (`status != 0`) | 返回 400 Bad Request，提示赛事无效 |
| 投注选项非法（例如不属于该赛事） | 返回 400 Bad Request，提示选项错误 |
| 用户余额不足 | 调用 MemberService 返回扣款失败，返回 402 Payment Required |
| DB (Cassandra) 写入超时或失败 | 返回 500 Internal Server Error，并记录错误日誌至 Kafka `applogs` |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预期结果 |
|---|---|---|---|
| ACC-01 | API Test | 发送正常多场赛事串关请求 | HTTP 200，DB 出现对应 `predict_bets` 记录 |
| ACC-02 | Permission Test | 使用已停用账号 (`status=0`) 请求 | HTTP 4xx，拒绝下注 |
| ACC-03 | Flow Test | 请求包含一场已关闭的赛事 | HTTP 400，提示指定赛事无法下注 |
| ACC-04 | Integration Test | 模拟 MemberService 扣款失败 | HTTP 5xx 或特定业务错误码，DB 无新记录 |
| ACC-05 | Flow Test | 下注包含 VIP 专享赛事，但用户非 VIP | HTTP 403，提示权限不足 |

---

## 9. 高風險區域
- **金流一致性**：`predictservice` 写入注单成功，但 `memberservice` 扣款失败（或反之），会导致数据不一致。需确保流程有回滚机制或依赖分布式事务/补偿。
- **高風險 Table**：`predict.predict_bets`。直接记录玩家投注金，任何错误写入都可能导致金流纠纷。
- **跨服務資料同步**：用户封禁状态变更时，Redis 快取 (`GameUser:{authkey}`) 的 TTL 延迟可能导致已封禁用户短暂仍可下注。**建议 TTL 设置不超过 5-10 分钟**。
- **Idempotency**：串关下注请求若因网络问题重复发送，可能导致重复扣款。**需人工确认** API 是否具备幂等性设计（如请求携带唯一 `id` 并在写入前校验）。

---

## 10. 常见错误
- **新人错误**：直接操作 `member` keyspace 的 GameUser 表进行扣款或状态变更。`predictservice` 对 `member` 只有读权限，必须通过 `memberservice` API 执行。
- **AI 误判**：假设 `predict_bets` 表的主键是单纯的 `account`。查询时务必带上 `game_type`, `lid`, `g_date` 等分区键，避免全表扫描。
- **遗漏检查**：只检查 `member.gameusers.status`，而忘记检查 `member.gameusers_banned` 表中的有效封禁记录。
- **错误流程**：在前端传入的参数中直接信任 `amount` 字段而不做服务端校验，或未进行服务端总金额重算，导致金额被篡改。

---

## 11. Evidence
| 类型 | 来源 |
|---|---|
| API | `BetController` (基于 README 路由 `POST /api/v1/bets/accumulator` 推断) |
| DB | `member.gameusers` (status), `member.gameusers_banned` (封禁检查), `predict.predict_bets` (写入) |
| DB 规则 | `predict-detail.md`, `member-detail.md` |
| Code | AccumulatorService.Create, MemberProvider, PredictProvider (**需人工确认具体实现**) |
| Redis | `predictservice-detail.md` - `GameUser:{authkey}` 快取 |
| 權責 | `predictservice-detail.md` - 本服务不负责章节 |
| 测试 | OpenAPI 定义 `PredictBet` schema (**需人工确认完整字段**) |