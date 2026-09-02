# 貢獻指南

感謝你協助建立更透明、尊重求職者的招募資料。

## 新增資料

1. 請只提交自己的真實經驗，移除姓名、電話、Email、住址及其他可識別個資。
2. 使用 `data/reviews/YYYY/rv-YYYYMM-XXXXXX.yaml`，欄位依 schema 與 taxonomy。
3. 摘要只寫可描述的事實與個人體驗，不寫私生活、猜測或人身攻擊。
4. 送出 PR，說明資料來自直接投稿或匿名表單；不要在 PR 文字暴露投稿人的身分。

## 本機檢查

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/build_index.py
```

CI 會在 PR 與 `main` push 時重跑驗證與索引建置。合併前請確認 `status` 正確；需下架時保留檔案與 `id`，改用 `status: removed`，流程見 `GOVERNANCE.md`。

## PR 審查

維護者會檢查 schema、taxonomy、個資風險、是否與既有紀錄重複，以及摘要是否符合事實與倫理原則。爭議內容可先標記 `flagged`，在申訴程序完成前不保證公開。
