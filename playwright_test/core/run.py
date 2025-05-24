from playwright_test.core.bases_case import BaseCase
import re

class Runner:
    def __init__(self, env_config, test_case):
        self.env_config = env_config
        self.test_case = test_case
        self.browser, self.context, self.page = None, None, None

    def run(self):
        # 执行公共参数的前置操作
        if self.test_case.get("setup_step"):
            self.run_suite_step()
        self.run_suite()

    def run_suite_step(self):
        print("执行前置操作")
        run_case = BaseCase(self.env_config)
        for step in self.test_case.get("setup_step"):
            print("前置步骤操作", step)
            run_case.perform(step)
        self.browser, self.context, self.page = run_case.browser, run_case.context, run_case.page

    def run_suite(self):
        print("执行用例集")
        run_case2 = BaseCase(self.env_config, self.browser, self.context, self.page)
        for case in self.test_case.get("cases"):
            self.run_case(case, run_case2)

    def run_case(self, case:dict,run_obj: BaseCase):
        print("执行用例", case)
        for step in case.get("steps"):
            run_obj.perform(step)
            print("执行步骤", step)


if __name__ == '__main__':
    env_config = {
        "is_debug": False,
        "browser_type": "chromium",
        "host": "https://www.baidu",
        "global_vars": {
            "value1": "python代码",
            "value2": "java代码"
        }
    }

    test_case = {
        "id": "编号",
        "name": "测试名称",
        # 前置操作
        "setup_step": [
            # {"desc": "打开浏览器", "method": "open_browser", "params": {"browser_type": "chromium"}},
            # {"desc": "打开网页", "method": "open_url", "params": {"url": ".com"}},
            # {"desc": "等待时间", "method": "wait_time", "params": {"timeout": 3}}
        ],
        # 用例集
        "cases": [
            {"title": "测试用例1",
             "steps": [
                 # {"desc": "打开浏览器", "method": "open_browser", "params": {"browser_type": "chromium"}},
                 {"desc": "打开网页", "method": "open_url", "params": {"url": ".com"}},
                 {"desc": "输入搜索内容", "method": "fill_value",
                  "params": {"locator": '//*[@id="kw"]', "value": "{{value1}}"}},
                 {"desc": "点击搜索", "method": "click_elm", "params": {"locator": '//*[@id="su"]'}},
                 {"desc": "等待时间", "method": "wait_time", "params": {"timeout": 3}},
                 {"desc": "重置浏览器", "method": "init_browser", "params": {}}
             ]},
            {
                "title": "测试用例2",
                "steps": [
                    {"desc": "等待时间", "method": "wait_time", "params": {"timeout": 3}},
                    # {"desc": "打开浏览器", "method": "open_browser", "params": {"browser_type": "chromium"}},
                    {"desc": "打开网页", "method": "open_url", "params": {"url": "https://www.baidu.com"}},
                    {"desc": "输入搜索内容", "method": "fill_value",
                     "params": {"locator": '//*[@id="kw"]', "value": "{{value2}}"}},
                    {"desc": "点击搜索", "method": "click_elm", "params": {"locator": '//*[@id="su"]'}},
                    {"desc": "等待时间", "method": "wait_time", "params": {"timeout": 3}}
                ]}
        ]
    }
    Runner(env_config, test_case).run()
