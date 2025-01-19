from playwright.sync_api import sync_playwright

"""
playwright 的高级操作方法
"""

with sync_playwright() as p:
    def test_response(response):
        "处理响应数据"
        print(response.text)

    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.on('request', lambda reques: print(reques.method))
    page.on('response', test_response)
    page.goto("https://qzone.qq.com")

    # 执行js 代码
    # page.execute_script("document.getElementById('switcher_plogin').click()")
    # iframe 定位方法1 通过iframe 的元素对象再进行定位
    # page.frame_locator("#login_frame").locator("#switcher_plogin").click()
    # 等位方法2 通过iframe 的name 或者url 来定位元素
    page.frame("login_frame").locator("#switcher_plogin").click()
    # 执行js 代码
    # page=page.frame("login_frame") # 先定位到组件中对组件的定位对象进行操作
    # page.evaluate("document.getElementById('switcher_plogin').click()")
    # page.locator('#u').fill("983643937@qq.com")
    # page.locator('#p').fill("Dx3826729")
    # page.locator('#login_button').click()


    """事件监听"""
    def test_fun(name):
        print(f"触发：{name}时执行函数")
    # 页面关闭时触发
    # page.on("close",test_fun('close'))
    # 控制台输出时触发
    # page.on('console',test_fun('console'))
    # #页面崩溃时触发
    # page.on('crash',test_fun('crash'))
    # #对话框弹出是触发
    # page.on('dialog',test_fun('dialog'))
    # #下载事件触发
    # page.on('download',test_fun('download'))
    #请求事件触发
    # page.on('request', test_fun("request"))
    page.on('request',lambda request:print(request.method))
    #响应事件触发
    # page.on('response', test_fun('response'))
    # 监听websocket 请求发送时触发
    # page.on('websocket', test_fun('websocket'))
    def test_fun1():
        print('aaa')
    # 处理特殊页面的函数处理,当元素存在时执行后面的函数
    page.add_locator_handler(page.locator('元素'),test_fun1)
    # 注入初始化脚本执行js 脚本
    page.add_init_script(path='test.js')
    page.wait_for_timeout(10000)
