import requests
import os
from datetime import datetime
from collections import defaultdict

# 路径配置
URLS_FILE = "urls.txt"
URL_ALIASES_FILE = "url_aliases.txt"  # URL缩写配置文件
OUTPUT_DIR = "result"
MERGED_FILE = os.path.join(OUTPUT_DIR, "ADaway.txt")
DUPLICATES_FILE = os.path.join(OUTPUT_DIR, "duplicates.txt")

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

def load_url_aliases():
    """从url_aliases.txt读取URL与缩写的映射"""
    aliases = {}
    if not os.path.exists(URL_ALIASES_FILE):
        print(f"警告：{URL_ALIASES_FILE} 文件不存在，将使用原始URL")
        return aliases
    
    with open(URL_ALIASES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                url, alias = stripped.split('=', 1)  # 只按第一个=分割
                aliases[url.strip()] = alias.strip()  # 去除首尾空格
    return aliases

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
    """合并规则，去重并备份重复规则（显示URL缩写）"""
    urls = load_urls()
    if not urls:
        return
    
    # 加载URL缩写映射（无缩写则使用原始URL）
    url_aliases = load_url_aliases()

    # 用于统计规则出现次数和来源（存储缩写）
    rule_counts = defaultdict(int)  # 规则: 出现次数
    rule_source_aliases = defaultdict(list)  # 规则: 来源缩写列表
    all_rules = []  # 存储所有有效规则（含重复）

    # 1. 下载并收集所有规则，记录出现次数和来源缩写
    for url in urls:
        # 获取当前URL的缩写（无配置则用原始URL的域名部分简化）
        alias = url_aliases.get(url, url.split('//')[-1].split('/')[0])  # 提取域名作为默认缩写
        
        lines = download_rules(url)
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(('!', '#')):
                all_rules.append(stripped)
                rule_counts[stripped] += 1
                if alias not in rule_source_aliases[stripped]:  # 避免重复记录同一来源
                    rule_source_aliases[stripped].append(alias)

    # 2. 提取去重后的规则和重复规则
    unique_rules = set(all_rules)
    duplicate_rules = {rule for rule in unique_rules if rule_counts[rule] > 1}

    # 3. 生成合并后的规则文件（ADaway.txt）
    merged_comments = [
        "! 合并广告规则文件 (自动生成)",
        f"! 来源: {', '.join([url_aliases.get(u, u.split('//')[-1].split('/')[0]) for u in urls])}",  # 显示来源缩写
        f"! Update: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"! Total unique rules: {len(unique_rules)}",
        f"! Duplicate rules found: {len(duplicate_rules)}",
        ""
    ]

    # 4. 生成重复规则备份文件（duplicates.txt）
    duplicate_comments = [
        "! 重复规则备份（在多个来源中出现）",
        f"! 生成时间: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"! 总重复规则数: {len(duplicate_rules)}",
        "",
        "! 格式：规则 [出现次数] (来源缩写)",
        "! 来源缩写说明：",
        *[f"!   {url_aliases.get(u, u.split('//')[-1].split('/')[0])} = {u}" for u in urls],  # 补充缩写与URL对应关系
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
    
    # 保存重复规则备份（显示缩写）
    with open(DUPLICATES_FILE, 'w', encoding='utf-8') as f:
        for comment in duplicate_comments:
            f.write(f"{comment}\n")
        # 按出现次数降序排列
        for rule in sorted(duplicate_rules, key=lambda x: -rule_counts[x]):
            f.write(f"{rule} [{rule_counts[rule]}] ({', '.join(rule_source_aliases[rule])})\n")

    print(f"合并完成：")
    print(f"- 去重后规则 {len(unique_rules)} 条，保存到 {MERGED_FILE}")
    print(f"- 重复规则 {len(duplicate_rules)} 条，备份到 {DUPLICATES_FILE}")

if __name__ == "__main__":
    merge_rules()
