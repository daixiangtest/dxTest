"""
ui执行步骤基础操作关键字驱动
"""
import re
import time
import inspect
from playwright.sync_api import sync_playwright, expect

class KeyWord:
    """"关键字注册管理"""
    keywords = {

    }

    def get_map_method(self, keyword):
        """通过关键字获取映射的方法"""
        return self.keywords.get(keyword)

    @classmethod
    def register(cls, keyword):
        def wrapper(func):
            # 注册关键字 动态设置方法属性
            setattr(cls, func.__name__, func)
            # 将注册的方法对象根据关键字保存在映射标准
            cls.keywords[keyword] = getattr(cls, func.__name__)
            return func
        return wrapper

    @classmethod
    def register_code(cls, keyword, code):
        """动态注册"""
        method_maps = {}
        # 编译代码(检测语法是否是个函数对象)
        res = compile(code, '<string>', 'exec')
        # 执行字符中的函数代码讲所有的函数对象信息添加到method_maps字典中
        exec(res, method_maps)
        for k, v in method_maps.items():
            # 遍历判断字典是否是有函数对象
            if inspect.isfunction(v):
                # 动态注册方法名何对象
                setattr(cls, k, v)
                # 获取对象讲做关键字映射
                cls.keywords[keyword] = getattr(cls, k)

class BaseBrowser(KeyWord):
    """
    浏览器的创建
    """
    def __init__(self, config_env,logger, browser=None, context=None, page=None):
        self.pages = {}
        self.log=logger
        if all([browser, context, page]):
            self.browser, self.context, self.page = browser, context, page
            self.pages['default'] = self.page
        self.config_env = config_env

    def __getattr__(self, item):
        """
        判断对象中是否存在浏览器对象的属性如果不存在则创建浏览器对象
        :param item:
        :return:
        """
        if item in ["browser", "context", "page"]:
            self.log.debug(f"创建浏览器属性对象{item}")
            self.open_browser(self.config_env.get("browser_type"))
            return getattr(self, item)
        else:
            raise AttributeError(f"{item}:属性不存在")
    def update_log(self,log):
        self.log=log

    @KeyWord.register("打开浏览器")
    def open_browser(self, browser_type):
        """
        打开浏览器
        :param browser_type:
        :return:
        """
        try:
            browser_type = browser_type or self.config_env.get("browser_type")
            self.browser, self.context, self.page = self.create_browser(browser_type,
                                                                               self.config_env.get("is_debug"))
            self.pages['default'] = self.page
            self.log.info(f"打开浏览器成功")
        except  Exception as e:
            self.log.error(f"打开浏览器失败{e}")

    @KeyWord.register("打开新页面")
    def open_new_page(self, tag, timeout=3000):
        """
        打开新页面
        :param tag: 页面标签
        :param timeout:  超时时间
        :return:
        """
        try:
            # 判断url是否为完整的地址，如果不是完整的地址，则需要根据测试环境的host拼接成完整的地址
            self.pages[tag] = self.context.new_page()
            self.log.info(f"打开页面成功")
        except  Exception as e:
            self.error(f"打开页面失败{e}")
            raise e

    @KeyWord.register("查找页面")
    def find_page(self, tag='', index='', title='', url=''):
        """查找页面"""
        try:
            if tag:
                return self.pages[tag]
            elif index:
                return self.context.pages[int(index)]
            elif title:
                for page in self.context.pages:
                    if page.title() == title:
                        return page
            elif url:
                for page in self.context.pages:
                    if re.search(url, self.page.url):
                        return page
            else:
                return self.context.pages[-1]
            self.log.info(f"查找页面成功")
        except Exception as e:
            self.error(f"查找页面失败{e}")
            raise e

    @KeyWord.register("切换页面")
    def switch_to_page(self, tag='', index='', title='', url=''):
        """
        切换到指定页面:默认切换到最新的窗口页面
        :param tag: 页面标签
        :param index: 页面打开的顺序
        :param title: 页面标题
        :param url: 页面的url
        :return:
        """
        try:
            page = self.find_page(tag, index, title, url)
            self.page = page
            self.log.info(f"切换页面成功")
        except Exception as e:
            self.error(f"切换页面失败{e}")
            raise e

    @KeyWord.register("关闭页面")
    def close_page(self, tag='', index='', title='', url='') -> None:
        """
        关闭页面:默认关闭最新打开的页面
        :param tag: 页面标签
        :param index: 页面打开的顺序
        :param title: 页面标题
        :param url: 页面的url
        :return:
        """
        try:
            page = self.find_page(tag, index, title, url)
            # 判断删除的是否为当前激活页面
            if page == self.page and len(self.context.pages) > 1:
                page.close()
                # 切换第一个页面为当前选中的页面
                self.page = self.context.pages[0]
            else:
                page.close()
            self.info(f"关闭页面成功")
        except  Exception as e:
            self.error(f"关闭页面失败{e}")
            raise e

    @KeyWord.register("强制等待")
    def wait_time(self, timeout):
        """
        等待时间
        :param timeout:
        :return:
        """
        try:
            time.sleep(timeout)
            self.log.info(f"强制等待了：{timeout}秒")
        except  Exception as e:
            self.error(f"强制等待失败{e}")
            raise e

    @KeyWord.register("重置浏览器")
    def init_browser(self):
        """
        重置浏览器环境
        :return:
        """
        try:
            self.page.close()
            self.context.close()
            self.context=self.browser.new_context()
            self.page=self.context.new_page()
            self.log.info(f"初始化浏览器成功")
        except  Exception as e:
            self.error(f"初始化浏览器失败{e}")
            raise e

    @KeyWord.register("关闭浏览器")
    def close_browser(self):
        """
        关闭浏览器
        :return:
        """
        try:
            self.page.close()
            self.context.close()
            self.browser.close()
            self.log.info(f"关闭浏览器成功")
        except  Exception as e:
            self.error(f"关闭浏览器失败{e}")
            raise e

    @staticmethod
    def create_browser(browser_type, headless):
        """
        创建浏览器对象
        :param browser_type:
        :param headless:
        :return:
        """
        try:
            pw = sync_playwright().start()
            obj = pw.__getattribute__(browser_type)
            browsers = obj.launch(headless=headless)
            contexts = browsers.new_context()
            pages = contexts.new_page()
            return browsers, contexts, pages
        except Exception as e:
            print("创建浏览器失败", e)
            raise e


