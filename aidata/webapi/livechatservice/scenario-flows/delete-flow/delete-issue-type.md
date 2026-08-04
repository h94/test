# 删除问题类型

## 1. 场景目的

将指定问题类型（Issue Type）标记为禁用状态（`enabled = 0`），实现软删除。该操作同时更新 MySQL 与 Redis，确保查询接口不再返回该问题类型。

---

## 2. 入口 API

| Method | Path | 说明 |
|--------|------|------|
| DELETE | `/api/v1/issuetype?issueId={id}` | 软删除指定问题类型 |

---

## 3. 流程總覽

1. 接收 DELETE 请求，携带 `issueId` 参数。
2. 校验 `issueId` 是否存在（可选，部分实现直接更新）。
3. 更新 MySQL 中问题类型表 `enabled` 字段为 0，条件 `id = issueId`。
4. 更新 Redis 缓存（可能是删除缓存键或更新列表）。
5. 返回受影响的记录数（通常为 1）。

*Redis 更新策略需人工确认：是删除整个列表缓存，还是标记特定 item 为失效。*

---

## 4. 程式流程

> **注意**：以下为推断流程，具体类名与方法名需人工确认。

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `IssueTypeController.DeleteIssueType` | 接收 `issueId` 并转发至 Service |
| 2 | Service | `IssueTypeService.DeleteIssueType` | 调用 Provider 执行 MySQL 更新，并通知 Redis 更新 |
| 3 | Provider | `MySqlProvider`（推测） | 执行 `UPDATE issue_types SET enabled = 0 WHERE id = @issueId` |
| 4 | Provider | `RedisProvider`（推测） | 删除或更新缓存键，使缓存失效 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | MySQL · `issue_types` 表（表名需确认） | Write（UPDATE） | 设置 `enabled = 0` |
| Cache | Redis | Write/Delete | 清除问题类型列表缓存或更新条目状态，保证读取接口一致 |
| Queue | Kafka | - | 未使用 |

---

## 6. 重要規則

- **软删除机制**：仅修改 `enabled` 状态，不物理删除记录，保留历史数据。
- **不可修改其他字段**：仅更新 `enabled`，不能变更 `id`、`content` 等。
- **缓存一致性**：更新 MySQL 后必须同步更新 Redis，否则查询接口可能返回已禁用类型。
- **幂等性**：重复调用同一 `issueId` 应返回成功，且 `enabled` 保持 0。
- **权限限制**：需人工确认是否需要权限控制（如后台管理员）。
- **错误处理**：若 Redis 更新失败，应考虑重试或标记日志，避免不一致。

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| `issueId` 不存在 | 返回失败（如影响行数为 0）或业务异常 |
| MySQL 更新失败（如连接超时） | 返回 500 错误，Redis 不更新 |
| Redis 更新失败 | 可能返回成功但记录日志，系统出现短暂不一致 |
| 并发删除同一问题类型 | 由于幂等性，均为成功 |
| `issueId` 参数缺失或非整数 | 返回参数校验错误 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| DT-1 | Integration Test | 正常删除已启用的问题类型 | `enabled` 变为 0，Redis 缓存失效 |
| DT-2 | API Test | 查询已删除类型（通过列表或详细接口） | 不再出现在启用列表中 |
| DT-3 | API Test | 重复删除同一 ID | 成功，状态保持 0 |
| DT-4 | API Test | 删除不存在的 ID | 返回适当错误码（如 404 或影响行数 0） |
| DT-5 | Flow Test | 删除后立即修改其他字段（如 content） | 修改操作应正常执行 |
| DT-6 | Cache Test | 删除后查询缓存接口 `/api/v1/issuetype/cacheredis` | 不应包含该条目 |

---

## 9. 高風險區域

- **缓存不一致**：MySQL 更新成功但 Redis 未更新，导致前端仍显示已删除问题类型。需确保缓存更新操作有重试或最终一致性机制。
- **无事务支持**：MySQL 与 Redis 为独立存储，无法使用分布式事务；需人工确认当前实现是否使用补偿逻辑。
- **外键关系**：若其他表（如聊天记录）引用问题类型 ID，软删除可能影响关联查询，需确认系统假设。
- **历史数据膨胀**：长期软删除会导致表变大，影响查询性能，需有定期清理机制。

---

## 10. 常見錯誤

- ❌ 误执行物理删除（`DELETE FROM`）导致历史数据丢失。
- ❌ 只更新 MySQL 而未处理 Redis 缓存，导致缓存脏读。
- ❌ 更新 `enabled` 时未添加 `WHERE id = @issueId` 条件，误更新全表。
- ❌ 忘记在查询接口过滤 `enabled = 0` 的条目，导致已删除类型仍出现。
- ❌ 未处理并发请求，可能出现状态被覆盖（本场景影响小，因为只设 0）。

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| API 定义 | `OpenAPI` 中 `DELETE /api/v1/issuetype` |
| 软删除说明 | API 摘要：“修改DB中的IssueTypes:enabled=0” |
| DB 类型 | `README`：“问题类型...资料同步写入 MySQL 与 Redis” |
| Redis 使用 | `README` 及 API `/api/v1/issuetype/cacheredis` 表明问题类型数据缓存于 Redis |
| 返回类型 | OpenAPI 响应 schema 为 `integer (int32)`，应为影响行数 |

---

> **需人工确认**：
> - MySQL 表实际名称及 Redis 键模式。
> - Service/Provider 具体类名与方法实现。
> - 缓存更新策略（全量重建、删除键、或单项标记）。
> - 是否存在分布式事务或重试逻辑。
> - 是否有权限校验（如管理员角色）。