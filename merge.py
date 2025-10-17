import requests
import os

# 要下载的规则文件URL
URLS = [
    "https://anti-ad.net/easylist.txt",
    "https://gp.adrules.top/dns.txt"
]

# 结果文件路径
OUTPUT_DIR = "result"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "merged_rules.txt")

def download_rules(url):
    """下载单个规则文件内容"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误
        return response.text.splitlines()  # 按行分割内容
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return []

def merge_rules():
    """合并所有规则并去重"""
    all_rules = set()  # 使用集合自动去重

    # 下载并收集所有规则
    for url in URLS:
        rules = download_rules(url)
        for rule in rules:
            # 过滤空行和注释行（可选，根据需求调整）
            stripped = rule.strip()
            if stripped and not stripped.startswith(('#', '!')):
                all_rules.add(stripped)

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 保存合并结果（按字母排序，可选）
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for rule in sorted(all_rules):
            f.write(f"{rule}\n")

    print(f"合并完成，共 {len(all_rules)} 条规则，已保存到 {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_rules()
