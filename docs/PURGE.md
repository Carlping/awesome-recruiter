# 真實下架與 Git 歷史清除手冊

本手冊只供維護者處理已確認需要永久移除的資料。下架前請先建立或更新申訴 Issue，記錄 Issue 編號、確認日期、下架原因與通知對象。

## 1. 確認資料

確認 review `id`、下架理由與 YAML 路徑。可用的 `reason`：

- `pii`：含個資
- `defamation_claim`：申訴後無法佐證
- `harassment`：人身攻擊／騷擾
- `fake`：造假／重複
- `requester`：投稿者自行要求
- `legal`：法律要求

在 repository 根目錄執行：

```bash
.venv/bin/python scripts/purge.py \
  --id rv-202608-000001 \
  --reason pii \
  --date 2026-09-02
```

`purge.py` 會刪除 review YAML、在 `data/removed.yaml` 加入只含識別碼的墓碑並排序，接著只列印後續命令，不會自行改寫或推送 git history。請確認輸出與墓碑內容後再繼續。

## 2. 清除本地 Git 歷史

若尚未安裝 `git-filter-repo`：

```bash
python -m pip install git-filter-repo
```

依 `purge.py` 輸出的路徑執行：

```bash
git add -A && git commit -m "Remove rv-202608-000001"
git filter-repo --invert-paths \
  --path data/reviews/2026/rv-202608-000001.yaml \
  --force
```

`git filter-repo` 可能會移除 remote，請重新加入：

```bash
git remote add origin https://github.com/Carlping/awesome-recruiter.git
git push --force --all origin
git push --force --tags origin
```

強制推送前請確認所有維護者已知悉，並確認 branch、tag 與工作樹內容。不得重新使用已下架的 id。

## 3. 請 GitHub 清除快取與 fork

透過 [GitHub Support request](https://support.github.com/request) 申請清除敏感資料的 cache、搜尋結果與 fork。可參考 [GitHub 官方文件](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)。

同時通知已知 fork 維護者，請他們依相同路徑清除本地與遠端歷史。保留 Support request 編號與回覆。

## 4. 完成紀錄

在申訴 Issue 補上：

- 下架處理日期與維護者；
- `purge.py` 使用的 reason；
- history rewrite 與 force push 日期；
- GitHub Support request 編號；
- 已通知的 fork 或其他公開快取位置。
