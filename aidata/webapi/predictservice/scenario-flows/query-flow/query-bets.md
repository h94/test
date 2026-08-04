# 查询竞猜下注

## 1. 场景目的

提供前台用户查询个人在指定日期范围内、针对特定游戏类型、联赛与赛事的竞猜下注纪录。系统须确保查询结果仅包含请求者本人的下注资料，并遵守 Cassandra 查询限制。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| GET | `/api/v1/bets/{gameType}` | 查询特定游戏类型的下注记录。支援以 startDate, endDate, account, limit 作为查询参数。 |
| GET | `/api/v1/bets/{gameType}/{lid}` | 查询特定游戏类型、联赛下的下注记录。支援相同查询参数。 |
| GET | `/api/v1/bets/{gameType}/{lid}/{gDate}` | 查询特定游戏类型、联赛、指定日期的下注记录。 |
| GET | `/api/v1/bets/{gameType}/{lid}/{gDate}/{gid}` | 查询特定赛事的下注记录。 |

---

## 3. 流程总览

1. **认证与授权**：所有 `/api/v1/bets` 路由都标示为需要验证 (✅)。请求通过 `ECFramework.ECService` 统一验证框架解析出当前登录账号。
2. **请求参数验证**：Controller 层确保 `account` 参数与当前登录用户一致（若提供），或自动填入当前用户账号。验证 `startDate`、`endDate` 等日期格式。
3. **查询 Cassandra**：Service 层调用 Provider 进行数据库查询。不同路径对应不同的 Cassandra 分页键，资料源为 `predict` keyspace 中的 `predict_bets` 系列表。
   - 路由参数用于精确指定 Cassandra 分区键。
   - 查询参数作为查询条件，需注意 Cassandra `WHERE` 子句的限制。
4. **结果过滤与加工**：检查返回数据的完整性，确保不包含其他账号的资料。
5. **回传响应**：回传符合 `PredictBet` schema 的注单列表。

---

## 4. 程序流程

> 缺乏具体 Controller / Service 名称的 code evidence，流程为基于 API 定义与 DB schema 的推断。需人工确认具体类别名称。

| 顺 序 | Layer | 预估 Class / Method | 动作 |
|---|---|---|---|
| 1 | Controller | `BetController` | 接收 GET 请求，从路由与查询字串取得参数。从 `ECService` 上下文中取得当前使用者账号，并与 `account` 参数交叉验证。 |
| 2 | Service | `BetQueryService` | 处理业务逻辑：组合 Cassandra 分区键与查询条件，确保查询被限制在单一分割区。 |
| 3 | Provider | `BetDataProvider` | 执行对 `predict_bets` 表的 `SELECT` 操作。Cassandra 查询语句将包含分区键与聚类键的精确匹配或范围查询。 |
| 4 | Transfer | `BetDto` | 将 Cassandra 回传的物件映射为 API 响应结构 `PredictBet`，处理敏感栏位（如有）。 |

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `predict.predict_bets` | Read | 查询使用者下注记录。主键设计推测为 `(game_type, lid, g_date, gid, account, ...)` 或类似结构，以支援从 API 路径进行精确分页。 |
| DB (Cassandra) | `predict.predict_bets` | Read | 查询指定游戏类型、日期、联赛的下注记录。Cassandra 查询必须包含分区键。 |
| Redis | — | — | 查询流程中未发现 Redis 使用。此为单纯查询历史记录，非高频热点资料，无快取需求。|
| Queue | — | — | 无 Queue 参与。 |

---

## 6. 重要规则

- **权 限限制**：使用者只能查询本人的下注记录 (`betpool_bets.account` 过滤规则)。跨账号查询是被禁止的，需由 Controller 层强制检查。
- **资料库限制**：Cassandra 查询必须提供分区键。对于 `predict_bets` 表，其分区键设计决定了哪些查询是高效的。路由参数直接对应分区键，不可进行全表扫描。
- **不可暴露资料**：
  - 根据 `predict-detail.md`，类似 `betpool_bets.account` 不可在公众 API（如排行榜）回传。此处为查询本人记录，可以回传。
  - 须确保不回传其他使用者的任何栏位。
