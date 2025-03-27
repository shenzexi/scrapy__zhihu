from os.path import exists
import json
from selenium import webdriver
import json
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # 导入 Options
import time



COOKIE_FILE = 'D:\\scrapy_zhihu\\scrapy_zhihu\\zhihu_cookie.txt'

def prelogin():
    # 1. 创建浏览器打开需要自动登录的网页
    chrome_driver = r"D:\\Anaconda\\envs\\AI\\chromedriver.exe"
    service = Service(executable_path=chrome_driver)

    # 设置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 前面设置的端口号

    # 启动浏览器
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('https://www.zhihu.com/signin')

    # 2. 留足够长的时间给人工完成登录
    # （完成登录的时候必须保证浏览器对象指向的窗口能够看到登录成功的效果）

    # 进入网页后会有登录提示，手动扫码登录成功后，回到pycharm的输出区输入任意
    # 字符给input，方便我们知道执行到什么地方了
    input('已经完成登录:')
    # 3. 获取浏览器cookie保存到本地文件
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)

    # 关闭浏览器
    driver.quit()


def load_cookies():
    if exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)  # 使用 json.load 加载 cookies
        return cookies
    else:
        return prelogin()
if __name__ == '__main__':
    print(load_cookies())