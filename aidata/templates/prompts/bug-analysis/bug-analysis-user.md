# Bug 分析 — User Prompt 範本

> 此檔案為 AIReviewServer 產生 User Prompt 的範本
> 大括號 {xxx} 為程式填入的佔位符，說明見下方

---

## 佔位符說明

| 佔位符 | 來源 | 說明 |
|--------|------|------|
| {rawLog} | Loki API | 完整原始 log 內容 |
| {serviceName} | Loki label | 服務名稱，例如 crawlerservice |
| {fileName} | log 解析 | 錯誤發生的檔案名稱 |
| {lineNumber} | log 解析 | 錯誤發生的行號 |
| {methodName} | log 解析 | 錯誤發生的方法名稱 |
| {errorType} | log 解析 | 錯誤類型，例如 IndexError |
| {errorMessage} | log 解析 | 錯誤訊息，例如 list index out of range |
| {timestamp} | Loki API | 第一次發生時間 |
| {count} | Loki API | 過去 1 小時發生次數 |
| {requestRawData} | log 解析 | request 資料，null 時特別標注 |
| {language} | 副檔名判斷 | python / csharp / typescript |
| {fullMethodCode} | 本機 repo | 完整方法 code，錯誤行加 >>> 標注 |
| {callerCode} | 本機 repo | 呼叫此方法的上層方法 code |
| {modelCode} | 本機 repo | 相關 Model 或 Schema，無則留空 |
| {serviceDetailContent} | aidata | webapi/{serviceName}/service-detail.md 內容 |

---

## Prompt 本體

```
## 任務
分析以下 error log，結合對應的 source code，
找出 bug 原因並給出修復方案。

---

## Error Log
{rawLog}

---

## 錯誤解析
- 服務：{serviceName}
- 檔案：{fileName}
- 行號：{lineNumber}
- 方法：{methodName}
- 錯誤類型：{errorType}
- 錯誤訊息：{errorMessage}
- 第一次發生：{timestamp}
- 發生次數：{count}（過去 1 小時）
- requestRawData：{requestRawData}
{requestRawDataNote}

---

## 對應的 Source Code

### 錯誤方法完整內容
>>> 標注的是第 {lineNumber} 行，即錯誤發生位置

{fullMethodCode}

### 相關的呼叫方（呼叫這個方法的上層）

{callerCode}

### 相關的 Model / Schema

{modelCode}

---

## 服務業務說明

{serviceDetailContent}

---

## 請依序回答以下問題

### 1. 錯誤原因（必答）
- 這個錯誤是如何產生的？
- 哪個變數或操作在什麼情況下會導致這個錯誤？

### 2. 觸發情境（必答）
- 什麼樣的輸入、外部資料或系統狀態會觸發這個錯誤？
- 這個情境在正常業務流程中是否合理可能發生？

### 3. 修復方案（必答）
請給出修復後的完整方法 code。

修復原則：
- 保留原有業務邏輯，只修復問題點
- 加入防禦性檢查
- 加上有意義的 log（說明為何跳過或如何處理）
- 符合現有 code 風格，不引入新 library

格式：
修復後的 code（{language}）：
[修復後的完整方法]

修復說明：
[說明改了什麼、為什麼這樣改]

### 4. 是否有其他潛在問題（選答）
在閱讀這段 code 時，是否發現其他明確可見的問題？
只列你在提供的 code 中實際看到的，不要推測看不到的部分。

### 5. 建議的測試案例（選答）
針對這個 bug，應該加入哪些測試情境？

### 6. 風險評估（必答）

嚴重程度：Critical / High / Medium / Low

定義：
- Critical = 核心功能完全中斷，影響所有使用者
- High     = 主要功能異常，影響大部分使用者
- Medium   = 部分功能受影響，有 workaround
- Low      = 邊緣情境，影響少數使用者

影響範圍：哪些功能或使用者受影響

建議修復時程：
- 立即修復（Critical / High）
- 本次 sprint（Medium）
- 下次 sprint（Low）

---

## 如果資訊不足以分析

請說明：
- 還需要看哪些檔案或資訊
- 目前能確定的是什麼
- 目前不確定的是什麼

不要在資訊不足時強行給出結論。
```

---

## requestRawData 為 null 時的額外標注

當 {requestRawData} 為 null 時，在錯誤解析區塊加入以下提示：

```
⚠️ requestRawData 為 null，代表呼叫時輸入資料為空。
   請優先從「外部輸入為空」的角度分析觸發原因。
```

當 {requestRawData} 不為 null 時，此標注省略。

---

## 程式碼格式規範

fullMethodCode 的格式範例（Python）：

```
```python
    65:     def get_pregame_data(self, match_id: str):
    66:         """
    67:         取得賽前資料
    68:         """
    69:         try:
    70:             response = self._api_client.fetch(
    71:                 endpoint="pregame",
    72:                 params={"match_id": match_id}
    73:             )
    74:
    75:             # 解析回應
    76:             data = response.get("data", [])
    77:
    78:             # 取得主客場資料
    79:             home_team = data[0].get("home")
    80:             away_team = data[0].get("away")
    81:
    82:             if not home_team or not away_team:
    83:                 return None
    84:
    85:             result = {
    86:                 "home": self._parse_team(home_team),
    87:                 "away": self._parse_team(away_team),
    88:             }
    89:
    90:             # 取得賠率資料
    91:             odds_list = response.get("odds", [])
    92:             best_odds = odds_list[0]
    93:
    94:             # 取得歷史對戰
    95: >>>         history = response.get("history", [])[0]
    96:
    97:             return {
    98:                 **result,
    99:                 "best_odds": best_odds,
    100:                 "history": history
    101:             }
    102:
    103:         except Exception as e:
    104:             self._logger.error(f"[get_pregame_data] {str(e)}")
    105:             raise
```
```

規則：
- 每行前綴格式：`{行號}: {code}`
- 錯誤行前綴格式：`{行號}: >>> {code}`
- 至少包含錯誤行前 20 行和後 10 行
- 如果方法很長，優先保留錯誤行附近的 context
