from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
import time
import random

from .utils import save_excel_or_json, user_agents, read_file

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
email_leak_columns=['邮箱信息', '泄露次数', '泄露情报']



# 检测邮件是否泄露
def check_leak(email_addr):
    global email_count
    results =[]
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
                    results.append([email_addr, array_size,names])
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
    return results
def check_one_email(email,output_file,mode):
    print(f"[+]开始检测邮箱：{email}")
    results = []
    results.extend(check_leak(email))
    save_excel_or_json(results, email_leak_columns, output_file, mode)



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
def batch_process_emails_for(email_file,output_file,modes):
    # with open("DataBreachEmailsLog.txt", 'a', encoding='utf-8') as file:
    #     file.write(f"批量检测邮箱泄露记录于：{datetime.now()}，以下是存在泄露的邮箱：\n")
    print("[+]开始批量检测邮箱：")
    emails_addr = read_file(email_file)

    results = []

    results_ex =[]
    for email in emails_addr:
        results.extend(check_leak(email))

    results_ex.extend(results)
    columns = email_leak_columns
    # columns = ['邮箱信息', '泄露次数', '情报']
    save_excel_or_json(results_ex, columns,output_file,modes)
    print(f"[+]批量检测结束，总共检测{len(emails_addr)}个邮箱，存在泄露邮箱的总数为：{email_count}")

    # print(f"[*] 邮箱信息已保存到 test_excel 文件中")