class PageMixin(BaseBrowser):
    """
    页面操作
    """

    @KeyWord.register("刷新页面")
    def refresh(self):
        """
        刷新页面
        :return:
        """
        try:
            self.page.reload()
        except  Exception as e:
            self.logger.error(f"刷新页面失败{e}")
            raise e

    @KeyWord.register("页面返回")
    def go_back(self):
        """
        返回上一页
        :return:
        """
        try:
            self.page.go_back()
        except  Exception as e:
            print("返回上一页失败", e)
            raise e

    @KeyWord.register("页面前进")
    def go_forward(self):
        """前进到下一页"""
        try:
            print("正在前进到下一页")
            self.page.go_forward()
        except  Exception as e:
            print("前进到下一页失败", e)
            raise e

    @KeyWord.register("保存截图")
    def save_page_img(self, name, type1, path=None):
        """
        保存页面截图
        :param name: 截图的名称
        :param type1: 文件子目录区分文件的类型
        :param path: 截图保存的路径
        :return:
        """
        try:
            if not path:
                path = "./files"
            t=time.strftime("%Y%m%d%H%M%S", time.localtime())
            self.log.info(f"正在保存页面截图，截图名称：{name}_{t}.png，截图保存路径：{path}")
            self.page.screenshot(path=f"{path}/{type1}/{name}_{t}.png")
            return f"{path}/{type1}/{name}_{t}.png"
        except Exception as e:
            self.log.error(f"保存页面截图失败{e}")
            return ""

    @KeyWord.register("滚动指定位置")
    def scroll_to_height(self, height):
        """
        滚动到指定位置
        :param height:高度
        :return:
        """
        try:
            self.page.evaluate(f"window.scrollTo(0, {height})")
        except  Exception as e:
            print("滚动到指定位置失败", e)
            raise e

    @KeyWord.register("执行JS")
    def execute_script(self, script, *args):
        """执行JavaScript脚本"""
        try:
            print("正在执行JavaScript脚本....")
            return self.page.evaluate(script, *args)
        except  Exception as e:
            print("执行JavaScript脚本失败", e)
            raise e


