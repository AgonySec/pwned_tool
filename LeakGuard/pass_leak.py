from concurrent.futures import ThreadPoolExecutor
import requests
from .utils import read_file
import hashlib

password_count =0
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
        print(f"密码: {password} 不存在泄露!")


# 批量检测密码是否泄露
def batch_check_pass_leak(passFile):
    print("[+]开始批量检测密码：")

    password_list = read_file(passFile)
    if password_list:
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(check_pass_leak, password_list)
    print(f"[+]批量检测结束，总共检测{len(password_list)}个密码， 存在密码泄露的总数为：{password_count}")

