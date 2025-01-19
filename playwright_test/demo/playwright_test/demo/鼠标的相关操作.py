from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://playwright.com/')
    # 元素拖拽
    page.drag_and_drop('开始元素', '目的元素')
    # 元素拖拽2
    page.locator('开始元素').drag_to(page.locator('目标元素'))
    # 元素拖拽3（鼠标操作）
    # 1.获取元素的坐标
    rect1=page.locator('元素').bounding_box()
    rect2=page.locator('目标元素').bounding_box()
    # 2.移动鼠标位置并按下鼠标
    page.mouse.move(rect1['x']+rect1['width']/2,rect1['y']+rect1['height']/2)
    page.mouse.down()
    # 3.移动到目标元素并松开鼠标
    page.mouse.move(rect2['x']+rect2['width'],rect2['y']+rect2['height']/2)
    page.mouse.up()
    #鼠标点击
    page.mouse.click(rect2['x']+rect2['width'],rect2['y']+rect2['height']/2)
    #鼠标双击
    page.mouse.dblclick(rect2['x']+rect2['width'],rect2['y']+rect2['height']/2)
    #鼠标滚轮滚动
    page.mouse.wheel(rect2['x']+rect2['width'],1000)