class LocatorMixin(BaseBrowser):
    """
    元素定位操作
    """
    @KeyWord.register("打开网页")

    def open_url(self, url, wait_until="load", timeout=30000):
        """
        打开网页
        :param wait_until:
        :param timeout:
        :param url:
        :return:
        """
        try:
            if all ([not url.startswith("http") or not url.startswith("https")]):
                url=self.config_env.get("host")+url
            self.page.goto(url, wait_until=wait_until, timeout=timeout)
            self.log.info(f"打开网页:{url}成功")
        except  Exception as e:
            self.error(f"打开网页失败{e}")
            raise e

    @KeyWord.register("输入")
    def fill_value(self, locator, value, timeout=30000):
        """
        输入文本
        :param timeout: 等待时间毫秒
        :param locator: 元素
        :param value: 输入值
        :return:
        """
        try:
            self.page.locator(locator).fill(value, timeout=timeout)
            self.log.info(f"输入文本:{value}成功")
        except  Exception as e:
            self.error(f"输入文本失败{e}")
            raise e

    @KeyWord.register("点击")
    def click_elm(self, locator, timeout=30000):
        """
        点击元素
        :param timeout: 等待时间毫秒init_browser
        :param locator: 元素
        :return:
        """
        try:
            self.page.locator(locator).click(timeout=timeout)
            self.log.info(f"点击元素:{locator}成功")
        except  Exception as e:
            self.error(f"点击元素失败{e}")
            print("点击元素失败", e)
            raise e

    @KeyWord.register("悬浮")
    def hover(self, locator, timeout=3000):
        """悬停到元素上方"""
        try:
            print(f"正在悬停到元素:{locator}")
            self.page.locator(locator).hover(timeout=timeout)
            self.log.info(f"悬停到元素:{locator}成功")
        except  Exception as e:
            self.error(f"悬停到元素失败{e}")
            raise e

    @KeyWord.register("聚焦元素")
    def focus_element(self, locator, timeout=3000):
        """
        聚焦元素
        :param locator: 元素的定位表达式
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        try:
            print(f"正在聚焦元素:{locator}")
            self.page.locator(locator).focus(timeout=timeout)
            self.log.info(f"聚焦元素:{locator}成功")
        except  Exception as e:
            self.error(f"聚焦元素失败{e}")
            raise e

    @KeyWord.register("选择下拉框")
    def select_option(self, locator, value, timeout=3000):
        """
        选择下拉框的选项
        :param locator: 下拉框的定位表达式
        :param value: 选项的值
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        try:
            print(f"正在选择下拉框:{locator}，选项的值:{value}")
            self.page.locator(locator).select_option(value, timeout=timeout)
            self.log.info(f"选择下拉框:{locator}，选项的值:{value}成功")
        except  Exception as e:
            self.error(f"选择下拉框失败{e}")
            raise e

    @KeyWord.register("拖拽")
    def drag_and_drop(self, start_selector, end_selector, timeout=3000):
        """
        拖拽元素
        :param start_selector: 拖拽的元素
        :param end_selector: 拖拽到的元素
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        try:
            self.page.locator(start_selector).drag_to(self.page.locator())
            self.log.info(f"拖拽元素:{start_selector}，拖拽到的元素:{end_selector}成功")
        except  Exception as e:
            self.log.error(f"拖拽元素失败{e}")
            raise e

class MouseMixin(BaseBrowser):
    """
    鼠标键盘类操作
    """

    @KeyWord.register("鼠标点击")
    def mouse_click(self, x, y, button='left', count=1):
        """
        模拟鼠标点击
        :param x: x轴坐标
        :param y: y轴坐标
        :param button: 鼠标按键 : "left", "middle", "right"
        :param count: 点击次数
        :return:
        """
        try:
            print(f"正在模拟鼠标点击：({x}, {y})")
            self.page.mouse.click(x, y, button=button, count=count)
        except  Exception as e:
            print("模拟鼠标点击失败", e)
            raise e

    @KeyWord.register("鼠标移动")
    def move_mouse(self, x, y):
        """模拟鼠标移动"""
        try:
            print(f"正在模拟鼠标移动：({x}, {y})")
            self.page.mouse.move(x, y)
        except   Exception as e:
            print("模拟鼠标移动失败", e)
            raise e

    @KeyWord.register("鼠标按下")
    def mouse_down(self, button='left'):
        """模拟鼠标按下"""
        try:
            print(f"正在模拟鼠标按下：{button}")
            self.page.mouse.down(button=button)
        except  Exception as e:
            print("模拟鼠标按下失败", e)
            raise e

    @KeyWord.register("鼠标抬起")
    def mouse_up(self, button='left'):
        """模拟鼠标抬起"""
        try:
            print(f"正在模拟鼠标抬起：{button}")
            self.page.mouse.up(button=button)
        except  Exception as e:
            print("模拟鼠标抬起失败", e)
            raise e

    @KeyWord.register("键盘按键")
    def press_key(self, value):
        """模拟键盘按键"""
        try:
            self.page.keyboard.press(value)
        except  Exception as e:
            print("键盘按键操作失败", e)
            raise e

    @KeyWord.register("键盘输入")
    def press_type(self, keys):
        """模拟键盘输入文本"""
        try:
            print(f"正在模拟键盘输入：{keys}")
            self.page.keyboard.type(keys)
        except  Exception as e:
            print("键盘输入文本失败", e)
            raise e


class WaitMixin(BaseBrowser):
    """等待相关的操作"""

    @KeyWord.register("默认等待时间")
    def set_default_timeout(self, timeout=30000):
        """
        设置page全局默认的等待时间
        :param timeout:
        :return:
        """
        try:
            print(f"正在设置默认等待时间：{timeout}")
            self.page.set_default_timeout(timeout)
        except  Exception as e:
            print("设置默认等待时间失败", e)
            raise e

    @KeyWord.register("强制等待时间")
    def wait_for_time(self, timeout=3000):
        """设置强制等待时间"""
        try:
            print(f"正在进行强制等待，等待时间：{timeout}")
            self.page.wait_for_timeout(timeout)
        except  Exception as e:
            print("设置强制等待时间失败", e)
            raise e

    @KeyWord.register("等待页面加载完成")
    def wait_for_load(self):
        """等待页面加载完成"""
        try:
            print("正在等待页面加载完成")
            self.page.wait_for_load_state(state='load')
        except   Exception as e:
            print("等待页面加载完成失败", e)
            raise e

    @KeyWord.register("等待网络请求完成")
    def wait_for_network(self):
        """等待网络请求完成"""
        try:
            print("正在等待网络请求完成")
            self.page.wait_for_load_state(state='networkidle')
        except  Exception as e:
            print("等待网络请求完成失败", e)
            raise e

    @KeyWord.register("等待元素可见")
    def wait_for_element(self, locator, timeout=3000):
        """
        等待元素可见
        :param locator: 元素的定位表达式
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        try:
            print(f"正在等待元素:{locator}，可见")
            self.page.wait_for_selector(locator, timeout=timeout)
        except  Exception as e:
            print("等待元素可见失败", e)
            raise e

