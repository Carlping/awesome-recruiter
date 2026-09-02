# Recruiter Review TW

以匿名、結構化的方式，讓台灣人在世界各地分享對個別 recruiter／HR／獵頭的真實求職體驗。

## 為什麼做

面試趣的評題、PTT 的討論很有價值，卻常是零散文字，難以長期比較與查找。這個開放資料專案用 Git、YAML 與公開欄位，記錄 recruiter 在聯絡與招募流程中的表現；初始資料是**明顯虛構的示範資料**，不是任何真實人物或公司的指涉。

## 五個評分維度

每項 1–5 分：

1. **回應速度**：是否在合理時間回覆。
2. **資訊透明**：薪資、流程與時程是否清楚。
3. **專業度**：是否了解職缺，推薦與 JD 是否吻合。
4. **尊重**：是否準時、友善，且避免臨時取消。
5. **結果通知**：是否在流程後告知結果。

## 如何參與

- **匿名表單**：[填寫匿名評價表單（連結待設定）](https://example.com/anonymous-recruiter-review-form)
- **直接開 PR**：依 `schema/review.schema.json` 新增一筆 YAML，並先在本機執行驗證。
- **Fork 分析資料**：執行 `scripts/build_index.py` 產生本地索引，或直接分析 `data/reviews/`。

## 資料欄位

| 欄位 | 說明 |
| --- | --- |
| `id`、`submitted_at`、`period` | 評價識別碼、提交日期、經歷月份 |
| `recruiter.name`、`type`、`company`、`linkedin` | recruiter 顯示名稱、類型、所屬公司、可選的公開 LinkedIn |
| `hiring_company` | 應徵公司；與 recruiter 所屬公司不同時才填 |
| `industry`、`country`、`tw_region`、`role_family`、`seniority`、`channel` | 產業、國家／地區、台灣子地區（僅台灣可填）、職務族群、職級、接觸管道 |
| `stage_reached`、`ghosted` | 走到的階段與是否無聲卡 |
| `scores` | 回應速度、資訊透明、專業度、尊重、結果通知，均為 1–5 |
| `salary_disclosed_upfront`、`would_engage_again` | 是否事前揭露薪資、是否願意再次接觸 |
| `summary` | 0–300 字的事實與個人體驗摘要 |
| `source`、`status` | 資料來源與審核狀態 |

搜尋網站：[Recruiter Review TW](https://carlping.github.io/awesome-recruiter/)（需在 Settings → Pages 啟用 GitHub Actions 來源）

## 法律與倫理原則

只記錄可由投稿者負責的事實與個人體驗，不推測動機、不煽動攻擊。禁止聯絡資訊、住址、私生活、與職缺無關的個資及歧視性內容。被點名者可以申訴；下架標準與流程見 [`GOVERNANCE.md`](GOVERNANCE.md)。

## 授權

資料採 **CC BY-SA 4.0**，程式碼採 **MIT**。完整條款與適用範圍見 [`LICENSE`](LICENSE)、[`LICENSE-CODE`](LICENSE-CODE) 與 [`LICENSE-DATA`](LICENSE-DATA)。
