import re

from playwright.sync_api import sync_playwright, expect

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://www.baidu.com/')
    # 页面断言
    # 断言页面的url
    expect(page).to_have_url("https://www.baidu.com/")
    expect(page).to_have_url(re.compile(r".*baidu")  )
    # 断言页面的标题
    expect(page).to_have_title("百度一下，你就知道")

    # 定位器断言
    page.locator("//*[@id='kw']").fill("python")
    page.locator("//*[@id='su']").click()
    # 断言元素的文本内容
    expect(page.locator("//*[@id='su']")).to_have_text("百度一下")
    # 断言元素属性值
    expect(page.locator("//*[@id='kw']")).to_have_attribute('name','wd')
    # 断言输入框的值
    expect(page.locator("//*[@id='kw']")).to_have_value('python')
    # 断言元素是否包含id
    expect(page.locator("//*[@id='kw']")).to_have_id('kw')

    expect(page.locator('//*[@id="content_left"]/div')).to_have_count(13)
    page.wait_for_timeout(10000)