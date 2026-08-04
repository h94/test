# 修改问题类型

## 1. 场景目的

更新 MySQL 中的问题类型资料，同时同步更新 Redis 缓存，确保客服端即时取得最新问题类型配置。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| PUT | /api/v1/issuetype | 修改 DB 及 Redis 中的 IssueType |

---

## 3. 流程总览

1. 接收 PUT 请求，Body 为 IssueType JSON（包含 id、content 等栏位）。
2. 检查必须栏位（content 不可为空，否则直接回传 0 失败）。
3. 调用 MySQL 写入：
   - 根据 id 更新对应问题类型记录（例：UPDATE issue_type SET content = ..., enabled = ... WHERE id = ...）。
4. 若 MySQL 更新成功（影响行数 > 0），同布更新 Redis：
   - 推测更新某个 Hash 或 Set，确保透过 `cacheredis` API 读取到的资料是最新。
5. 回传 int32 结果（成功行数 / 0 代表失败）。

---

## 4. 程式流程

| 顺序 | Layer | Class / Method（推断） | 动作 |
|---|---|---|---|
| 1 | Controller | IssueTypeController.Put | 接收请求，呼叫 Service |
| 2 | Service | IssueTypeService.Update | 验证 content 不为空；若缺乏 content 则回传 0 |
| 3 | Provider (MySQL) | IssueTypeRepository.Update | 执行 UPDATE SQL，取得受影响行数 |
| 4 | Provider (Redis) | RedisProvider.UpdateIssueType | 将更新后的问题类型写入 Redis（可能为 HSET 或 SET） |
| 5 | Service | IssueTypeService.Update | 判断 MySQL 与 Redis 结果，回传成功与否 |

> 注：实际 Class 名称需人工确认。

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB | MySQL table（猜测：issue_type） | Update | 更新问题类型内容 / 状态 |
| Cache | Redis key（猜测：issue_type:<id> 或 issue_type:list） | Write | 更新缓存中的问题类型资料，供快速读取 |

> 需确认 MySQL 表名与 Redis Key 规则。

---

## 6. 重要规则

- **Content 必填**：OpenAPI 说明 “含content，若无content则失败-回传0” → 请求 Body 若未提供 content 或为空，必须直接回传 0，不执行 MySQL/Redis 操作。
- **同步写入**：MySQL 与 Redis 须在同一次请求中完成更新；若 MySQL 成功但 Redis 失败，可能导致资料不一致（需人工确认补偿策略）。
- **回传值**：成功时回传受影响的 MySQL 行数（通常为 1）；失败或未找到 id 时回传 0。
- **Idempotency**：相同请求重送应保持幂等（因基于 id 更新，自然幂等）。
- **禁止部分更新**：Request Body 中可能允许只更新部份栏位？依 OpenAPI summary 需包含 content，但其他栏位（如 enabled、lang 等）的更新规则需人工确认原始码。

---

## 7. 错误情境

| 情境 | 预期结果 |
|---|---|
| 请求 Body 缺少 content | 回传 int32 0，不写入任何资源 |
| MySQL 更新时找不到 id | 回传 0（影响行数 0），不写 Redis |
| MySQL 写入成功，但 Redis 写入失败 | 可能导致缓存不更新，需人工确认是否有重试或补偿 |
| Redis 连线超时或不可用 | 可能仍回传成功（仅 MySQL 成功）？需人工确认错误处理策略 |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预期结果 |
|---|---|---|---|
| UT-01 | API Test | 正常更新含 content 的请求 | HTTP 200，回传 1；MySQL 与 Redis 资料更新 |
| UT-02 | Validation | 请求不包含 content | 回传 0，资料未变动 |
| UT-03 | Permission Test | 无权限呼叫（若存在验证） | 需人工确认是否有权限控制 |
| UT-04 | Flow Test | MySQL 更新后立刻查询 `/api/v1/issuetype/cacheredis` | Redis 中资料应与 MySQL 一致 |
| UT-05 | Consistency Test | 在 Redis 写入时模拟失败 | 观察 API 回传值及系统行为（需人工确认设计） |

---

## 9. 高风险区域

- **一致性**：MySQL 与 Redis 的双写没有事务保障，容易出现 Redis 中资料过旧。
- **缓存键结构**：Redis Key 设计错误可能导致覆盖或读取错误。
- **并发更新**：同一 id 被同时修改可能后写覆盖前写，但业务上影响较小。
- **回退机制**：若 Redis 更新失败，是否要回滚 MySQL 需确认。

---

## 10. 常见错误

- ❌ 未检查 content 为空，导致写入空白资料。
- ❌ 只更新 MySQL，忘记更新 Redis，导致线上用户持续看到旧内容。
- ❌ 对 Redis 进行增量更新（如使用 HINCRBY）而非直接覆盖，导致资料异常。
- ❌ 回传值错误判断，例如将 0 当作成功。
- ❌ 未处理 id 不存在的情境，导致无故回传 1。

---

## 11. Evidence

| 类型 | 来源 |
|---|---|
| API 定义 | OpenAPI: `PUT /api/v1/issuetype` summary 与 request body 说明 |
| Content 必填规则 | OpenAPI summary: “含content，若无content则失败-回传0” |
| MySQL 与 Redis 双写 | README: “問題類型管理：支援新增、修改、刪除問題類型，資料同步寫入 MySQL 與 Redis” |
| 读取 Redis 的端点 | OpenAPI: `GET /api/v1/issuetype/cacheredis` 证实 Redis 缓存存在 |
| 删除行为仅修改 enabled | OpenAPI: `DELETE /api/v1/issuetype` summary: “修改DB中的IssueTypes:enabled=0” |

> 对于 MySQL 表结构、Redis Key 命名、Service/Repository 具体阶层，尚缺代码证据，**需人工确认**。