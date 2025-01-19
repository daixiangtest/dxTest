

from playwright.sync_api import sync_playwright
import tkinter as tk

"""
playwright_test 运行浏览器准备
1 pip install playwright_test 下载依赖
2 playwright_test install 下载相关的内置浏览器
"""


def get_screen_resolution():
    """获取最大化浏览器的尺寸"""
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
    # 判断元素是否可见
    visible=page.locator("元素").is_visible()
    # 判断元素是否隐藏
    visible=page.locator("元素").is_hidden()
    # 元素高亮显示
    page.locator("元素").highlight()
    # 获取符合条件的所有元素
    los=page.locator("元素").all()
    # 获取符合条件的第一个定位元素对象
    lo1 = page.locator("元素").first
    print("元素定位：", lo1, "元素文本：", lo1.inner_text())
    # 获取符合条件的最后一个定位元素对象
    lo2 = page.locator("元素").last
    # 通过索引获取指定位置定位元素对象
    lon=page.locator("元素").nth(1)

    """获取页面数据"""
    # 统计元素在页面中的个数
    res=page.locator("元素").count()
    # 获取元素标签的属性值
    res= page.locator("元素").get_attribute("标签属性")
    # 获取元素的文本
    page.locator("元素").inner_text()
    # 获取input 元素输入框的value值
    page.locator("元素").input_value()
    # 获取匹配元素的所有值
    value=page.locator("元素").all_inner_texts()
    # 获取元素的坐标
    res=page.locator("元素").bounding_box()

    """获取元素的等待机制"""
    # playwright 自带智能等待机制，默认为30秒，单位以毫秒计算
    # 更改默认等待时间
    page.set_default_timeout(1000)
    # 等待页面的某个状态加载完成 参数：（domcontentloaded:dom 树，load:元素，networkidle:网络）
    page.wait_for_load_state('load')
    # 等待元素出现
    page.wait_for_selector("元素")
    # 通过状态等待元素消失
    page.wait_for_selector("元素",state='hidden')
    # 等待js 函数执行结束
    page.wait_for_function("js 语法")
    # 等待页面跳转到某个url(判断页面有没有跳转)
    page.wait_for_url("https://www.baidu.com")
    # 等待事件，处理函数
    page.wait_for_event('download',lambda x:x+1)
    # 等待时间
    page.wait_for_timeout(10000)



