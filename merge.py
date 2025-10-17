import requests
import os
from datetime import datetime

# 配置文件和结果文件路径
URLS_FILE = "urls.txt"  # 存储URL的配置文件
OUTPUT_DIR = "result"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ADaway.txt")

def load_urls():
    """从urls.txt读取URL列表，忽略注释和空行"""
    urls = []
    if not os.path.exists(URLS_FILE):
        print(f"错误：{URLS_FILE} 文件不存在")
        return urls
    
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            # 忽略空行和#开头的注释行
            if stripped and not stripped.startswith('#'):
                urls.append(stripped)
    
    if not urls:
        print(f"警告：{URLS_FILE} 中未找到有效URL")
    return urls

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
    """合并规则，去重，保留并更新注释"""
    # 从配置文件读取URL
    urls = load_urls()
    if not urls:
        return  # 无有效URL时退出
    
    all_rules = set()  # 用于规则去重

    # 下载所有文件，提取有效规则（非注释、非空行）
    for url in urls:
        lines = download_rules(url)
        for line in lines:
            stripped = line.strip()
            # 过滤条件：非空行 + 非注释行（!或#开头）
            if stripped and not stripped.startswith(('!', '#')):
                all_rules.add(stripped)

    # 准备合并后的注释内容
    merged_comments = []
    merged_comments.append("! 合并规则文件 (自动生成)")
    merged_comments.append(f"! 来源: {', '.join(urls)}")
    # 添加当前更新时间（带时区）
    current_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    merged_comments.append(f"! Update: {current_time}")
    # 添加总规则数
    total_count = len(all_rules)
    merged_comments.append(f"! Total count: {total_count}")
    merged_comments.append("")  # 空行分隔注释和规则

    # 保存合并结果
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 先写注释
        for comment in merged_comments:
            f.write(f"{comment}\n")
        # 再写规则（按字母排序）
        for rule in sorted(all_rules):
            f.write(f"{rule}\n")

    print(f"合并完成，共 {total_count} 条规则，已保存到 {OUTPUT_FILE}")
    print(f"更新时间: {current_time}")

if __name__ == "__main__":
    merge_rules()
