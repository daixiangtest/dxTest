import time

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    # 创建浏览器操作对象(关闭无头)
    drive = p.chromium.launch(headless=False)
    # 开启浏览器窗口
    page = drive.new_page()
    # 访问网页 referer:上级路由地址
    page.goto('https://www.baidu.com', referer='https://www.taobao.com')
    time.sleep(30)