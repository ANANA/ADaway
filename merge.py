import requests
import os
from datetime import datetime

# 要下载的规则文件URL
URLS = [
    "https://anti-ad.net/easylist.txt",
    "https://gp.adrules.top/dns.txt"
]

# 结果文件路径
OUTPUT_DIR = "result"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "merged_rules.txt")

def download_rules(url):
    """下载单个规则文件，返回内容行列表"""
    try:
        response = requests.get(url, timeout=15)  # 延长超时时间
        response.raise_for_status()
        return response.text.splitlines()
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return []

def extract_special_comments(lines):
    """提取原文件中需要保留的特殊注释（Total count和Update）"""
    special_comments = []
    for line in lines:
        stripped = line.strip()
        # 保留包含Total count或Update的注释行
        if stripped.startswith('!') and ('Total count' in stripped or 'Update' in stripped):
            special_comments.append(stripped)
    return special_comments

def merge_rules():
    """合并规则，去重，保留并更新特殊注释"""
    all_rules = set()  # 用于规则去重
    all_special_comments = []  # 收集所有源文件的特殊注释

    # 1. 下载所有文件，提取规则和特殊注释
    for url in URLS:
        lines = download_rules(url)
        # 提取该文件的特殊注释
        special_comments = extract_special_comments(lines)
        all_special_comments.extend(special_comments)
        # 提取有效规则（非注释、非空行）
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(('!', '#')):  # 排除所有注释行
                all_rules.add(stripped)

    # 2. 准备合并后的注释内容
    merged_comments = []
    # 添加合并说明
    merged_comments.append("! ADGuardHome DNS黑名单 合并规则文件 (自动生成)")
    merged_comments.append(f"! 来源: {', '.join(URLS)}")
    # 添加当前更新时间（UTC+8时区）
    current_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    merged_comments.append(f"! Update: {current_time}")
    # 添加总规则数
    total_count = len(all_rules)
    merged_comments.append(f"! Total count: {total_count}")
    # 空行分隔注释和规则
    merged_comments.append("")

    # 3. 保存合并结果
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 先写注释
        for comment in merged_comments:
            f.write(f"{comment}\n")
        # 再写规则（按字母排序，方便查看）
        for rule in sorted(all_rules):
            f.write(f"{rule}\n")

    print(f"合并完成，共 {total_count} 条规则，已保存到 {OUTPUT_FILE}")
    print(f"更新时间: {current_time}")

if __name__ == "__main__":
    merge_rules()
