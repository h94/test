# 建立竞猜设定

## 1. 场景目的

为指定的游戏类型建立竞猜整体设定。此设定决定该游戏类型的核心玩法模式（play_modes）以及是否启用Killer淘汰机制，是后续所有竞猜投注和Killer周期结算功能的前置配置。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| POST | `/api/v1/settings/predict/{gameType}` | 建立指定游戏类型的竞猜设定 |

---

## 3. 流程总览

1. 接收管理员通过`pricebackendservice`代理的后台建置请求。
2. 获取路径参数`gameType`（游戏类型代码）。
3. 验证请求者权限（需人工确认具体验证逻辑）。
4. 组装竞猜设定实体，包含`play_modes`（玩法列表）和`killer_enabled`（Killer开关）。
5. **写入 Cassandra** `predict.predict_settings` 表，以`game_type`作为主键。
6. 返回写入成功的设定内容。

---

## 4. 程式流程

| 顺序 | Layer | Class / Method | 动作 |
|---|---|---|---|
| 1 | Controller | `SettingsController.CreatePredictSettings(gameType, request)` | 接收请求，调用Service层 |
| 2 | Service | `PredictSettingService.CreateSetting(gameType, request)` | 验证请求，组装实体 |
| 3 | DataProvider<br/>(需人工确认) | `PredictSettingProvider.InsertOrUpdate(entity)` | 写入Cassandra |

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB (Cassandra) | `predict.predict_settings` | Write (INSERT) | 写入`game_type`、`play_modes`、`killer_enabled`等核心设定 |
| DB (Cassandra) | `predict.predict_settings` | Read (SELECT) | 检查当前`game_type`是否已有设定（需人工确认） |

---

## 6. 重要规则

- **负责人**：仅限管理员或后端服务调用，需验证管理员权限（需人工确认权限模型）。
- **幂等性**：由于`game_type`是主键，重复请求可能覆盖原设定。需确认是否有防重复机制。
- **服务职责**：本服务为`predict` Keyspace的Owner，负责对该表直接读写，并非通过其他服务代理。

---

## 7. 错误情境

| 情境 | 预期结果 |
|---|---|
| 缺少`gameType`路径参数 | 返回 `400 Bad Request` |
| 请求体格式错误 | 返回 `400 Bad Request`，验证器拦截 |
| 数据库写入失败 | 返回 `500 Internal Server Error` |
| 无管理权限 | 返回 `401 Unauthorized` 或 `403 Forbidden` |
| 同一`gameType`重复建立 | **需人工确认**：是直接覆盖，还是返回错误提示设定已存在？ |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预期结果 |
|---|---|---|---|
| TC01 | API Test | 正常发送带`play_modes`和`killer_enabled`的请求 | 返回 `200`，DB出现对应记录 |
| TC02 | Permission Test | 未授权角色调用API | 返回 `401`/`403` |
| TC03 | Flow Test | 缺少必填字段 | 返回 `400` 及错误信息 |
| TC04 | Flow Test | 写入Cassandra超时 | 服务处理异常，返回 `500` |

---

## 9. 高风险区域

- **主键覆写**：`predict_settings`的主键设计为`game_type`，若系统允许重复POST，会导致现有核心设定被意外覆盖，可能触发全盘竞猜逻辑错乱或Killer错误启用。
- **服务拥有权**：虽然`predictservice`是`predict` Keyspace的Owner，但如果有其他服务（如`pricebackendservice`）代理写入请求，需确保请求来源可靠。

---

## 10. 常见错误

- **AI 容易误解**：AI可能会假设此API是用户层面的竞猜设定查询，或者产生复杂的CRUD逻辑。实际上它是管理员用于开启游戏类型竞猜功能的“安装”功能。
- **新人容易犯错**：忘记同时设定`killer_enabled`，导致Killer功能无法开启。忽略Cassandra写入失败的回滚处理。
- **缺失规则确认**：
  - 若`gameType`已存在，是报错还是更新？需要明确**覆盖机制**。
  - `play_modes` 的具体值域需参照游戏系统枚举，AI若生造容易出错。

---

## 11. Evidence

| 类型 | 来源 |
|---|---|
| API 路径 | `README.md` - 竞猜设定表。`POST /api/v1/settings/predict/{gameType}` |
| DB 表名与字段 | `db/predict-detail.md`、`predictSchema` 中的 `predict_settings` 表及重要欄位 |
| Cassandra 权限 | `predictservice-detail.md` - 服务角色总览，本服务为`predict` keyspace的owner |
| Code 范例 | Controller 层路径依据为 `SettingsController`，DataProvider 操作 `predict_settings` |