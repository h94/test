# 查询Killer帐号

## 1. 场景目的

根据指定的游戏类型(`gameType`)、联赛(`lid`)与周期(`cid`)，查询该范围内的 Killer（杀手）帐号列表，用于前台展示、后台管理或结算流程。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| GET | `/api/v1/killers/{gameType}/{lid}/{cid}` | 查询指定游戏、联赛、周期的 Killer 帐号列表 |
| GET | `/api/v1/killers/{gameType}/{lid}` | 查询指定游戏、联赛的所有周期 Killer 帐号 |
| GET | `/api/v1/killers/{account}` | 查询特定帐号的 Killer 记录 |

> **主要分析目标**：`GET /api/v1/killers/{gameType}/{lid}/{cid}`

---

## 3. 流程總覽

1.  `predictservice` 接收 GET 请求，路径参数包含 `gameType`、`lid`、`cid`。
2.  通过 ECFramework 验证用户身份与权限。
3.  Controller 调用 Service 层，Service 层调用 Provider 层。
4.  Provider 层查询 Cassandra 的 `predict.killer_accounts` 表（或 `predict.killeraccounts_{gameType}` 表）。
5.  根据 `lid` 和 `cid` 过滤出 Killer 帐号列表。
6.  对敏感资料进行脱敏处理。
7.  回传结果。

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Middleware | ECFramework | 验证请求的合法性，解密 JWT token，提取用户身份与权限。 |
| 2 | Controller | `KillerController` | 接收请求，解析 `gameType`, `lid`, `cid` 参数。需人工确认具体 Controller 名称 |
| 3 | Service | `KillerService` | 处理业务逻辑：参数校验、权限验证、调用 Provider。需人工确认具体 Service 名称 |
| 4 | Provider | `KillerProvider` | 封装 Cassandra 查询逻辑。依 `lid`, `cid` 查询 `killer_accounts` 或 `killeraccounts_{gameType}` 表。需人工确认具体 Provider 名称及确切的 Table Name |
| 5 | Service | `KillerService` | 接收 Provider 回传的资料，進行資料脫敏（如遮蔽帳號部分字元），並按規則排序（例如依 `profitpoint` 降冪）。需人工確認排序規則 |
| 6 | Controller | `KillerController` | 将结果封装为 HTTP 200 响应回传。 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `predict.killer_accounts` 或動態表名 `predict.killeraccounts_{gameType}` | Read | 根据 `lid`, `cid` (复合主键的一部分) 查询 Killer 帐号列表。 |
| Cache (Redis) | 无直接证据表明此流程使用 Redis 缓存。 | 需人工确认 | 需人工确认是否有缓存加速，若没有，高并发查询可能对 DB 造成压力 |

---

## 6. 重要規則

*   **權限限制**：所有 Killer API 都需要驗證（根据 README），意味着只有登入用户可查询。是否需要特定角色(如管理员)需人工确认。
*   **查詢過濾**：必须提供 `lid` 和 `cid` 作为查询条件。根据 `predictservice-detail.md`，不加这些条件会导致跨周期/跨联盟的全表扫描，是常见错误。
*   **不可暴露資料**：回传的帐号列表，若包含 `account` 等敏感字段，对外 API 可能需要脱敏（例如 `account` 显示为 `user***`），尤其是非本人查询的情境。 `predictservice-detail.md` 强调了公开 API 不可暴露会员隐私。
*   **排序規則**：根据 `predictservice-detail.md` 中关于 `killeraccounts_{gameType}` 的读取规则，列表应按照 `profitpoint` 排序。需人工确认是升序还是降序，以及是否有其他排序字段。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| 请求中缺少 `gameType`, `lid`, 或 `cid` 参数 | API 返回 400 Bad Request。 |
| 未登入或 token 无效/过期 | ECFramework 拦截并返回 401 Unauthorized。 |
| 提供的 `gameType` / `lid` / `cid` 组合在 DB 中不存在 | API 返回 200 OK，body 为空列表 `[]`。 |
| 查询时未指定 `lid` 和 `cid`，导致全表扫描 | 查询性能极差，可能触发 DB 保护机制或超时，最终返回 500 Internal Server Error。 |
| Cassandra 查询超时或失败 | API 返回 500 Internal Server Error。 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| `FT-KLR-01` | Flow Test | 提供有效的 `gameType`, `lid`, `cid`，且该周期存在 Killer | 返回 200 OK，body 内为非空的 Killer 帐号列表，资料结构正确且已脱敏。 |
| `FT-KLR-02` | Flow Test | 提供有效的参数，但该周期不存在 Killer | 返回 200 OK，body 内为空列表 `[]`。 |
| `PT-KLR-01` | Permission Test | 未登入状态直接呼叫 API | 返回 401 Unauthorized。 |
| `IT-KLR-01` | Integration Test | 验证列表顺序是否符合业务规则 (如 `profitpoint` 降序) | 列表正确排序。 |
| `IT-KLR-02` | Integration Test | 验证回传资料是否包含不该暴露的栏位 (如完整 `account`) | 回传资料不包含敏感信息或已被脱敏。 |

---

## 9. 高風險區域

*   **高風險 Table**：`predict.killer_accounts` (或 `predict.killeraccounts_*`)
    *   **原因**：此表为主键查询，若程式码错误导致不带 `lid` 和 `cid` 的查询，会引发全表扫描，严重影响 Cassandra 集群效能。
*   **資料脫敏**：Killer 列表属公开排行榜性质，回传时必须确保帐号等个人隐私资讯不会外泄。若此处逻辑缺失，属高风险的隐私泄露事件。

---

## 10. 常見錯誤

*   ❌ **查詢時未帶 `lid`、`cid` 條件**：如 `predictservice-detail.md` 所述，`killeraccounts_{gameType}` 的查询必须加上 `lid` 和 `cid`。忘记添加会触发跨分区的范围查询，这是 Cassandra 的反模式，会导致严重效能问题。
*   ❌ **直接回傳 DB 原始資料**：忘记对回传的 `account` 等敏感栏位进行脱敏处理，直接将整个 Row 回传，造成个资外泄。
*   ❌ **AI 誤解**：AI 可能假设所有 `predict`Keyspace 下的表都遵循相同的快取策略。本场景的证据中未发现快取使用，AI 不应自行推断使用 Redis 快取。

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | `README.md` Killer 机制路由 `GET /api/v1/killers/{gameType}/{lid}/{cid}` |
| DB | `README.md` 資料庫重要 Table：`predict.killer_accounts` |
| DB 規則 | `predictservice-detail.md` `killeraccounts_{gameType} 查詢` 规则与常见错误。 |
| 權限 | `README.md` 對外 API 重點中，该路由 `需要驗證` 标记为 ✅。 |