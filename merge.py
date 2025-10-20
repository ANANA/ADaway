import requests
import os
from datetime import datetime
from collections import defaultdict

# 路径配置
URLS_FILE = "urls.txt"
OUTPUT_DIR = "result"
MERGED_FILE = os.path.join(OUTPUT_DIR, "ADaway.txt")  # 去重后规则
DUPLICATES_FILE = os.path.join(OUTPUT_DIR, "duplicates.txt")  # 重复规则备份

def load_urls():
    """从urls.txt读取URL列表"""
    urls = []
    if not os.path.exists(URLS_FILE):
        print(f"错误：{URLS_FILE} 文件不存在")
        return urls
    
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                urls.append(stripped)
    
    if not urls:
        print(f"警告：{URLS_FILE} 中未找到有效URL")
    return urls

def download_rules(url):
    """下载单个规则文件"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text.splitlines()
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return []

def merge_rules():
    """合并规则，去重并备份重复规则"""
    urls = load_urls()
    if not urls:
        return
    
    # 用于统计规则出现次数和来源
    rule_counts = defaultdict(int)  # 规则: 出现次数
    rule_sources = defaultdict(list)  # 规则: 来源URL列表
    all_rules = []  # 存储所有有效规则（含重复）

    # 1. 下载并收集所有规则，记录出现次数和来源
    for url in urls:
        lines = download_rules(url)
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(('!', '#')):
                all_rules.append(stripped)
                rule_counts[stripped] += 1
                if url not in rule_sources[stripped]:  # 避免重复记录同一来源
                    rule_sources[stripped].append(url)

    # 2. 提取去重后的规则和重复规则
    unique_rules = set(all_rules)  # 去重后的规则
    duplicate_rules = {rule for rule in unique_rules if rule_counts[rule] > 1}  # 出现次数>1的规则

    # 3. 生成合并后的规则文件（ADaway.txt）
    merged_comments = [
        "! 合并广告规则文件 (自动生成)",
        f"! 来源: {', '.join(urls)}",
        f"! Update: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"! Total unique rules: {len(unique_rules)}",  # 唯一规则数
        f"! Duplicate rules found: {len(duplicate_rules)}",  # 重复规则数
        ""  # 空行分隔
    ]

    # 4. 生成重复规则备份文件（duplicates.txt）
    duplicate_comments = [
        "! 重复规则备份（在多个来源中出现）",
        f"! 生成时间: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"! 总重复规则数: {len(duplicate_rules)}",
        "",
        "! 格式：规则 [出现次数] (来源URLs)",
        ""
    ]

    # 5. 保存结果文件
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 保存去重后的规则
    with open(MERGED_FILE, 'w', encoding='utf-8') as f:
        for comment in merged_comments:
            f.write(f"{comment}\n")
        for rule in sorted(unique_rules):
            f.write(f"{rule}\n")
    
    # 保存重复规则备份
    with open(DUPLICATES_FILE, 'w', encoding='utf-8') as f:
        for comment in duplicate_comments:
            f.write(f"{comment}\n")
        # 按出现次数降序排列重复规则
        for rule in sorted(duplicate_rules, key=lambda x: -rule_counts[x]):
            f.write(f"{rule} [{rule_counts[rule]}] ({', '.join(rule_sources[rule])})\n")

    print(f"合并完成：")
    print(f"- 去重后规则 {len(unique_rules)} 条，保存到 {MERGED_FILE}")
    print(f"- 重复规则 {len(duplicate_rules)} 条，备份到 {DUPLICATES_FILE}")

if __name__ == "__main__":
    merge_rules()
