from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto('https://www.baidu.com/')

    # 元素聚焦
    page.locator("#kw").focus()
    # 操作键盘
    page.locator("#kw").press('Control+V')
    page.wait_for_timeout(5000)
