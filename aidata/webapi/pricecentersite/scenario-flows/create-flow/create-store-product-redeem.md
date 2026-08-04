# 商城商品兌換

## 1. 場景目的
使用者在前端商城選擇商品，填寫收件人資料（姓名、地址、電話），提交兌換請求。系統驗證使用者身份、商品狀態後，將兌換記錄寫入 `product_store_redeem_logs`，初始狀態設為 `"pending"`（待處理）。後續由後台或物流系統更新狀態。

---

## 2. 入口 API
需人工確認：OpenAPI 文件中未列出此端點，推測為 `POST /api/Store/Redeem`。

| Method | Path | 說明 |
|--------|------|------|
| POST | `/api/Store/Redeem`（推測） | 提交商城商品兌換請求 |

---

## 3. 流程總覽
1. 接收請求（含 `authKey`、`pclass`、`pid`、`recipient`、`address`、`phonenumber`）
2. 依據 `authKey` 查詢 `member.gameusers`，驗證帳號狀態（`status=1`）
3. 查詢 `product.products_store`，確認商品 `status='1'`（上架）且庫存 > 0
4. 驗證輸入欄位：`address`、`phonenumber`、`recipient` 不可為空，電話需符合格式（如 10 碼數字）
5. 產生兌換記錄 `id`（UUID）與 `addtime`（UTC 時間戳）
6. 寫入 `product.product_store_redeem_logs`，`status` 固定為 `"pending"`
7. 回傳成功回應（可含兌換記錄摘要，但不可暴露 `address`、`phonenumber` 完整內容）

---

## 4. 程式流程
（以下為推測層架構，實際名稱需人工確認）

| 順序 | Layer | Class / Method | 動作 |
|------|-------|---------------|------|
| 1 | Controller | `StoreController.Redeem` | 接收 DTO，委派 Service |
| 2 | Validator | `StoreRedeemValidator` | 驗證必填欄位與格式 |
| 3 | Service | `StoreService.Redeem` | 調用 Provider 進行 DB 操作 |
| 4 | Provider | `MemberProvider.GetGameUserByAuthKey` | 查詢 `member.gameusers` 取得 `account`、`status` |
| 5 | Provider | `ProductStoreProvider.GetProduct` | 查詢 `product.products_store` 取得商品狀態、庫存 |
| 6 | Provider | `RedeemLogProvider.Insert` | 寫入 `product.product_store_redeem_logs` |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|------|------|------|------|
| DB | `member.gameusers` | Read | 驗證 authKey 並取得 account 與啟用狀態 |
| DB | `product.products_store` | Read | 檢查商品上架 (`status='1'`) 與庫存 (>0) |
| DB | `product.product_store_redeem_logs` | Write | 寫入兌換記錄，初始 `status='pending'` |
| Redis | `product:store:{pclass}:{pid}` | 可能 Read | 若快取存在則讀取商品資訊，否則回源 DB（非必要） |

---

## 6. 重要規則

- **權限限制**：僅通過 `authKey` 驗證且 `member.gameusers.status=1` 的帳號可提交
- **欄位限制**：
  - `address`、`phonenumber`、`recipient` 不可為空
  - `phonenumber` 需符合台灣手機格式（e.g., 09xx-xxx-xxx，10 碼數字，可含符號）
- **不可暴露資料**：對外 API 回傳時不得包含完整 `address`、`phonenumber`、`recipient`；僅回傳兌換記錄 `id`、商品名稱、狀態等
- **TTL 規則**：無
- **Transaction 規則**：無分散式交易，寫入 log 為單一 Cassandra INSERT
- **Retry 規則**：若寫入失敗，前端可重試（但需注意冪等性，由 `id` 唯一性保證）
- **狀態值限制**：寫入時 `status` 必須固定為 `"pending"`，不可由前端指定其他值
- **不可修改欄位**：`id`、`addtime`、`account` 寫入後不可變更

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|------|----------|
| 帳號不存在或 `status` 不為 1 | 回傳 401/403 錯誤訊息（需人工確認） |
| 商品不存在、已下架（`status!='1'`）或庫存為 0 | 回傳 400 錯誤，提示「商品不可兌換」 |
| `address`、`recipient` 為空 | 回傳 400 錯誤，提示「必填欄位」 |
| `phonenumber` 格式不符 | 回傳 400 錯誤，提示「電話格式不正確」 |
| Cassandra 寫入失敗 | 回傳 500 錯誤，可重試 |
| 同一 `id` 重複提交 | 因主鍵約束寫入失敗，回傳 409 衝突（若前端未產生唯一 id 則由系統生成） |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---------|------|------|----------|
| TC01 | Integration | 正常兌換（帳號有效、商品上架、庫存充足） | 成功回傳，DB 出現 status='pending' 記錄 |
| TC02 | Permission | 使用已凍結或未啟用帳號的 authKey | 拒絕請求，回傳 401/403 |
| TC03 | API Test | 缺少 `address` 或 `recipient` | 400 欄位驗證失敗 |
| TC04 | API Test | `phonenumber` 格式錯誤（如過短、含英文字） | 400 格式錯誤 |
| TC05 | Flow Test | 商品庫存為 0 | 400 提示無庫存 |
| TC06 | Flow Test | 商品已下架 | 400 提示不可兌換 |
| TC07 | API Test | 嘗試在 request 中指定 status 非 'pending' | 伺服器忽略或 400（需確認） |

---

## 9. 高風險區域

- **高風險 table**：`product_store_redeem_logs` 的 PII 欄位 (`address`, `phonenumber`, `recipient`)，需嚴格控制讀取權限
- **高風險 API**：兌換 API 若無正確驗證或記錄審核，可能導致洗商品或資訊洩漏
- **庫存一致性**：目前未使用 CAS（LWT）進行原子扣減，僅作讀取檢查，可能超賣（需人工確認是否後續有獨立扣庫邏輯）
- **Idempotency**：若客戶端未帶 `id` 由系統生成，重試可能產生重複記錄；應使用客戶端提供的 id 或記錄唯一約束
- **個人資料暴露**：任何對外查詢記錄 API 必須遮蔽 `address`、`phonenumber`，僅用戶本人或後台可看完整資訊

---

## 10. 常見錯誤

- ❌ 未檢查 `member.gameusers.status=1` 就寫入兌換記錄 → 已停用帳號仍可兌換
- ❌ 允許前端傳入 `status` 參數 → 可能跳過審核或竄改狀態
- ❌ 兌換記錄查詢 API 直接回傳完整 `address`、`phonenumber` → 個資洩漏
- ❌ 地址或電話僅依前端驗證，後端未檢查 → 寫入無效或惡意資料
- ❌ 未過濾商品狀態或庫存 → 下架商品仍可被兌換

---

## 11. Evidence

| 類型 | 來源 |
|------|------|
| DB Table | `product.product_store_redeem_logs` schema（包含 address、phonenumber、recipient、status 等欄位） |
| DB detail | `product-detail.md`：status 初始為 "pending"；地址電話欄位需驗證格式 |
| Auth | `member-detail.md`：登入驗證須 `status=1` |
| 商品讀取 | `product-detail.md`：`products_store` 須 WHERE `status='1'` 上架 |
| 不可回傳欄位 | `product-detail.md`：對外 API 不可回傳完整 address、phonenumber |
| API 入口 | 需人工確認 – OpenAPI 未列出此端點，推測存在內部 Controller |
| 測試建議 | 需人工確認現有測試腳本（若無則應新增） |