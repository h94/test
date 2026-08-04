# 获取数据库中的问题类型（IssueType）

## 1. 场景目的

从 MySQL 数据库查询所有已启用的问题类型（IssueType），供客服聊天界面或其他功能模块直接使用，避免缓存穿透，绕过 Redis 直接从 DB 获取最新数据。

---

## 2. 入口 API

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/v1/issuetype/cachedb` | 取得 DB 中的所有 IssueTypes（仅包含启用状态） |

---

## 3. 流程总览

1. 客户端发出 HTTP GET 请求到 `/api/v1/issuetype/cachedb`。
2. API Controller 接收请求（**需人工确认**：是否存在前置权限验证）。
3. Controller 调用 Service 层的方法，该方法负责查询 MySQL。
4. Service 执行 SQL 查询 `issuetype` 表（**需人工确认**：表名），过滤条件 `enabled = 1`。
5. 将查询结果转换为 `IssueType` 模型列表。
6. 返回 HTTP 200 及 `IssueType[]` 的 JSON 数组。

---

## 4. 程式流程

| 顺 | Layer | Class / Method | 动作 |
|----|-------|----------------|------|
| 1 | Controller | 未知（需人工确认） | 接收 HTTP GET 请求 |
| 2 | Controller → Service | 未知（需人工确认） | 调用 Service 中对应方法 |
| 3 | Service | 未知（需人工确认） | 执行 MySQL 查询 `SELECT * FROM issuetype WHERE enabled = 1`（**推测**） |
| 4 | Service → Controller | - | 返回 `IssueType` 集合 |
| 5 | Controller | - | 序列化为 JSON 并返回 200 |

**注**：由于缺少代码证据，上述层/类/方法名均为推测，具体名称请查阅 `LiveChatService.DomainService/LiveChatService.cs` 与对应 Controller 代码。

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|------|------|------|------|
| DB | MySQL `issuetype` 表（需人工确认表名） | Read | 获取所有 `enabled = 1` 的问题类型记录 |
| Redis | 无 | 无 | 本 API 路径特意标明 `cachedb`，绕过 Redis 缓存，直接读 DB |
| Kafka/Queue | 无 | 无 | 此流程不涉及队列 |

---

## 6. 重要规则

- **enabled 过滤**：`DELETE /api/v1/issuetype` 操作会将 `enabled` 设为 0（软删除），因此查询时必须加上 `WHERE enabled = 1`，确保不返回已禁用的问题类型。
  - Evidence：OpenAPI 中 DELETE 端点摘要：“修改DB中的IssueTypes:enabled=0”。
- **只读操作**：本接口为安全的 GET 请求，不应产生任何写操作或副作用。
- **不可暴露字段**：需确认表中是否存在后台管理专用字段（如 `createdby` 等），查询时需限制返回列（**需人工确认**）。
- **无缓存**：本接口专用于跳过 Redis 直接读取 MySQL，不应主动写入或读取 Redis。
- **数据同步责任**：根据 README，问题类型的增删改会同步写入 MySQL 与 Redis，本接口仅负责读取 MySQL 的原始数据。

---

## 7. 错误情境

| 情境 | 预想结果 |
|------|----------|
| MySQL 连接失败或超时 | 返回 HTTP 500，可能包括错误信息 |
| 表 `issuetype` 不存在 | 返回 HTTP 500，提示数据库错误 |
| 查询超时（大量数据） | 返回 HTTP 500 或 408 |
| 所有 `enabled` 均为 0 | 返回空数组 `[]`，状态码 200 |

**需人工确认**：错误响应体格式、中间件是否统一包装异常。

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预想结果 |
|---------|------|------|----------|
| QET-01 | API Test | 调用 `GET /api/v1/issuetype/cachedb`，库中有多条 enabled=1 的记录 | 返回 200，列表包含所有启用的问题类型 |
| QET-02 | Integration Test | 库中存在 enabled=0 的记录 | 返回的列表中**不**包含这些禁用记录 |
| QET-03 | API Test | 库中没有任何记录 | 返回 200，空数组 |
| QET-04 | Integration Test | MySQL 服务不可用 | 返回 500，不应导致 crash |
| QET-05 | Permission Test | 是否需要认证（**需人工确认**） | 按实际权限配置验证 |
| QET-06 | Flow Test | 调用该接口后，再通过增删改接口修改数据，并检查 Redis 缓存是否受影响 | 确认本接口仅读 DB，不会污染或清除 Redis 缓存 |

---

## 9. 高风险区域

- **高负载直接读 MySQL**：该接口标记为 `cachedb`，意味着调用者（通常是前端或其他服务）可能期望跳过缓存直接获取最新数据。若调用频繁，可能对 MySQL 造成压力。建议评估是否需要限流。
- **字段变更风险**：表 `issuetype` 的结构若发生变化（增加/删除字段），需同步更新返回的 `IssueType` 模型，避免序列化错误或遗失数据。
- **并发软删除冲突**：当其他请求正在将某个问题类型设为 `enabled=0` 时，本查询可能出现瞬间读到旧值的情况，由于读操作不锁表，对业务影响较小（最终一致性可接受）。
- **缺少认证/授权**（需人工确认）：如果该接口开放给公网，且 IssueType 数据属于敏感配置，存在未授权访问风险。

---

## 10. 常见错误

- ❌ 忘记过滤 `enabled = 1`，误将已删除（禁用）的问题类型返回给前端。
- ❌ 误解接口前缀 `cachedb`，以为会读取 Redis 缓存；实际该接口直接访问 MySQL。
- ❌ 在代码中意外写入或删除 Redis 缓存数据，破坏缓存一致性。
- ❌ 没有对 MySQL 查询进行超时控制，导致请求阻塞。
- ❌ 返回的模型中包含不应该暴露的管理字段（如内部备注）。

---

## 11. Evidence

| 类型 | 来源 |
|------|------|
| API | OpenAPI 描述：`GET /api/v1/issuetype/cachedb` 摘要 “取得DB中的IssueTypes” |
| DB | README 提及：“问题类型（Issue Type）管理：支援新增、修改、删除问题类型，资料同步写入 MySQL 与 Redis” |
| DB `enabled` | OpenAPI `DELETE /api/v1/issuetype` 摘要 “修改DB中的IssueTypes:enabled=0” → 证实存在 enabled 字段，0 为禁用 |
| 代码 | 无具体代码证据，需人工确认 Controller / Service 位置 |
| Redis 无使用 | README 描述 IssueType 仅提到 MySQL 与 Redis，但 `cachedb` 路径暗示绕过缓存 |

---

**建议补充信息**：
- `issuetype` 表的完整 schema（列定义）以及对应的 MySQL 连接字符串所在配置文件。
- 具体 Controller 与 Service 的方法签名，以明确参数验证、异常处理逻辑。
- 接口是否需携带 token 或特定的 header 进行认证。