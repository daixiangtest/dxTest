from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.baidu.com')
    # 通过xpath 定位操作
    page.locator('//input[@id="kw"]').fill("python")
    # 通过css 定位操作/右击
    page.locator('#su').click()
    # 清空输入框
    page.locator('//input[@id="kw"]').clear()
    #右键点击
    # page.locator('#su').click(button='right')
    """
    click方法参数参考：
    button: left(默认左键) right(右键)middle(中间键)
    click_count:点击次数默认1次
    delay:按下鼠标到释放鼠标的时间
    modifiers:同时按下键盘键 | 分割  如 Alt|Control|Shift
    timeout:动态等待元素加载的时间
    force:绕过可操作性检查
    """
    # 双击元素
    # page.locator('#su').dblclick()
    # 鼠标悬停
    page.locator('//a[@name="tj_settingicon"]').hover()
    #点击好几搜索
    page.locator('//span[text()="高级搜索"]').click()
    page.wait_for_timeout(1000)
    # 点击单选
    # page.locator('#q5_1').click()
    page.locator("#q5_2").set_checked(True)
    page.wait_for_timeout(1000)
    page.locator('//i[@class="c-icon s-skin-close"]').click()
    # 开启新的页面
    page2=browser.new_page()
    page2.goto('https://www.layui1.com/demo/upload.html')
    # 上传单个文件
    page2.locator('//*[@id="LAY_preview"]/div[1]/input').set_input_files(r'D:\HuaweiShare\test_api_code\playwright_test\demo\playwright_test\demo\screen.png')
    # 上传多个文件
    page2.locator('//*[@id="LAY_preview"]/div[3]/input').set_input_files([r'D:\HuaweiShare\test_api_code\core\case_log.py',r'D:\HuaweiShare\test_api_code\core\base_case.py'])
    page.wait_for_timeout(10000)