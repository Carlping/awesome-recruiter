# Google Form 題目規格

題目標題必須逐字一致；選項必須使用下列中文標籤。Apps Script 會以題目標題作為 `e.namedValues` 的鍵。

| 題目 | 型態 | 選項／格式 | payload 欄位 |
| --- | --- | --- | --- |
| Recruiter 顯示名稱 | 簡答 | 1–60 字；可使用匿名化名稱 | `recruiter.name` |
| Recruiter 類型 | 單選 | 企業內部 HR；獵頭；仲介／派遣；RPO；不確定 | `recruiter.type` |
| Recruiter 所屬公司 | 簡答 | 必填，1–120 字 | `recruiter.company` |
| Recruiter LinkedIn | 簡答 | 選填，`https://www.linkedin.com/in/` 開頭 | `recruiter.linkedin` |
| 應徵公司 | 簡答 | 選填 | `hiring_company` |
| 產業 | 下拉選單 | 半導體；硬體／電子；軟體；網路平台；金融科技；金融／銀行；保險；顧問；電商／零售；製造；生技／製藥；醫療；教育；媒體／行銷；遊戲；電信；政府／非營利；其他 | `industry` |
| 地區 | 下拉選單 | 台北市；新北基隆；桃竹苗；中部；南部；東部與離島；遠端；海外；不確定 | `region` |
| 職務族群 | 下拉選單 | 軟體工程；資料／AI；硬體工程；產品／專案管理；設計；行銷；業務／商務開發；營運；財務／會計；人資；法務；客服；研究；其他 | `role_family` |
| 職級 | 單選 | 實習；初階；中階；資深；主管／帶人 | `seniority` |
| 接觸管道 | 下拉選單 | 104；1111；LinkedIn；Yourator；CakeResume；獵頭主動聯絡；內推；公司官網；其他 | `channel` |
| 評價月份 | 簡答 | `YYYY-MM` | `period` |
| 走到的階段 | 單選 | 僅聯絡；電話初談；面試；拿到 offer；被拒絕；無聲卡 | `stage_reached` |
| 回應速度 | 線性刻度 | 1–5 | `scores.score_responsiveness` |
| 資訊透明 | 線性刻度 | 1–5 | `scores.score_transparency` |
| 專業度 | 線性刻度 | 1–5 | `scores.score_professionalism` |
| 尊重 | 線性刻度 | 1–5 | `scores.score_respect` |
| 結果通知 | 線性刻度 | 1–5 | `scores.score_closure` |
| 是否無聲卡 | 單選 | 是；否 | `ghosted` |
| 是否事前揭露薪資 | 單選 | 是；否 | `salary_disclosed_upfront` |
| 是否願意再次接觸 | 單選 | 是；否 | `would_engage_again` |
| 經驗摘要 | 段落 | 0–300 字；只寫事實與個人體驗 | `summary` |
