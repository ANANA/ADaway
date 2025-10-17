# 个人自用

# 广告规则自动合并工具

自动定时下载并合并以下广告过滤规则：
- https://anti-ad.net/easylist.txt
- https://gp.adrules.top/dns.txt

合并过程中会自动剔除重复规则，最终结果文件为 `result/merged_rules.txt`。

## 定时更新
每天 UTC 时间 0 点（北京时间 8 点）自动执行更新，结果会提交到本仓库。
