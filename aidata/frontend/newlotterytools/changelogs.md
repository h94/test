# newlotterytools — 變更紀錄

> 由 AI Review Server 依 MR（同時含 `_plans/` + code）自動維護。

## 歷年索引

| 年度 | 檔案 | 備註 |
|------|------|------|
| 2026 | （本檔下方） | 進行中 |

## 2026

<!-- 新條目插於此區塊頂部 -->

### 2026-06-08 — MR !10

變更摘要：本次 MR 實作後台討論區管理、水桶名單維護及訊息中心三大功能模組。討論區管理頁面支援依板塊分頁瀏覽主題、檢視完整內文與回文，並可刪除主題及回文；分頁採用 nextPage 模式，表格以 items-per-page="-1" 關閉內建切片。水桶管理頁面提供新增、編輯與解除禁言，新增時透過搜尋玩家（帳號或暱稱）帶入會員資訊。訊息中心涵蓋通知主題與文章管理，主題 Icon 限三選一，文章支援繁中、英文標題內容編輯與硬刪除。同時更新 Sidebar 選單架構，擴充 API 函式並定義相關 TypeScript 介面。

| 檔案路徑 | 變更類型 | 說明 |
|---------|---------|------|
| apis/index.ts | 修改 | 新增討論區、水桶、通知相關 API 函式共 18 支，包含分頁查詢、刪除及玩家搜尋 |
| components/forum/ForumCommentsModal.vue | 新增 | 回文列表對話框，支援 nextPage 分頁、刪除回文與關閉內建分頁 |
| components/forum/ForumDeleteConfirm.vue | 新增 | 刪除確認對話框，區分主題與回文類型，Toast 成功訊息 |
| components/forum/ForumSubjectDetailModal.vue | 新增 | 主題詳情模態窗，顯示完整標題、內文及會員暱稱 |
| components/global/Sidebar.vue | 修改 | 新增「社群管理」與「訊息管理」群組及子項目（討論區管理、水桶管理、主題管理、文章管理） |
| components/global/input/Switch.vue | 修改 | 擴充 v-switch 元件，支援 v-model、label、readonly 及自訂 trueValue/falseValue |
| config/forum/forum.ts | 新增 | 討論區狀態文案、分頁常數（FORUM_PAGE_SIZE、FORUM_TABLE_ITEMS_PER_PAGE）及會員暱稱格式化函式 |
| pages/community/forums.vue | 新增 | 討論區管理頁，板塊選擇、主題分頁表、會員暱稱本地篩選、詳情/回文/刪除操作 |
| pages/member/banned.vue | 新增 | 水桶管理頁，列表、新增（搜尋玩家）、編輯、解除禁言，Toast 提示 |
| pages/notification/messages.vue | 新增 | 通知文章管理頁，主題篩選、新增/編輯/硬刪除，表單驗證 |
| pages/notification/topics.vue | 新增 | 通知主題管理頁，Icon 三選一、啟用/停用開關，CRUD 操作 |
| types/forum/Forum.ts | 新增 | 討論區相關 TypeScript 介面（IForum、IForumSubject、IForumComment、分頁查詢與結果） |
| types/member/Banned.ts | 新增 | 水桶名單及請求介面（IBanned、ICreateBannedBody、IUpdateBannedBody） |
| types/member/UserSearch.ts | 新增 | 玩家搜尋結果介面（INewLotteryUserSearch） |
| types/notification/Message.ts | 新增 | 通知文章及請求介面（INotificationMessage 等） |
| types/notification/Topic.ts | 新增 | 通知主題及請求介面（INotificationTopic 等） |

---
