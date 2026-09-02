# 貢獻指南

感謝你協助建立更透明、尊重求職者的招募資料。

## 新增資料

1. 請只提交自己的真實經驗，移除姓名、電話、Email、住址及其他可識別個資。
2. 匿名投稿請使用 Google Form；原始資料會先進入私有 inbox，不要直接把未審查內容提交到公開 repository。
3. 摘要只寫可描述的事實與個人體驗，不寫私生活、猜測或人身攻擊。
4. 維護者會在私有 inbox 建立審查 PR；不要在任何 PR 或 Issue 文字暴露投稿人的身分。

## 本機檢查

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/build_index.py
```

CI 會在 PR 與 `main` push 時重跑驗證與索引建置。公開 review 由私有 inbox 審核後發佈；資料下架與歷史清除流程見 `GOVERNANCE.md` 與 `docs/PURGE.md`。

## 私有 inbox 審查

維護者會在私有 inbox PR 檢查 schema、taxonomy、個資風險、是否與既有紀錄重複，以及摘要是否符合事實與倫理原則。審查 PR 合併後才會發佈；關閉 PR 則丟棄內容。爭議內容可先標記 `flagged`，在申訴程序完成前不會公開。
