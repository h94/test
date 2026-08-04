# predictresultservice — 相關文件摘要

> 此文件由 AI 從 Confluence 自動整理，經資深工程師審核後生效
> 最後更新：2026-05-27 11:31
> 完整索引：[aidata/confluence/_index.md](../../confluence/_index.md)

---

## 業務規範類

目前尚無符合此類別的 Confluence 文件；如有新增會在此區塊補充。

---

## 技術設計類

### mlb.com-HA

> Confluence 頁面 ID：47223108
> 原始文件：[查看 Confluence](https://confluence.zbdigital.net/display/TCZB/mlb.com-HA)
> 摘要檔：[processed/47223108-summary.md](../../confluence/processed/47223108-summary.md)
> Confluence 最後更新：2023-08-23 13:46
> 摘要最後同步：2026-05-27 11:31
> ⚠️ 若摘要和 Confluence 原始文件有出入，以 Confluence 為準

**摘要**：
這是一份 MLB 棒球讓分預測的模型實驗記錄，比較了多種回歸模型（神經網路、XGBoost、RandomForest、SVR、KNN、LGBM 等）在加入先發投手和官方 EVA 數據前後的表現。實驗篩選了相關係數大於 0.3 的特徵，並以 7/30 前資料訓練、8/1 後測試，用 MSE 和 HA 勝率評估。結果顯示 RandomForest 和 KNN 在測試與回測上獲得較佳的下注勝率，可作為後續預測服務的基線參考與特徵選擇依據。

**關鍵設計決策**：
- 使用相關係數 > 0.3 篩選特徵，選出的欄位包含主客隊的打擊、投球、守備統計及 composite stats（AVG, OBP, SLG, OPS, ERA），後綴 _h 表主隊、_a 表客隊。
- 訓練數據切分：2023 年 7 月 30 日以前（1603 筆）為訓練集，8 月 1 日以後為測試集；回測使用 6 月 1 日以後共 1047 筆數據。
- 以 MSE 為 loss 進行訓練，並採用 RandomSearch（10 次）分別對 Neural Network、XGBoost、RandomForest、SVR、KNN、DecisionTree 搜尋最佳超參數。
- 後續實驗導入「先發投手」和「EVA」取自官方網站的特徵，並增加 LGBMRegressor、KNeighborsRegressor、DecisionTreeRegressor 進行比較。
- 模型評估採用 HA error（預測差分與實際差分的平均絕對誤差）以及「下注勝率」（預測主客方向正確的場次比例），並以回測確認穩定度。

**影響範圍**：
- 此實驗記錄為模型開發階段的技術參考，若後續擴充 MLB 預測服務，可沿用上述特徵選擇邏輯與模型比較基準。
- HA error 與下注勝率的評估方式可作為 predictresultservice 成果驗收的參考指標。

---

## 歷史決策類

目前尚無符合此類別的 Confluence 文件；如有新增會在此區塊補充。

---

## 操作手冊類

目前尚無符合此類別的 Confluence 文件；如有新增會在此區塊補充。