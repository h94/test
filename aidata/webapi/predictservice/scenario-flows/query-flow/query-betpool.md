# 查询奖池赛事及下注

## 1. 场景目的

前台用户查询可投注的开放奖池赛事列表，或查询特定奖池赛事详情，以及查询个人在某一奖池赛事中的历史下注记录。此流程纯为数据查询，不涉及下注或金流操作。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| GET | `/api/v1/betpool/games` | 查询奖池赛事列表 |
| GET | `/api/v1/betpool/games/{id}` | 查询单一个奖池赛事详情 |
| GET | `/api/v1/betpool/games/{id}/bets` | 查询特定奖池赛事的（所有）下注记录 |
| GET | `/api/v1/betpool/games/accounts/{account}/bets` | 查询特定帐号在特定奖池赛事中的下注记录 |

---

## 3. 流程总览（以用户查询自身下注为例）

1. 接收带有 `account` 路径参数的 GET request。
2. 验证用户身份（需登入）。
3. 依登入的站台（site），从 `pricecenter` 确认帐号 `enabled = 1` 且未被关闭。
4. 从 `member` 确认用户 `status = 1`（活耀）。
5. 依赛局 ID (`gid`) 与帐号 (`account`) 查询 `predict.betpool_bets`。
6. 依赛局 ID 查询 `predict.betpool_games` 取得赛事详细资讯。
7. 组合并回传查询结果。

---

## 4. 程式流程

| 顺续 | Layer | Class / Method | 动作 |
|---|---|---|---|
| 1 | Middleware | `AuthFilter` | 验证请求的 JWT Token 是否正确及有效。 |
| 2 | Middleware | `AuthFilter` | 解析 Token，取得登入的 `account` 与 `site`。 |
| 3 | Controller | `BetPoolController` | 接收请求，验证路径参数 `account` 与登入者是否为同一人。 |
| 4 | Service | `BetPoolService` | 被 Controller 呼叫，负责主要商业逻辑。 |
| 5 | Provider | `BetPoolProvider` | 执行 Cassandra 的資料庫查询。 |
| 6 | Provider | `MemberProvider` | 查询 `member.gameusers`，查验帐号状态。 |
| 7 | Provider | `PriceCenterProvider` | 查询 `pricecenter.accounts_{site}`，再次确认帐号有效性。 |

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB | `member.gameusers` | Read | 透过 `authkey` 查询使用者基本资料与状态 (`status = 1`)。 |
| DB | `pricecenter.accounts_{site}` | Read | 透过 `account` 主键查询帐号是否启用 (`enabled = 1`) 且未关闭 (`closetime` 为空)。 |
| DB | `predict.betpool_bets` | Read | 透过 `gid` (分区键) 与 `account` (聚类键) 查询下注纪录。 |
| DB | `predict.betpool_games` | Read | 透过赛事 `id` 主键查询奖池赛事的设定与状态。 |

---

## 6. 重要规则

- **权限限制**：
  - 所有端点皆需验证。
  - 查询自身下注纪录时，路径中 `{account}` 必须与登入帐号一致。
- **查询规则**：
  - **betpool_games 查询**：开放投注列表查询须过滤 `starttime <= CURRENT TIME < endtime` 且 `status = 0`。
  - **历史纪录查询**：排行榜或已结束赛事须过滤 `payout = true` 且 `status = 1`。
  - **betpool_bets 查询**：查询个人投注记录时须依 `account` 过滤，不可跨帐号查询。
- **不可暴露资料**：
  - **betpool_bets.account**：非本人查询下注记录时，须遮蔽此栏位。
  - **betpool_bets.id**：对外回传时可考虑遮蔽，避免泄露投注单流水号。
  - **betpool_games.betoptions**：内部选项映射不应回传给前端，仅用作后端计算。
  - **member.gameusers** 的 `password`, `email`, `authkey` 绝不可回传。
  - **pricecenter.accounts_{site}** 的 `password`, `phone` 绝不可回传。

---

## 7. 错误情境

| 情境 | 预期结果 |
|---|---|
| 账务不存在或未启用 | 回传帐务错误，拒绝查询。 |
| `account` 参数与 Token 身份不符 | 回传 HTTP 403 Forbidden。 |
| 查询 `betpool_bets` 时未提供分页键 `gid` | **需人工确认**。依 Cassandra 规则，全表扫描会被拒绝或效能极差，应强制要求 `gid` 参数。 |
| 赛事 `id` 不存在 | 回传空列表或HTTP 404。 |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预期结果 |
|---|---|---|---|
| BPL-01 | API Test | 无 Token 呼叫 API。 | HTTP 401 Unauthorized。 |
| BPL-02 | Permission Test | A 帐号查询 B 帐号的投注纪录。 | HTTP 403 Forbidden。 |
| BPL-03 | Flow Test | 查询一个存在的 `gid`，且本人有下注纪录。 | 成功回传包含 `betoption`, `betzcoin` 等详细资讯。 |
| BPL-04 | Flow Test | 查询一个存在的 `gid`，但本人无下注纪录。 | 成功回传空列表 `[]`。 |
| BPL-05 | Flow Test | 查询赛事列表，应有多个包含 `hot`, `viponly`, `status` 字段的赛事。 | 成功回传，且赛事应仍处于开放时间范围内。 |
| BPL-06 | Status Test | 查詢 `status=1` 已完成赛事的下注。 | 成功回传，且应有 `winlose`, `profitzcoin` 等结果。 |

---

## 9. 高风险区域

- **查询效能**：
  - 查询 `predict.betpool_bets` 时若未指定 `gid`，将导致 Cassandra 全表扫描，有严重的效能风险。
- **资料一致性**：
  - 赛事时间与状态的比较依赖服务端时间与资料库时间的同步。若 `endtime` 已过但仍显示为开放，将造成错误。

---

## 10. 常见错误

- ❌ **查询 `betpool_bets` 时未指定 `gid` 条件**：Cassandra 查询必须包含全部分区键，否则会出错或扫全表。
- ❌ **直接回传完整 `GameUser` 或 `accounts_*` 物件**：必须移除 `password`, `email`, `authkey`, `phone` 等所有敏感栏位。
- ❌ **将 `betpool_games.betoptions` 的原始 map 回传给前端**：此栏位为内部使用，对前端无意义，应只回传选项目的清列表。
- ❌ **未过滤 `status` 即回传**：已结案或取消的竞猜赛事不应出现在投注列表中，导致前台显示错误。

---

## 11. Evidence

| 类型 | 来源 |
|---|---|
| API | `BetPoolController` (推测，基于 `README.md`) |
| DB | `predict.betpool_bets`, `predict.betpool_games` |
| Rule | `predictservice-detail.md` - betpool_games 查询规则 / betpool_bets 查询规则 |
| Rule | `predictservice-detail.md` - 不可回传栏位 |
| Rule | `predict-detail.md` - status / payout 规则 |