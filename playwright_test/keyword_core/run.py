import time

from playwright_test.keyword_core.bases_case import BaseCase
from playwright_test.keyword_core.logger import Logger


class Result:
    """
    {
    1、套件编号
    2、用例总数
    3、成功数量
    4、失败数量
    5、错误数量
    6、跳过的数量(前置执行错误，所有的用例都跳过执行)
    7、套件名称
    8、开始执行时间
    9、执行总时长
    10、套件执行日志信息
    11、用例执行详情:[
        {
            1、用例ID: N01
            2、用例名称：XXX
            3、执行结果：成功、失败、错误、跳过，
            4、执行步骤:
            5、日步骤执行日志
            6、执行结果截图：
        },
        {
            1、用例ID: N02
            2、用例名称：XXX2
            3、执行结果：成功、失败、错误、跳过，
            4、执行步骤:
            5、日步骤执行日志
            6、执行结果截图：
        }
    ],
    12、未执行用例数量
    13、未执行的用例详情
}
    """

    def __init__(self, config_env, suite):
        self.time_ = None
        self.suite = suite  # 执行套件详情
        self.config_env = config_env  # 执行环境配置
        self.all=len(suite.get("cases",[]))
        self.success = 0  # 成功数量
        self.fail = 0  # 失败数量
        self.error = 0  # 错误数量
        self.skip = 0  # 跳过数量
        self.no_run = 0  # 未执行用例数量
        self.start_time = ""  # 开始执行时间
        self.run_time = ""  # 执行总时长
        self.suite_logs = []  # 执行日志
        self.run_cases = []  # 执行用例详情
        self.no_run_cases = []  # 未执行用例详情

    def add_success(self, case_, log, img):
        self.success += 1
        case_["state"] = "success"
        case_["log"] = log
        case_["img"] = img
        self.run_cases.append(case_)

    def add_fail(self, case_, log, img):
        self.fail += 1
        case_["state"] = "fail"
        case_["log"] = log
        case_["img"] = img
        self.run_cases.append(case_)

    def add_error(self, case_, log, img):
        self.error += 1
        case_["state"] = "error"
        case_["log"] = log
        case_["img"] = img
        self.run_cases.append(case_)

    def add_skip(self, case_):
        self.skip += 1
        case_["state"] = "skip"
        self.run_cases.append(case_)

    def add_no_run(self, case_):
        self.no_run += 1
        self.no_run_cases.append(case_)

    def run_start_time(self):
        self.time_ = time
        self.start_time = self.time_.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def run_end_time(self,suite_log):
        end = time.time()
        self.run_time = end - self.time_.time()
        # 统计未执行用例
        if  (self.success+self.fail+self.error+self.skip) != self.all:
            run_case_ids=[run_case.get("id") for run_case in self.run_cases]
            for case_ in self.suite.get("cases"):
                if case_ not in run_case_ids:
                    self.add_no_run(case_)
        self.suite_logs=suite_log
    def get_result(self):
        return {
            "id": self.suite.get("id"),
            "name": self.suite.get("name"),
            "total": self.all,
            "success": self.success,
            "fail": self.fail,
            "error": self.error,
            "skip": self.skip,
            "no_run": self.no_run,
            "start_time": self.start_time,
            "run_time": self.run_time,
            "run_cases":self.run_cases,
            "no_run_cases":self.no_run_cases,
            "suite_logs":self.suite_logs
        }