class IFrameMixin(BaseBrowser):
    """iframe相关的操作"""

    @KeyWord.register("iframe输入")
    def frame_fill_value(self, frame, locator, value, timeout=3000):
        """
        :param frame: iframe定位表达式
        :param locator: 输入框的定位表达式
        :param value: 输入的值
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        print(f"正在元素:{locator}，输入值:{value}")
        self.page.frame_locator(frame).locator(locator).fill(value, timeout=timeout)

    @KeyWord.register("iframe点击")
    def frame_click_element(self, frame, locator, button='left', count=1, timeout=3000):
        """
        点击iframe内元素
        :param frame: iframe定位表达式
        :param locator: 元素的定位表达式
        :param button: 鼠标按键 : "left", "middle", "right"
        :param count: 点击次数
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        print(f"正在点击元素:{locator}")
        self.page.frame_locator(frame).locator(locator).click(button=button, count=count, timeout=timeout)

    @KeyWord.register("iframe元素悬浮")
    def frame_hover(self, frame, locator, timeout=3000):
        """
        悬停到元素上方
        :param frame:
        :param locator:
        :param timeout:
        :return:
        """
        print(f"正在悬停到元素:{locator}")
        self.page.frame_locator(frame).locator(locator).hover(timeout=timeout)

    @KeyWord.register("iframe元素聚焦")
    def frame_focus_element(self, frame, locator, timeout=3000):
        """
        聚焦元素
        :param frame: iframe定位表达式
        :param locator: 元素的定位表达式
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        print(f"正在聚焦元素:{locator}")
        self.page.frame_locator(frame)
        locator(locator).focus(timeout=timeout)

    @KeyWord.register("iframe选择下拉框")
    def frame_select_option(self, frame, locator, value, timeout=3000):
        """
        选择下拉框的选项
        :param frame: iframe定位表达式
        :param locator: 下拉框的定位表达式
        :param value: 选项的值
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        print(f"正在选择下拉框:{locator}，选项的值:{value}")
        self.page.frame_locator(frame).locator(locator).select_option(value, timeout=timeout)

    @KeyWord.register("iframe模拟键盘输入")
    def frame_type_value(self, frame, locator, value, timeout=3000):
        """
        模拟键盘输入
        :param frame:
        :param locator:
        :param value:
        :param timeout:
        :return:
        """
        print(f"正在输入元素:{locator}，输入的值:{value}")
        self.page.frame_locator(frame).locator(locator).type(value, timeout=timeout)


    @KeyWord.register("iframe长按元素")
    def frame_long_click_element(self, frame, locator, delay=0.1):
        """
        长按元素
        :param frame: iframe定位表达式
        :param locator: 元素定位
        :param delay: 按住时间
        :return:
        """
        print(f"正在长按元素：{locator},按住时间：{delay}")
        self.page.frame_locator(frame).click(locator, delay=delay)

    @KeyWord.register("iframe拖拽元素")
    def frame_drag_and_drop(self, frame, start_selector, end_selector, timeout=3000):
        """
        拖拽元素
        :param frame: iframe定位表达式
        :param start_selector: 拖拽的元素
        :param end_selector: 拖拽到的元素
        :param timeout: 等待元素可见的最大超时时间
        :return:
        """
        print(f"正在拖拽元素:{start_selector}，拖拽到的元素:{end_selector}")
        s_ele = self.page.frame_locator(frame).locator(start_selector, timeout=timeout)
        e_ele = self.page.frame_locator(frame).locator(end_selector, timeout=timeout)
        s_ele.drag_to(e_ele)