- **TTL 规则**：无特定 TTL 规则。
- **Transaction 规则**：无跨服务 Transaction。
- **状态值限制**：无特殊状态限制，但须注意 API 回传的 `PredictBet` schema 定义（`result` 等栏位含义）。
- **不可修改栏位**：历史注单为不可变 (immutable) 记录。此场景为纯查询，不涉及修改。

---

## 7. 错误情境

| 情 境 | 预 期结果 |
|---|---|
| 使用者未登入或 token 无效 | 回传 401 Unauthorized，由 `ECFramework.ECService` 统一拦截。 |
| 使用者尝试查询其他帐号的下注记录 | Controller 层拒绝请求，可回传 403 Forbidden 或仅回传空列表。 |
| 请求的 `gameType` 不存在 | 可能导致无效的 Cassandra 表查询，Service 层应检查有效游戏类型列表。 |
| Cassandra 查询逾时或找不到分区 | 回传 500 Internal Server Error 或空阵列 `[]`，取决于错误处理策略。 |
| 无效的日期格式 | Controller 层 Model Validation 失败，回传 400 Bad Request。 |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预 期结果 |
|---|---|---|---|
| `TEST-QUERY-01` | Permission Test | 以 User A 登入，调用 GET `/api/v1/bets/{gameType}?account=UserB` | 拒绝请求或回传空列表。 |
| `TEST-QUERY-02` | Flow Test | 以 User A 登入，调用 GET `/api/v1/bets/{gameType}?startDate=...&endDate=...` | 成功回传 User A 在日期范围内的所有该类型注单。 |
| `TEST-QUERY-03` | API Test | 提供不正确的日期格式 `startDate=01-15-2026` | 收到 400 Bad Request。|
| `TEST-QUERY-04` | API Test | 使用所有可选参数进行深度查询 | 验证 Cassandra 查询效率与结果正确性。 |
| `TEST-QUERY-05` | DB Test | 预先插入特定 `gameType, lid, gDate` 的资料 | `GET /api/v1/bets/{gameType}/{lid}/{gDate}` 回传正确注单。 |

---

## 9. 高风险区域

- **Cassandra 全表扫瞄**：API 路由要求提供完整的 `gameType`，且路径越具体，查询效率越高。高频调用最简路径 `GET /api/v1/bets/{gameType}` 需确认分区键设计是否能高效支援日期范围查询，避免效能问题。
- **资料外泄**：`account` 参数若未强制与登入者绑定，将成为严重漏洞。所有查询逻辑中，必须以 Controller 取得的用户身份为准，不可信任请求参数中的 `account`。
- **状态一致性**：无。

---

## 10. 常见错误

- ❌ **新人错误**：未验证请求者账号，直接使用 query string 中的 `account` 字段查询，导致任何用户可查看他人下注纪录。
- ❌ **AI 容易误解**：认为 `GET /api/v1/bets` 是查询所有记录的入口，而忽略 Cassandra 分区键的巨大影响。应优先使用更具体的路径，或由 Service 层在内部限制查询范围。
- ❌ **常见漏检查项目**：未对 `gameType` 进行白名单校验，可能导致针对不存在 Cassandra 表 (如 `predict_bets_unknown`) 的异常查询。
- ❌ **常见错误流程**：将查出的 `PredictBet` 物件直接序列化，没有排除或格式化内部栏位（如金额单位），导致前端显示错误。

---

## 11. Evidence

| 类型 | 来源 |
|---|---|
| API | OpenAPI Spec: GET `/api/v1/bets/{gameType}`; `/api/v1/bets/{gameType}/{lid}`... |
| 权限 | README.md: "/api/v1/bets 需要验证 (✅)" |
| DB 表 | README.md: `predict.predict_bets` (用途: 竞猜下注记录) |
| DB 规则 | predict-detail.md: "查寻个人投注记录时须依 account 过滤，不可跨帐号查询" |
| 依赖 | predict-detail.md: predictservice 对 member/pricecenter keyspace 为唯读，不负责金流。 |