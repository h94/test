# 更新會員資料

## 1. 場景目的

會員更新其個人資料，根據業務邏輯，系統進行相關驗證和數據庫更新。

---

## 2. 入口 API

| Method | Path | 說明 |
|---|---|---|
| PUT | /api/v1/member/{authKey} | 更新會員資料 |

---

## 3. 流程總覽

1. 接收更新會員資料請求
2. 進行資料驗證，包括 email 格式和黑名單檢查
3. 更新 `member.gameusers` 表中的相應欄位
4. 清除相關的 Redis Cache
5. 回傳操作結果

---

## 4. 程式流程

| 順序 | Layer | Class / Method | 動作 |
|---|---|---|---|
| 1 | Controller | MemberController.UpdateMember | 接收與解析更新資料請求 |
| 2 | Service | MemberService.ValidateMemberData | 驗證會員資料的合法性 |
| 3 | Service | MemberService.UpdateMemberInDB | 更新資料到 `gameusers` 表 |
| 4 | Service | CacheService.InvalidateMemberCache | 清除相關會員的 Cache |
| 5 | Controller | MemberController.ResponseUpdate | 回應請求結果 |

---

## 5. DB / Cache / Queue 使用

| 類型 | 資源 | 操作 | 用途 |
|---|---|---|---|
| DB | member.gameusers | Update | 更新會員資料 |
| Redis | GameUser:{authkey} | Delete | 清除會員 Cache 保持一致性 |

---

## 6. 重要規則

- **email** 需驗證格式，並與 `forbidden_email_domains` 黑名單比對確認
- 更新流程需確保不修改 **authkey** 和 **password**
- **status** 欄位修改僅能透過驗證流程或管理後台進行
- **rank** 和 **memberships** 欄位受特定業務邏輯控制，不可手動直接修改

---

## 7. 錯誤情境

| 情境 | 預期結果 |
|---|---|
| email 格式不正確 | 回傳錯誤訊息，更新失敗 |
| email 在黑名單中 | 回傳錯誤訊息，拒絕更新 |
| 欄位驗證失敗（如 status） | 拒絕更新，提示合法性錯誤 |

---

## 8. 測試重點

| Test ID | 類型 | 情境 | 預期結果 |
|---|---|---|---|
| T1 | Integration Test | 更新合法資料 | 成功更新會員資料 |
| T2 | API Test | email 格式錯誤 | 返回400錯誤 |
| T3 | Permission Test | 測試未授權更新重要欄位 | 操作被拒絕 |

---

## 9. 高風險區域

- **DB 操作**: 更新 `gameusers` 中的 email 時需小心，以避免與黑名單重複
- **Cache Consistency**: 確保每次更新會員資料後，立即刪除對應的 Redis Cache
- **欄位驗證**: 確保所有敏感欄位均遵循完整驗證與限制

---

## 10. 常見錯誤

- 新人易忘刪除 Cache，導致資料不一致
- 錯誤地允許直接更新受保護的欄位
- 忽視 email 黑名單檢查，導致後續操作失誤
- 未檢查 `status` 狀態合法性，從而影響使用者功能

---

## 11. Evidence

| 類型 | 來源 |
|---|---|
| API | MemberController.UpdateMember |
| DB | member.gameusers |
| Redis | GameUser:{authkey} |
| Code | MemberService.UpdateMemberInDB |
| SQL | Update member.gameusers SET ... WHERE authkey = ? |