class Runner:
    """
    关键字驱动测试执行用例
    """
    def __init__(self, env_config, test_case):
        self.env_config = env_config
        self.test_case = test_case
        self.browser, self.context, self.page = None, None, None
        self.suite = []
        self.log = Logger()
        self.result = Result(self.env_config, self.test_case)

    def run(self):
        # 开始执行时间
        self.result.run_start_time()
        # 执行公共参数的前置操作
        self.run_suite_step()
        # 执行用例集
        self.run_suite()
        # 结束执行时间
        log_data=getattr(self.log,"log_data")
        self.result.run_end_time(log_data)
        # 返回用例执行结果
        return self.result.get_result()

    def run_suite_step(self):
        """
        执行前置执行步骤
        :return:
        """
        if self.test_case.get("setup_step"):
            try:
                self.log.debug("执行测试前置步骤")
                run_case = BaseCase(self.env_config, self.log)
                for step in self.test_case.get("setup_step"):
                    self.log.debug(f"执行测试前置用例步骤:{step.get('desc')}")
                    run_case.perform(step)
                self.browser, self.context, self.page = run_case.browser, run_case.context, run_case.page
            except  Exception as e:
                self.log.error("前置步骤执行失败", e)
                raise e

    def run_suite(self):
        """
        运行测试套件
        :return:
        """
        if not self.test_case.get("cases"):
            self.log.warning("没有用例集需要执行")
            return
        run_case2 = BaseCase(self.env_config, self.log, self.browser, self.context, self.page)
        for case_ in self.test_case.get("cases"):
            # 创建执行用例的日志对象且每次用例执行完更新一个新的日志对象
            log = Logger()
            run_case2.update_log(log)
            self.log.debug(f"执行测试用例:{case_.get('title')}")
            # 跳过用例
            if case_.get("skip"):
                log.warning(f"跳过用例:{case_.get('title')}")
                self.result.add_skip(case_)
                continue
            try:
                self.run_case(case_, run_case2)
                log.info(f"用例执行成功:{case_.get('title')}")
                img=run_case2.save_page_img(f'{case_.get("title")}_{case_.get("id")}',"success")
                self.result.add_success(case_, getattr(log, "log_data"), img)
            except AssertionError as e:
                log.critical(f"用例断言失败:{case_.get('title')}", e)
                img = run_case2.save_page_img(f'{case_.get("title")}_{case_.get("id")}', "fail")
                self.result.add_fail(case_, getattr(log, "log_data"), img)
            except Exception as e:
                log.error(f"用例执行失败:{case_.get('title')}", e)
                img = run_case2.save_page_img(f'{case_.get("title")}_{case_.get("id")}', "error")
                self.result.add_error(case_, getattr(log, "log_data"), img)
    def run_case(self, case: dict, run_obj: BaseCase):
        for step in case.get("steps"):
            run_obj.perform(step)


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
            {"desc": "打开浏览器", "keyword": "打开浏览器", "params": {"browser_type": "chromium"}},
            {"desc": "打开网页", "keyword": "打开网页", "params": {"url": ".com"}}
        ],
        # 用例集
        "cases": [
            {
                "id": 1,
                "title": "测试用例1",
                "skip": False,
                "steps": [

                    {"desc": "输入搜索内容", "keyword": "输入",
                     "params": {"locator": '//*[@id="kw"]', "value": "{{value1}}"}},
                    {"desc": "点击搜索", "keyword": "点击", "params": {"locator": '//*[@id="su"]'}},
                    # {"desc": "等待时间", "method": "wait_time", "params": {"timeout": 3}},

                ]},
            {
                "id": 2,
                "title": "测试用例2",
                "skip": False,
                "steps": [
                    {"desc": "重置浏览器", "keyword": "重置浏览器", "params": {}},
                    # {"desc": "等待时间", "method": "wait_time", "params": {"timeout": 3}},
                    # {"desc": "打开浏览器", "method": "open_browser", "params": {"browser_type": "chromium"}},
                    {"desc": "打开网页", "keyword": "打开网页", "params": {"url": "https://www.baidu.com"}},
                    {"desc": "输入搜索内容", "keyword": "fill_value",
                     "params": {"locator": '//*[@id="kw"]', "value": "{{value2}}"}},
                    {"desc": "点击搜索", "keyword": "点击", "params": {"locator": '//*[@id="su"]'}},
                    {"desc": "等待时间", "keyword": "强制等待", "params": {"timeout": 3}},
                    # {"desc": "关闭浏览器", "method": "close_browser", "params": {}}
                ]}
        ]
    }
    res=Runner(env_config, test_case).run()
    print(res)

