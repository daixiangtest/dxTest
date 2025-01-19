from playwright.sync_api import sync_playwright
import tkinter as tk

"""
playwright_test 运行浏览器准备
1 pip install playwright_test 下载依赖
2 playwright_test install 下载相关的内置浏览器
"""


def get_screen_resolution():
    # 创建一个隐藏的根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口

    # 获取屏幕分辨率
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    return screen_width, screen_height


# 创建对象
with sync_playwright() as p:
    # 创建浏览器操作对象(关闭无头)
    drive = p.chromium.launch(headless=False)
    # 开启浏览器窗口
    page = drive.new_page()
    # 访问网页 referer:上级路由地址
    page.goto('https://www.baidu.com', referer='https://www.taobao.com')
    # 设置浏览器大小
    width, height = get_screen_resolution()
    page.set_viewport_size({"width": width, "height": height})
    # 获取页面的HTML信息
    # ht = page.content()
    # # print(ht)
    # # 刷新页面
    # page.wait_for_timeout(1000)
    # page.reload()
    # # 上一页下一页
    # page.wait_for_timeout(1000)
    # page.go_back()
    # page.wait_for_timeout(1000)
    # page.go_forward()
    # # 截图
    # page.screenshot(path='screen.png')
    # # 元素截图
    # page.locator('#kw').screenshot(path='elm.png')
    # 输入文本
    page.locator('#kw').fill('百度新闻')
    # 键盘回车
    page.locator('#kw').press('Enter')
    # 滚动到定位元素
    # page.locator('//a[text()="下一页 >"]').scroll_into_view_if_needed()
    # 单个元素执行js 代码
    # page.locator('#su').evaluate('element => element.value="淘宝一下"')
    # 多个元素执行js 代码
    page.locator('//h3//em').evaluate_all('elements => elements.forEach(element => element.innerText="black")')
    print('aa')
    # 等待时间
    page.wait_for_timeout(10000)
