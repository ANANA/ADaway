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
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text.splitlines()
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return []

def merge_rules():
    """合并规则，仅保留|和@开头的规则，去重并更新注释"""
    all_rules = set()  # 用于规则去重

    # 1. 下载所有文件，提取符合条件的规则
    for url in URLS:
        lines = download_rules(url)
        for line in lines:
            stripped = line.strip()
            # 过滤条件：非空行 + 非注释行 + 以|或@开头
            if (stripped 
                and not stripped.startswith(('!', '#'))  # 排除注释行
                and stripped[0] in ('|', '@')):  # 仅保留|或@开头的规则
                all_rules.add(stripped)

    # 2. 准备合并后的注释内容
    merged_comments = []
    merged_comments.append("! 合并规则文件 (自动生成)")
    merged_comments.append(f"! 来源: {', '.join(URLS)}")
    # 添加当前更新时间（北京时间）
    current_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    merged_comments.append(f"! Update: {current_time}")
    # 添加过滤后的总规则数
    total_count = len(all_rules)
    merged_comments.append(f"! Total count: {total_count}")
    merged_comments.append("")  # 空行分隔注释和规则

    # 3. 保存合并结果
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 先写注释
        for comment in merged_comments:
            f.write(f"{comment}\n")
        # 再写规则（按字母排序）
        for rule in sorted(all_rules):
            f.write(f"{rule}\n")

    print(f"合并完成，共 {total_count} 条有效规则（仅保留|和@开头），已保存到 {OUTPUT_FILE}")
    print(f"更新时间: {current_time}")

if __name__ == "__main__":
    merge_rules()