class AssertMixin(BaseBrowser):
    """
    断言操作
    """
    @KeyWord.register("断言页面的标题")
    def assert_page_title(self, expect_results, is_equal=1):
        """
        断言页面的标题
        :param expect_results: 期望结果
        :param is_equal: 是否相等
        :return:
        """
        if is_equal:
            expect(self.page).to_have_title(re.compile(expect_results))
        else:
            expect(self.page).not_to_have_title(re.compile(expect_results))

    @KeyWord.register("断言页面的url地址")
    def assert_page_url(self, expect_results, is_equal=1):
        """
        断言页面的url地址
        :param expect_results: 期望结果
        :param is_equal: 是否相等
        :return:
        """
        if is_equal:
            expect(self.page).to_have_url(re.compile(expect_results))
        else:
            expect(self.page).not_to_have_url(re.compile(expect_results))

    @KeyWord.register("断言元素的value")
    def except_elm_value(self, locator, expect_results, is_equal=1):
        """
        断言元素的value
        :param locator: 元素
        :param expect_results: 预期值
        :param is_equal: 是否相等 等于：1 不等于 0
        :return:
        """

        if is_equal:
            expect(self.page.locator(locator)).to_have_value(re.compile(expect_results))
        else:
            expect(self.page.locator(locator)).not_to_have_value(re.compile(expect_results))

    @KeyWord.register("断言元素文本")
    def except_elm_text(self, locator, expect_results, is_equal):
        """
        断言元素的文本
        :param locator:
        :param expect_results:
        :param is_equal:
        :return:
        """
        if is_equal:
            expect(self.page.locator(locator)).to_have_text(re.compile(expect_results))
        else:
            expect(self.page.locator(locator)).not_to_have_text(expect_results)

    @KeyWord.register("断言元素的属性值")
    def except_elm_attribute(self, locator, name, value, is_equal):
        """
        断言元素的属性值
        :param locator:定位表达式
        :param name: 属性名称
        :param value: 属性值
        :param is_equal: 是否相等
        :return:
        """
        if is_equal:
            expect(self.page.locator(locator)).to_have_attribute(name, value)
        else:
            expect(self.page.locator(locator)).not_to_have_attribute(name, value)

    @KeyWord.register("断言元素是否可见")
    def except_elm_visible(self, locator, index=1):
        """
        断言元素是否可见
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_visible()
        else:
            expect(self.page.locator(locator).first).to_be_visible()

    @KeyWord.register("断言元素是否不可见")
    def except_elm_hidden(self, locator, index=1):
        """
        断言元素是否不可见
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_hidden()
        else:
            expect(self.page.locator(locator).first).to_be_hidden()

    @KeyWord.register("断言元素是否可用")
    def except_elm_enabled(self, locator, index=1):
        """
        断言元素是否可用
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_enabled()
        else:
            expect(self.page.locator(locator).first).to_be_enabled()

    @KeyWord.register("断言元素是否不可用")
    def except_elm_disabled(self, locator, index=1):
        """
        断言元素是否不可用
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_disabled()
        else:
            expect(self.page.locator(locator).first).to_be_disabled()

    @KeyWord.register("断言元素是否被选中")
    def except_elm_checked(self, locator, index=1):
        """
        断言元素是否被选中
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_checked()
        else:
            expect(self.page.locator(locator).first).to_be_checked()

    @KeyWord.register("断言元素是否为空")
    def except_elm_empty(self, locator, index=1):
        """
        断言元素是否为空
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_empty()
        else:
            expect(self.page.locator(locator).first).to_be_empty()

    @KeyWord.register("断言元素是否可编辑")
    def except_elm_editable(self, locator, index=1):
        """
        断言元素是否可编辑
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_editable()
        else:
            expect(self.page.locator(locator).first).to_be_editable()

    @KeyWord.register("断言元素是否获取焦点")
    def except_elm_focused(self, locator, index=1):
        """
        断言元素是否获取焦点
        :param locator:
        :param index: 定位到的第几个元素
        :return:
        """
        if index > 1:
            expect(self.page.locator(locator).nth(index - 1)).to_be_focused()
        else:
            expect(self.page.locator(locator).first).to_be_focused()

class BaseCase(PageMixin, LocatorMixin, MouseMixin, AssertMixin,WaitMixin,IFrameMixin):
    def perform(self,setup):
        """
        执行用例
        :param setup: 用例参数
        :return:
        """
        try:
            keyword=setup.get("keyword")
            print("+++++++++++")
            print(keyword)
            self.log.debug(f"执行步骤：{setup.get('desc')} 执行关键字：{keyword},执行参数：{setup.get('params')}")
            fun=self.get_map_method(keyword)
            if fun is None:
                self.log.error(f"执行步骤：{setup.get('desc')} 执行关键字：{keyword}不存在")
                raise AttributeError(f"执行关键字:{keyword}方法不存在")
            else:
                args = self.replace_value(setup.get("params"))
                fun(self,**args)
        except  Exception as e:
            self.log.error(f"执行用例异常，执行参数：{setup}",e)
            raise e

    def replace_value(self, value:dict):
        """
        替换变量
        :param value:
        :return:
        """
        try:
            pattern=re.compile(r"\{{(.*?)}}")
            value=str(value)
            while pattern.search(value):
                # 获取需要的值
                value1=pattern.search(value).group()
                #   获取变量名
                key=pattern.search(value1).group(1)
                # 获取新的值
                value2=self.config_env.get("global_vars").get(key,value1)
                # 替换变量
                value=value.replace(value1,value2)
            return eval(value)
        except Exception as e:
            self.log.error(f"替换数据失败{e}")
            raise e

if __name__ == '__main__':
    env_config = {
        "is_debug": False,
        "browser_type": "chromium",
        "host": "127.0.0.1",
        "global_vars": {
            "token": "quanjubianliang",
            "token2": "quanjubianliang2"
        }
    }
    setp1={"desc": "打开浏览器", "method": "open_browser", "params": {"browser_type": "chromium"}}
    setp2={"desc": "打开网页", "method": "open_url", "params": {"url": "https://www.baidu.com"}}
    bs = BaseCase(config_env=env_config)
    bs.perform(setp1)
    bs.perform(setp2)