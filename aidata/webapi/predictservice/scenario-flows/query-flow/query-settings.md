# 查询竞猜及Killer设定

## 1. 场景目的

提供一个集合查询入口，让前端一次取得当前竞猜玩法及Killer机制设定（包含周期、派彩等），减少多支API调用并确保资料版本一致。

---

## 2. 入口 API

| Method | Path | 说明 |
|---|---|---|
| GET | `/api/v1/settings/predict/{gameType}` | 查询特定游戏类型竞猜设定 |
| GET | `/api/v1/settings/killer/cycles` | 查询Killer周期设定 |
| GET | `/api/v1/settings/killer/cycles/{gameType}/{lid}/{cid}` | 查询特定联赛/周期的Killer设定 |
| GET | `/api/v1/settings/playmodes/{gameType}` | 查询特定类型玩法设定 |

---

## 3. 流程总览

1. 前端组合呼叫查询竞猜设定与Killer周期
2. API网关透过ECFramework验证Token与权限
3. Controller接收request后转交Service
4. Service呼叫DataProvider执行Cassandra查询
5. `predict_settings`、`killer_cycle_settings`、`killer_accounts` 查询后组装回传
6. 如果有设定快取过期策略则顺便标记或淘汰（当次不立即淘汰）

---

## 4. 程式流程

| 顺序 | Layer | Class / Method | 动作 |
|---|---|---|---|
| 1 | Controller | PredictSettingController.Get | 接收GET request，验证gameType参数 |
| 2 | Service | PredictSettingService.GetSetting | 组合查询条件并呼叫Provider |
| 3 | Provider | PredictSettingProvider.GetByGameType | 对Cassandra `predict_settings` 执行单笔查询 |
| 4 | Controller | KillerCycleController.Get | 接收GET request，可选lid/cid参数 |
| 5 | Service | KillerCycleService.Get | 组合周期过滤条件 |
| 6 | Provider | KillerCycleProvider.GetCycles | 对Cassandra `killer_cycle_settings` 执行查询 |
| 7 | Provider | KillerAccountProvider.GetByLidCid | 查询特定杀手帐号（非本人时不回传account） |

---

## 5. DB / Cache / Queue 使用

| 类型 | 资源 | 操作 | 用途 |
|---|---|---|---|
| DB | `predict.predict_settings` | Read | 竞猜主设定（game_type, play_modes, killer_enabled） |
| DB | `predict.killer_cycle_settings` | Read | Killer周期设定（lid, cid, pay_out） |
| DB | `predict.killer_accounts` | Read | Killer帐号列表（lid, cid, account） |
| Redis | — | 无直接写入 | 此流程无直接快取互动（若有则需人工确认） |
| Queue | — | 无 | 此流程仅读操作，不使用Queue |

---

## 6. 重要规则

- **权限限制**：所有API皆须经过ECFramework验证，后端操作需额外权限检查。
- **不可暴露资料**：`password`、`email`、`authkey`不可回传；`phone`、`handler`需遮蔽。公开排行榜不可回传`account`（仅rank与统计）。
- **Killer查询**：`killeraccounts_{gameType}`查询必须带`lid`、`cid`，避免跨周期全表扫描。
- **状态限制**：帐号查询需确保 `enabled = 1`；已关闭／冻结帐号（`closetime IS NOT NULL`或`status ≠ 1`）不返回。
- **时间处理**：活动时间比对需将`startdate`+`starttime`、`enddate`+`endtime`合并为DateTime后比较，避免时区问题。
- **保守读取**：`GetAllGameUsers`全表扫描仅供后台，查询需限制条件。

---

## 7. 错误情境

| 情境 | 预期结果 |
|---|---|
| gameType不存在 | 回传空或404 |
| Killer周期未设定(lid/cid不存在) | 回传空集合 |
| Token过期或无效 | ECFramework回401 |
| 请求带非授权site（跨站查询） | 查询无结果或403 |
| Cassandra查询timeout | 回5xx并记录applogs |

---

## 8. 测试重点

| Test ID | 类型 | 情境 | 预期结果 |
|---|---|---|---|
| QT001 | API Test | 查询有效gameType设定 | 回200含完整设定栏位 |
| QT002 | API Test | 查询不存在gameType | 回404或空，无exception |
| QT003 | Permission Test | 无Token直接call | 回401 |
| QT004 | Flow Test | 查询Killer cycle时仅提供gameType | 回该游戏类型下所有lid/cid设定 |
| QT005 | Flow Test | 查询Killer accounts时未提供lid | 依主键限制查询；测试是否全表扫描（应拒绝或报错） |

---

## 9. 高風險区域

- **高風險table**：`predict_settings`（预设值错误可能影响全局）、`killer_cycle_settings`（pay_out误写会造成金流错误）。
- **跨服务资料同步**：Killer周期与memberservice对账需人工比对。
- **Cache consistency**：若后续引入Redis快取，设定变更后需立即失效，不可单纯依赖TTL。
- **不可逆操作提醒**：虽然此场景只读，但相关写API（如PUT payout/close cycle）存在不可逆特性。

---

## 10. 常见错误

- ❌ 查询`killer_accounts`未加`lid`／`cid`条件 → 导致跨周期扫描，效能极差。
- ❌ 回传player account在Killer公开API中 → 应以更名或遮蔽显示。
- ❌ 时间格式直接字串比对而非DateTime，导致时区误判。
- ❌ 误用`GetAllGameUsers`做一般列表查询。
- ❌ 忽略`status`或`enabled`栏位，回传已停用帐号。

---

## 11. Evidence

| 类型 | 来源 |
|---|---|
| API | PredictSettingController.Get, KillerCycleController.Get |
| DB | predict.predict_settings, predict.killer_cycle_settings |
| Code | PredictSettingService.GetSetting, KillerCycleProvider.GetCycles |
| Document | predictservice-detail.md（DB操作边界） |