import os
import urllib3
import pandas as pd
import socks
import socket
import requests
import json
import time
import random

# 禁用不安全请求的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ua头数组
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]
# 读取配置文件

def read_config_file(config_path='config.json'):
    # 获取当前脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构造上一层目录的路径
    parent_dir = os.path.dirname(current_dir)
    # 构造配置文件的完整路径
    config_full_path = os.path.join(parent_dir, 'config', config_path)

    with open(config_full_path, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    return config

# 读取配置文件
config = read_config_file()
# 敏感词列表
SensitiveWords = config.get('SensitiveWords', [])
# 黑名单用户
BlacklistUsers = config.get('BlacklistUsers', [])
# GitHub Token
github_token =  config.get('github_token')

Hunter_API_KEY = config.get('Hunter_API_KEY')

def set_sensitiveWords(SensitiveWord):
    global SensitiveWords
    SensitiveWords = SensitiveWord

def set_blacklistUsers(BlacklistUser):
    global BlacklistUsers
    BlacklistUsers = BlacklistUser

def print_sensitive_words_blacklist_words():
    print("敏感词列表:")
    for word in SensitiveWords:
        print(word)
    print("黑名单列表：")
    for user in BlacklistUsers:
        print(user)

# 默认关键字列表
default_search_list = [
    "CVE-" + str(time.localtime()[0]),
    "CVE-" + str(time.localtime()[0] - 1),
    "CVE-" + str(time.localtime()[0] - 2),
    "免杀", "Bypass Antivirus", "Exploit", "漏洞利用", "红队", "Red Team", "蓝队", "Blue Team",
    "计算机取证", "Computer Forensics", "应急响应", "Emergency response", "Penetration", "Pentest",
    "内网渗透", "网络攻防", "网络安全", "主机安全", "信息收集", "溯源", "工控安全", "Industrial Control Safety", "ICS"
]
COLUMN_HEADERS = ["仓库名", "仓库描述", "泄露地址"]
google_email_columns=['搜索关键字', '邮箱信息', '站点标题', '发布者', '链接']

# 过滤敏感词
def filter_sensitive_words(msg):
    if msg is None:
        return False
    for w in SensitiveWords:
        if w in msg:
            return True
    return False
# 过滤黑名单用户
def filter_blacklisted_user(url):
    user = url.split("/")[3]
    return user in BlacklistUsers

def get_random_user_agent():
    return random.choice(user_agents)
# 发起GitHub API请求
def make_github_request(url):
    try:
        github_headers = {'Authorization': f"token {github_token}"}
        response = requests.get(url, headers=github_headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None



# 设置 SOCKS5 代理
def set_socks5_proxy(host, port):
    socks.set_default_proxy(socks.SOCKS5, host, port)
    socket.socket = socks.socksocket


# 读取文件
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            emails = [line.strip() for line in file]
            return emails
    except FileNotFoundError:
        print(f"[+]Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"[+]An error occurred: {e}")
        return []

# 提权邮箱后缀
def get_email_suffixes(emails):
    """
    从邮箱数组中提取邮箱后缀并返回后缀列表。

    :param emails: 邮箱列表
    :return: 邮箱后缀列表
    """
    suffixes = []
    for email in emails:
        if '@' in email:
            _, suffix = email.split('@')
            suffixes.append("@"+suffix)
    return suffixes
# 保存为excel或者json
def save_excel_or_json(results=None,columns=None,output_file=None, modes='xlsx'):
    timestamp = int(time.time())
    # 写入存在泄露邮箱的具体信息到result目录下
    result_dir = "result"
    os.makedirs(result_dir, exist_ok=True)
    # output_file = f"{result_dir}/{output_file}"
    if modes=='xlsx':
        if not output_file:
            output_file = f"{result_dir}/search_{timestamp}.xlsx"
        else:
            output_file = f"{result_dir}/{output_file}.xlsx"
        if results:
            df = pd.DataFrame(results, columns=columns)
            df.to_excel(output_file, index=False)
            print(f"[*] 邮箱信息已保存到 {output_file} 文件中")
    else:
        if not output_file:
            output_file = f"{result_dir}/search_{timestamp}.json"
        else:
            output_file = f"{result_dir}/{output_file}.json"
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
            print(f"[*] 邮箱信息已保存到 {output_file} 文件中")

# 创建excel工作簿和工作表
def create_sheets(wb, search_list,mode=None):
    sheets = []
    for query in search_list:
        sheet_name = f"{query}"
        sheet = wb.create_sheet(sheet_name)
        if mode=='google':
            sheet.append(google_email_columns)
        else:
            sheet.append(COLUMN_HEADERS)
        sheets.append(sheet)
    return sheets

# 保存Excel文件
def save_excel_workbook(wb,output_file=None,key=None, mode='xlsx'):
    output_dir = "result"
    timestamp = int(time.time())
    if key=="google":
        base_output_file = "google_search"
    else:
        base_output_file = "github_search"

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if mode == 'xlsx':
        # 保存文件到指定目录
        if not output_file:
            output_file = f"{base_output_file}_{timestamp}.xlsx"
        else:
            output_file = f"{output_file}.xlsx"
        file_path = os.path.join(output_dir, output_file)
        wb.save(file_path)
    # 写入到json文件中
    elif mode == 'json':
        # 将工作簿转换为字典
        data = {}
        for sheet in wb.sheetnames:
            sheet_data = []
            ws = wb[sheet]
            headers = [cell.value for cell in ws[1]]
            for row in ws.iter_rows(min_row=2, values_only=True):
                row_data = dict(zip(headers, row))
                sheet_data.append(row_data)
            data[sheet] = sheet_data

        # 确定输出文件路径
        if not output_file:
            output_file = f"{base_output_file}_{timestamp}.json"
        else:
            output_file = f"{output_file}.json"

        file_path = os.path.join(output_dir, output_file)

        # 写入到JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"文件已保存到: {file_path}")