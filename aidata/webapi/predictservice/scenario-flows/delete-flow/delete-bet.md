# 删除竞猜下注

## 1. 场景目的

管理员或系统取消特定赛事下注，常用于赛事异常取消或需撤销投注时。

---

## 2. 入口 API

| Method | Path | 说明 |
|--------|------|------|
| DELETE | `/api/v1/bets/{gameType}/{lid}/{gDate}/{gid}` | 删除指定赛事下注 |

---

## 3. 流程总览

1. 接收 DELETE 请求，获取路径参数 `gameType`、`lid`、`gDate`、`gid`
2. 通过 ECFramework.ECService 验证调用者身份（管理员或内部服务，如 pricebackendservice）
3. 根据 `gameType` 确定实际下注表名（`predictbets_{gameType}`）
4. 执行删除操作（需人工确认：DB 文档禁止 DELETE/UPDATE，实际可能是软删除 `enabled=0`）
5. 若涉及已扣点数，需通知 `memberservice` 或金流服务退还金额（与 predictservice 无直接金流能力）
6. 清除相关缓存（如 `predict:bets:{gid}`）
7. 返回操作结果

---

## 4. 程式流程（推测，无实际代码证据）

| 顺序 | Layer | Class / Method | 动作 |
|------|-------|----------------|------|
| 1 | Controller | `BetController.Delete` | 接收参数，调用 Service |
| 2 | Service | `BetService.DeleteBet` | 权限校验，调用 Provider 执行删除 |
| 3 | Provider | `PredictBetProvider.Delete` | 操作 Cassandra（DELETE 或 UPDATE enabled=0） |
| - | - | 通知外部 | 若需退款，异步发送消息或调用 `memberservice` |

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|------|------|------|------|
| DB | `predictbets_{gameType}` | Delete 或 Update enabled=0 | 取消下注记录 |
| Redis | `predict:bets:{gid}` | DEL | 清除投注缓存，确保实时性 |
| 外部服务 | `memberservice` (可能) | 通知退款 | predictservice 不负责金流，需调用成员服务 |

**⚠️ 重要冲突**：`predict-detail.md` 明确声明 `predictbets_*` 系列表“仅可 INSERT（append-only），不可 UPDATE 或 DELETE”。此 API 的实际实现需人工确认是硬删除还是软删除，或是否依赖其他机制（如 TTL tombstone）。

---

## 6. 重要规则

- **权限限制**：仅管理员或内部服务（如 `pricebackendservice`）可调用
- **结算状态检查**：已结算（`status=2`）或已派彩的下注不可删除
- **不可回退金流**：predictservice 不直接处理退款，需协调 `TransactionService` 或 `MemberService` 完成
- **不可修改已结算记录**：一旦 `winlose` 非空，禁止任何变更
- **缓存一致性**：删除下注后须主动失效 Redis 缓存，避免前端展示错误

---

## 7. 错误情境

| 情境 | 预期结果 |
|------|----------|
| 下注记录不存在 | 返回 404 |
| 下注已结算（status=2 或 winlose 已填写） | 返回操作失败，提示不可删除 |
| 权限不足（普通用户） | 返回 403 |
| 传递无效的 `gameType`（表不存在） | 返回 400 |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预期结果 |
|---------|------|------|----------|
| DEL-BET-01 | API Test | 管理员删除未结算下注 | 成功，查询不到该注 |
| DEL-BET-02 | Permission Test | 普通用户调用 | 403 Forbidden |
| DEL-BET-03 | Flow Test | 删除已结算下注 | 返回业务错误，记录未被改动 |
| DEL-BET-04 | Consistency Test | 删除后查询缓存 | 旧缓存失效，返回空 |

---

## 9. 高风险区域

- **DB 设计冲突**：数据库文档禁止 DELETE/UPDATE 于 `predictbets_*`，需确认代码实际是否通过硬删除或 `enabled=0` 软删除实现，或者是否绕过限制
- **金流一致性**：若下注已扣款，删除后未退款会造成用户资产损失；需确认退款流程是否在 API 内同步完成或通过消息队列异步保证
- **结算排程竞态**：删除时若结算排程正在执行，可能导致下注被误结算，需引入锁或条件删除（如 `IF status=0`）
- **幂等性**：重复调用 DELETE 应安全，不会重复退款

---

## 10. 常见错误

- ✅ 新人误以为可以直接 DELETE 物理删除，忽略 DB 分层限制
- ✅ 忘记检查下注是否为“未结算”状态，允许删除已派奖记录
- ✅ 删除后未通知金流服务退款，导致金钱错乱
- ✅ 未清理 Redis 缓存，前端仍展示旧数据

---

## 11. Evidence

| 类型 | 来源 |
|------|------|
| API | README.md: DELETE `/api/v1/bets/{gameType}/{lid}/{gDate}/{gid}` |
| DB 表 | predict DB detail: `predictbets_{gameType}` 系列表 |
| DB 限制 | predict-detail.md: “predictbets_* 系列表僅可 INSERT（append-only），不可 UPDATE 或 DELETE” |
| 权限要求 | README: API 标记为需要验证 ✅ |
| 不负责金流 | predictservice-detail.md: 本服务不负责彩金派发 |

---

**⚠️ 需人工确认**：
- 实际删除操作是硬删除（Cassandra DELETE）还是软删除（`enabled=0`）？
- 退款流程是同步调用还是异步消息？
- 是否对已结算下注做了强校验？