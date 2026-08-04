# newlottery — 變更紀錄

> 由 AI Review Server 依 MR（同時含 `_plans/` + code）自動維護。

## 歷年索引

| 年度 | 檔案 | 備註 |
|------|------|------|
| 2026 | （本檔下方） | 進行中 |

## 2026

<!-- 新條目插於此區塊頂部 -->

### 2026-06-02 — MR !37

變更摘要：本次合併依照 TCZB-4397 規格重構通知中心為兩層式 UI（主題分頁切換與文章列表），首頁通知改依 API 提供的主題群組展示最新三則，並保留卡片索引套色邏輯。同時為論壇發文、留言、按讚與收回讚加入禁言（403）及系統錯誤（500）的 Toast 提示，並補上對應元件的 `data-testid` 以利 E2E 測試。此 MR 亦涵蓋範圍外的多項功能：文章及留言的圖片上傳與預覽、社群連結預覽（影片嵌入／連結卡片），以及賣牌獲利標籤等調整。

主要變更（code）：
| 檔案 | 說明 |
|------|------|
| `apis/index.ts` | 新增 `GetNotificationTopics` 函式，`GetNotificationList` 加入可選 `tid` 參數；建立與更新文章、留言的 API 改為傳遞圖片路徑，並支援 `File` 上傳；通知 API 強制不帶 `lang` query。 |
| `types/notification/NotificationTopic.ts` | 新增 `INotificationTopic` 型別（id, name, icon）。 |
| `pages/notification/index.vue` | 全面重構為主題分頁切換兩層 UI，加入 `loading` / 空狀態處理，列表列顯示 topic icon，並於關鍵區塊加入 `data-testid`。 |
| `pages/index.vue` | 首頁通知改為先取得主題列表，再依主題各取最新一則，最多三則顯示；保留依卡片索引套色；加入 `data-testid="home-notifications"`。 |
| `components/notification/DetailModal.vue` | 加入 `data-testid="notification-detail-modal"`。 |
| `pages/forum/index.vue` | 發文按鈕加入 `data-testid="forum-publish-btn"`；新增從文章詳情頁返回時依 query 刷新列表的機制。 |
| `pages/forum/[subjectId].vue` | 為留言發送、文章/留言按讚與收回讚加入 `toastCommunityError` 處理禁言及系統錯誤提示；新增 `data-testid="forum-comment-submit"` 與 `data-testid="forum-post-like-btn"`；額外實作圖片上傳（預覽、移除）、社群連結預覽嵌入（YouTube / TikTok / Instagram 等影片及連結卡片）、編輯模式圖片管理，以及大量對應樣式。 |
| `components/forum/ForumPublishModal.vue` | 發文 Modal 實作圖片上傳（選擇、預覽、移除），加 `data-testid="forum-publish-submit"`；根據 API 錯誤碼顯示「您已被禁言，無法發文」或「系統忙碌，請稍後再試」；加強送出前校驗。 |
| `pages/profile/index.vue` | 增加「賣牌獲利」的鑽石明細內容標籤對應。 |
| `server/api/link-preview.get.ts` | 新增伺服器端代理 noembed 的連結預覽 API，供論壇文章內文使用。 |

---
