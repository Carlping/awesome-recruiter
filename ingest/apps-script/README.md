# Google Form 與 GitHub 串接

1. 建立 Google Form，依 `ingest/form-spec.md` 逐題建立，並選擇不收集 Email。
2. 在表單設定中關閉登入限制，讓任何人都能匿名填寫。
3. 在 Apps Script 貼上同目錄的 `Code.gs`；它會將資料送到私有 inbox repo `Carlping/awesome-recruiter-inbox`。
4. 到 Apps Script「專案設定 → 指令碼屬性」新增 `GITHUB_TOKEN`。使用 fine-grained PAT，僅授予 inbox repo 的 `contents:read`、`contents:write` 與 `metadata` 權限。
5. 在 Apps Script 編輯器執行一次 `setup()`，授權並建立表單提交觸發器。
6. 送出一筆測試表單，確認 GitHub Actions 收到 `repository_dispatch`，並在私有 inbox 開出待審查 PR；公開 repo 不會收到投稿 PR。

Token 不要寫進 `Code.gs`，也不要把 Apps Script 執行記錄或表單回覆提交到本儲存庫。
