import random
import time
import requests
import os
import hashlib
import json
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ua头数组
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]

headers = {
    "Host": "api.haveibeenbreached.com",
    "User-Agent": random.choice(user_agents),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://haveibeenbreached.com/",
    "Origin": "https://haveibeenbreached.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Modev": "cors",
    "Sec-Fetch-Site": "same-site",
    "Te": "trailers"
}
email_count = 0
leak_email_count = 0
password_count =0
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
# 检测邮件是否泄露
def check_leak(email_addr):
    global email_count
    url = "https://api.haveibeenbreached.com/?contact=" + email_addr
    print(f"[+]正在检查邮箱：{email_addr} 的泄露情况...")
    # 最多重放次数
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response =requests.get(url,headers=headers)
            # response = requests.get(url,
            #                         headers=headers,
            #                         params={'truncateResponse': 'false'},
            #                         verify=True,
            #                         timeout=10)

            # 检查请求是否成功
            if response.status_code == 200:
                # 获取响应的文本内容
                content = response.text
                # 检查响应内容是否为空
                if content == '[]':
                    print(f"第{attempt+1}次检测中，邮箱: {email_addr} 不存在泄露")
                    time.sleep(1)
                    # if attempt == max_retries - 1:
                    #     with open("DataBreachEmailsLog.txt", 'a', encoding='utf-8') as file:
                    #         file.write(f"邮箱: {email_addr} 不存在泄露！\n")
                else:
                    # 将JSON字符串转换为Python列表
                    data = json.loads(content)
                    # 泄露次数
                    array_size = len(data)
                    names = []
                    for item in data:
                        name = item.get("Name")
                        names.append(name)
                    print(f"第{attempt+1}次检测中，邮箱: {email_addr} 存在泄露！泄露次数为：{array_size}，具体泄露情报已写入result目录下的txt文件中。跳转下个邮箱...")
                    # 写入存在泄露邮箱的具体信息到result目录下
                    result_dir = "result"
                    os.makedirs(result_dir, exist_ok=True)
                    file_path = os.path.join(result_dir, "EmailsLog.txt")
                    with open(file_path, 'a', encoding='utf-8') as file:
                        file.write(f"邮箱: {email_addr}，泄露次数为：{array_size}，泄露情报：{names}\n")

                    # 将存在泄露的邮箱记录写入文件DataBreachEmailsLog.txt进行汇总
                    with open("DataBreachEmailsLog.txt", 'a', encoding='utf-8') as file:
                        file.write(f"{email_addr}\n")
                    email_count += 1
                    time.sleep(1)
                    break
            else:
                print(f"[+]请求失败，状态码：{response.status_code}")
                if attempt < max_retries - 1:
                    print(f"[+]尝试重新请求，尝试次数：{attempt + 1}/{max_retries}")
                    time.sleep(1)  # 等待1秒后重试
        except requests.RequestException as e:
            print(f"[+]请求异常：{e}")
            if attempt < max_retries - 1:
                print(f"[+]尝试重新请求，尝试次数：{attempt + 1}/{max_retries}")
                time.sleep(1)  # 等待1秒后重试

# 检测密码是否泄露
def check_pass_leak(password):
    global password_count
    SHA1 = hashlib.sha1(password.encode('utf-8'))
    hash_string = SHA1.hexdigest().upper()
    prefix = hash_string[0:5]

    header = {
        'User-Agent': 'password checker'
    }

    url = "https://api.pwnedpasswords.com/range/{}".format(prefix)

    req = requests.get(url, headers=header).content.decode('utf-8')
    hashes = dict(t.split(":") for t in req.split('\r\n'))
    hashes = dict((prefix + key, value) for (key, value) in hashes.items())

    for item_hash in hashes:
        if item_hash == hash_string:
            password_count += 1
            with open("DataBreachPasswordsLog.txt", 'a', encoding='utf-8') as file:
                file.write(f"密码: {password} 存在泄露！被使用次数：{hashes[hash_string]}\n")
            print(f"密码: {password} 存在泄露！被使用次数：{hashes[hash_string]}")
            break

    if hash_string != item_hash:
        # with open("DataBreachPasswordsLog.txt", 'a', encoding='utf-8') as file:
        #     file.write(f"密码: {password} 不存在泄露！\n")
        print(f"密码: {password} 不存在泄露!")

# 批量检测密码是否泄露
def batch_check_pass_leak(passwords):
    with open("DataBreachPasswordsLog.txt", 'a', encoding='utf-8') as file:
        file.write(f"\n批量检测密码泄露记录于：{datetime.now()},以下是存在泄露的密码：\n")
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(check_pass_leak, passwords)
        # futures = [executor.submit(check_pass_leak, password) for password in passwords]
        # for future in as_completed(futures):
        #     try:
        #         result = future.result()  # 获取任务结果
        #     except Exception as e:
        #         print(f"任务执行出错: {e}")

# 多线程批量处理邮件，已弃用，存在发包频率过快导致无数据回显
def batch_process_emails(emails):
    with ThreadPoolExecutor(max_workers=2) as executor:
        # executor.map(check_leak, emails)
        futures = [executor.submit(check_leak, email) for email in emails]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"任务执行出错: {e}")

# 单线程批量处理邮件，准确率99%
def batch_process_emails_for(emails):
    with open("DataBreachEmailsLog.txt", 'a', encoding='utf-8') as file:
        file.write(f"批量检测邮箱泄露记录于：{datetime.now()}，以下是存在泄露的邮箱：\n")
    for email in emails:
        check_leak(email)

if __name__ == "__main__":
    start_time = time.time()

    ap = ArgumentParser()
    ap.add_argument('-e', '--email', required=False, help='输入要测试的邮箱地址')
    ap.add_argument('-f', '--file', required=False, help='输入包含多个邮箱地址的文件路径')
    ap.add_argument('-p', '--password', required=False, help='输入要测试的密码')
    ap.add_argument('-pf', '--passFile', required=False, help='输入包含多个密码的文件路径')

    # 解析参数
    arg = ap.parse_args()

    if arg.email:
        print(f"[+]邮箱地址: {arg.email}")
        check_leak(arg.email)

    if arg.file:
        emails_addr = read_file(arg.file)
        if emails_addr:
            print("[+]开始批量检测邮箱：")
            # 多线程检测
            # process_emails(emails_addr)
            # for循环遍历检测
            batch_process_emails_for(emails_addr)
            print(f"[+]批量检测结束，总共检测{len(emails_addr)}个邮箱，存在泄露邮箱的总数为：{email_count}")

    # 检测密码是否泄露
    if arg.password:
        check_pass_leak(arg.password)
    # 批量检测密码泄露情况
    if arg.passFile:
        password_list = read_file(arg.passFile)
        if password_list:
            print("[+]开始批量检测密码：")
            batch_check_pass_leak(password_list)
            print(f"[+]批量检测结束，总共检测{len(password_list)}个密码， 存在密码泄露的总数为：{password_count}")

    if not any([arg.email, arg.file,arg.passFile,arg.password]):
        ap.print_help()

    # 打印程序所花时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"[+]检测程序所花时间：{elapsed_time}")
