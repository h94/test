# Bug 分析 — 實際填入範例

> 以 crawlerservice 的 IndexError log 為例
> 展示佔位符填入後的完整 prompt 樣貌
> 此檔案僅供參考，不由 AIReviewServer 直接使用

---

## System Prompt（固定，見 bug-analysis-system.md）

```
你是一個資深工程師，負責分析 production error log 並給出修復建議。
...（同 bug-analysis-system.md 內容）
```

---

## User Prompt（填入實際內容後）

```
## 任務
分析以下 error log，結合對應的 source code，
找出 bug 原因並給出修復方案。

---

## Error Log
guid=94ab063b54-{"requestRawData":"null","state":"Traceback (most recent call last):\n  File \"CrawlerService.py\", line 95, in get_pregame_data\nIndexError: list index out of range\n","uri":""}

---

## 錯誤解析
- 服務：crawlerservice
- 檔案：CrawlerService.py
- 行號：95
- 方法：get_pregame_data
- 錯誤類型：IndexError
- 錯誤訊息：list index out of range
- 第一次發生：2026-05-20 14:22:31
- 發生次數：47（過去 1 小時）
- requestRawData：null

⚠️ requestRawData 為 null，代表呼叫時輸入資料為空。
   請優先從「外部輸入為空」的角度分析觸發原因。

---

## 對應的 Source Code

### 錯誤方法完整內容
>>> 標注的是第 95 行，即錯誤發生位置

```python
    75:     def get_pregame_data(self, match_id: str):
    76:         """
    77:         取得賽前資料，包含主客場資訊、賠率、歷史對戰
    78:         """
    79:         try:
    80:             response = self._api_client.fetch(
    81:                 endpoint="pregame",
    82:                 params={"match_id": match_id}
    83:             )
    84:
    85:             data = response.get("data", [])
    86:
    87:             home_team = data[0].get("home")
    88:             away_team = data[0].get("away")
    89:
    90:             if not home_team or not away_team:
    91:                 return None
    92:
    93:             odds_list = response.get("odds", [])
    94:             best_odds = odds_list[0]
    95: >>>         history = response.get("history", [])[0]
    96:
    97:             return {
    98:                 "home": self._parse_team(home_team),
    99:                 "away": self._parse_team(away_team),
    100:                 "best_odds": best_odds,
    101:                 "history": history
    102:             }
    103:
    104:         except Exception as e:
    105:             self._logger.error(f"[get_pregame_data] {str(e)}")
    106:             raise
```

### 相關的呼叫方（呼叫這個方法的上層）

```python
    210:     def process_match(self, match_id: str):
    211:         """
    212:         處理單一比賽資料
    213:         """
    214:         pregame = self.get_pregame_data(match_id)
    215:         if pregame is None:
    216:             return
    217:         self._store(match_id, pregame)
```

### 相關的 Model / Schema

```python
# 無對應 Model，回應格式由外部 API 決定
```

---

## 服務業務說明

# crawlerservice — DB 操作全貌

這個服務負責從外部賽事資料來源抓取賽前資料、賠率、歷史對戰記錄，
存入內部 DB 供其他服務使用。

## 這個服務不負責的事
| 賽果計算 | predictservice | 結算邏輯在 predictservice |
| 資料對外提供 | backendservice | crawlerservice 只負責抓取和儲存 |

## 常見錯誤
- ❌ 外部 API 回傳格式變動時未做防禦 → 應加格式驗證
- ❌ 外部 API timeout 未重試 → 應加 retry 機制

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
修復後的 code（python）：
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

## 預期 AI 回答的方向（供審核參考，非 AI 輸出）

```
1. 錯誤原因
   第 95 行 response.get("history", [])[0]
   當 history 為空 list 時，[0] 取第一個元素會拋出 IndexError。
   requestRawData 為 null 說明外部 API 本次回傳的資料可能不完整。

2. 觸發情境
   外部賽事 API 在某些比賽（例如新建立、資料不完整的比賽）
   回傳的 history 欄位為空 list，這在業務上是合理的情境。

3. 修復方案
   history_list = response.get("history", [])
   if not history_list:
       self._logger.warning(
           f"[get_pregame_data] match_id={match_id} 無歷史對戰資料，跳過")
       return None
   history = history_list[0]

4. 其他潛在問題
   第 87 行 data[0] 和第 94 行 odds_list[0] 有同樣問題，
   也未做空 list 防禦。

5. 風險評估
   Medium — 影響賽前資料抓取，但不影響核心預測和結算功能。
   建議本次 sprint 修復，同時補上第 87 和 94 行的防禦。
```
