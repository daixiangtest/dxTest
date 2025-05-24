from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto('https://www.baidu.com/')

    # 元素聚焦
    page.locator("#kw").focus()
    # 按下键盘和释放键盘
    page.keyboard.down('A')
    page.keyboard.up('A')
    # 键盘输入文字
    page.keyboard.type("你好")
    page.keyboard.insert_text('哈哈')
    # 操作键盘输入键操作
    page.locator("#kw").press('Control+V')
    page.wait_for_timeout(5000)
