import re
import time

import run_funtion_tools as run_fun
import requests
from jsonpath import jsonpath
from core.case_log import LogCase
from core.data.db_clinet import DBClient
from core.request_heards import SHA256_headers


class BaseCase(LogCase):
    """
        测试执行框架的类
    """

    def __init__(self, env):
        self.time = 0
        self.title = "调试用例"
        # 穿件数据库的连接对象
        self.db = DBClient()
        # 获取执行环境参数
        self.env = env
        # 识别字符串中的Python代码,将代码加载到run_fun模块中 可以通过该模块名称调用字符串中的类和方法
        # 该代码用来执行数据库保存的全局工具函数的Python代码
        exec(self.env['global_fun'], run_fun.__dict__)

    @staticmethod
    def is_value(data, key):
        """
        判断自动中的可以是否存在
        :param data: 字典对象
        :param key: key
        :return: 存在返回值不存在返回false
        """
        try:
            return data[key]
        except KeyError:
            return False

    def __run_script(self, data):
        """
        自定义前后置脚本的夹具
        :param data:
        :return:
        """
        # 连接测试环境中的数据库
        self.db.init_connect(self.env['db'])
        # 实例化一个对象方便调用里面的方法
        case = self
        db = self.db
        # 创建一个环境变量的对象
        # env_var = self.env['envs']
        # 全局环境变量(作用于整个测试计划)
        global_var= self.env['global_vars']
        # 局部环境变量（作用于测试业务流）
        local_var = self.env['local_vars']
        print = self.log_print
        # 执行前置脚本内容
        setup_script = data['setup_script']
        exec(setup_script)

        request_data, response = yield

        # 执行后置脚本内容
        teardown_script = data['teardown_script']
        exec(teardown_script)
        db.close_connect()
        yield

    def __setup_script(self, data):
        """
        执行前置脚本
        :param data:
        :return:
        """
        # 创建一个生成器函数对象先调用第一步
        self.script_hook = self.__run_script(data)
        # 执行第一步内容
        next(self.script_hook)

        # setup_script=data['setup_script']
        # exec(setup_script)

    def __teardown_script(self, data, request_data, response):
        """
        执行后置脚本
        :param data:
        :return:
        """
        # 根据生成器对象中添加response 参数并执行
        self.script_hook.send((request_data, response))
        # next(self.script_hook)
        # 后置脚本执行完删除生成器对象
        del self.script_hook
        # teardown_script=data['teardown_script']
        # exec (teardown_script)

    def __process_request_data(self, data):
        """
        处理请求参数
        :param data:
        :return:
        """
        try:
            request_data = {}
            method = data['interface']['method']
            request_data['method'] = method
            # 处理请求参数
            url = data['interface']['url']
            if not url.startswith('http'):
                url = self.env['base_url'] + url
            request_data['url'] = url
            # 处理全局请求头和用例的请求头
            headers = data['headers']
            headers.update(self.env['headers'])
            request_data['headers'] = headers
            # 处理请求数据
            self.request_body = {}
            if data['params'] != {}:
                params = data['params']
                request_data['params'] = params
                self.request_body['params'] = params
            body = data['body']
            if BaseCase.is_value(body, "json"):
                request_data['json'] = body['json']
                self.request_body['json'] = body['json']
            elif BaseCase.is_value(body, "data"):
                request_data['data'] = body['data']
                self.request_body['data'] = body['data']
            elif BaseCase.is_value(body, "files"):
                request_data['files'] = body['files']
                self.request_body['files'] = body['files']
            return self.__replace_data(request_data)
        except Exception as e:
            self.log_critical("处理请求数据失败：",e)

    def __replace_data(self, data):
        """
        处理请求数据中的变量进行替换 ${{}}
        :param data:
        :return:
        """
        try:
            # 正则匹配校验规则
            pattern = r'\${{(.+?)}}'
            data = str(data)
            # print(re.search(pattern, data))
            while re.search(pattern, data):
                # 匹配到变量名称
                match = re.search(pattern, data)
                # 获取变量进行替换
                key = match.group(1)
                value = key
                # 获取变量(优先获取局部变量)
                if BaseCase.is_value(self.env['local_vars'], key):
                    value = self.env['local_vars'][key]
                    print(1111)
                elif BaseCase.is_value(self.env['global_vars'], key):
                    value = self.env['global_vars'][key]
                    print(2222)
                else:
                    self.log_warn(f'变量名：{key}不存在环境变量中')
                # 替换变量
                print("value",value)
                data = data.replace(match.group(), str(value))
            return eval(data)
        except Exception as e:
            self.log_critical("替换变量数据失败：",e)
            raise e
    def __send_request(self, data,type):
        """
        发送接口请求
        :param data:
        :return:
        """
        request_data = self.__process_request_data(data)
        print(request_data)
        # 保存用例的请求信息
        # print('request_data', request_data)
        # self.request_data['request_data'] = request_data
        self.url = request_data['url']
        self.method = request_data['method']
        self.request_headers = request_data['headers']
        self.log_info("请求数据：", request_data)
        if type == 'ecv2':
            # 项目常用接口封装
            print("ecv2接口逻辑")
            print(self.logs)
            SHA256_headers(request_data)
            # responses = requests.request(**request_data)
        else:
            responses = requests.request(**request_data)
        # 保存响应信息
        self.status_code = responses.status_code
        self.response_headers = responses.headers
        self.response_body = responses.text
        self.log_info("响应数据：", responses.text)
        return request_data, responses

    def run_case(self, data,type):
        """
        运行测试用例
        :param data: 用例参数
        :return:
        """
        start_tiem=time.time()
        self.title = data.get('title')
        # 执行前置脚本
        self.__setup_script(data)
        # 发送请求
        request_data, responses = self.__send_request(data,type)
        # 执行后置脚本
        self.__teardown_script(data, request_data, responses)
        end_time = time.time()
        self.time=end_time-start_tiem
        # for i in self.logs:
        #     print(i)

    def add_var(self, variables, value):
        """
        添加值到环境变量中
        :param variables: 变量名
        :param value: 变量的值
        :return:
        """
        self.env['global_vars'][variables] = value
        self.log_debug(f"添加全局变量名：{variables}变量值：{value}")

    def del_var(self, variables):
        """
        删除环境中的全局变量
        :param variables:
        :param value:
        :return:
        """
        self.log_debug(f"删除全局变量名：{variables}变量值：{self.env['global_vars'][variables]}")
        del self.env['global_vars'][variables]


    def add_let(self, variables, value):
        """
        添加值到环境局部变量中
        :param variables: 变量名
        :param value: 变量的值
        :return:
        """
        self.env['local_vars'][variables] = value
        self.log_debug(f"添加局部变量名：{variables}变量值：{value}")
    def del_let(self, variables):
        """
       删除环境中的局部变量
       :param variables:
       :param value:
       :return:
       """
        self.log_debug(f"删除局部变量名：{variables}变量值：{self.env['envs']['local_vars']}")
        del self.env['local_vars'][variables]
    def re_extract(self, obj, ext):
        """
        正则提取数据的方法
        :param obj: 数据对象
        :param ext: 匹配的正则规则
        :return:
        """

        obj = str(obj) if not isinstance(obj, str) else obj
        self.log_debug("数据源：", obj)
        # ext=r'message":"(.+?)"'
        value = re.search(ext, obj)
        value = value.group(1) if value else ''
        self.log_debug("正则提取数据值为:", value)
        return value

    def json_extract(self, obj, ext, list=False):
        """
        通过jsonpath提取数据
        :param obj: json数据对象
        :param ext: 匹配规则 $.
        :return:
        """
        value = jsonpath(obj, ext)
        if list:
            value = value if value else []
        else:
            value = value[0] if value else ''
        self.log_debug("json提取数据：", value)
        return value

    def assert_data(self, expected_value, actual_value, method="eq"):
        """
        对响应结果进行断言
        :param expected_value: 预期结果
        :param actual_value:  实际结果
        :return:
        """
        self.log_info('对响应结果断言')
        result = "PASS"
        # 多重断言
        if isinstance(expected_value, dict):
            for k, v in expected_value.items():
                value = actual_value.get(k, None)
                if v == value:
                    self.log_info(f"断言结果：PASS 预期结果：{v}实际结果：{value}")
                else:
                    result = "FAIL"
                    self.log_error(f"断言结果：{result} 预期结果：{v}实际结果：{value}")
                    raise AssertionError(
                        f'断言结果：{result}预期结果：{expected_value}实际结果：{actual_value}断言方法：{method}')
            if result == "PASS":
                self.log_info(f"最终断言结果：{result}")
            else:
                self.log_error(f"最终断言结果：{result}")
        else:
            # 单数据断言
            method_map = {
                "eq": lambda x, y: x == y,
                "neq": lambda x, y: x != y,
                "gt": lambda x, y: x > y,
                "gte": lambda x, y: x >= y,
                "lt": lambda x, y: x < y,
                "lte": lambda x, y: x <= y,
                "in": lambda x, y: x in y,
                "nin": lambda x, y: x not in y,
            }
            results = method_map[method](expected_value, actual_value)
            if results:
                result = "PASS"
                self.log_info(f'断言结果：{result}预期结果：{expected_value}实际结果：{actual_value}断言方法：{method}')
            else:
                result = "FAIL"
                self.log_error(f'断言结果：{result}预期结果：{expected_value}实际结果：{actual_value}断言方法：{method}')
                raise AssertionError(
                    f'断言结果：{result}预期结果：{expected_value}实际结果：{actual_value}断言方法：{method}')
        return result


if __name__ == '__main__':
    case = {
        "title": "测试调试",
        "interface": {
            "url": "/v3/payment/sys/GRB/90231910/evo.e-commerce.authorise",
            "method": "POST",
        },
        "headers": {
            "content-type": "application/json"
        },
        "params": {},
        "body": {
            "files": {},
            "data": {},
            "json": {
            "webhook": "http://115.120.244.181:8001/webhook/${{trans_id}}/1/",
            "captureAfterHours": "0",
            "authorise": {
                "merchantTransID": "${{trans_id}}",
                "merchantTransTime": "${{transTime}}",
                "storeNum": "S12345678",
                "transAmount": {
                    "currency": "THB",
                    "value": "1"
                },
                "metadata": {
                    "case": 1
                },
                "paymentMethod": {
                    "card": {
                        "number": "5431289719925031",
                        "holderName": "MC TEST CARD",
                        "expiryMonth": "12",
                        "expiryYear": "2027",
                        "name": 12121212
                    }
                },
                "threeDS": {
                    "mpiData": {
                        "cavv": "YWFiYg==",
                        "eci": "02",
                        "dsTransID": "90231910334455",
                        "threeDSVersion": "2.1.0"
                    }
                }
            },
            "pspInfo": {
                "sponsorCode": "90231910",
                "name": "kbank",
                "merchantName": "testMerchant",
                "merchantID": "401012021680001"
            }
        }
        },
        "setup_script": open("data/G1setup", 'r', encoding='utf-8').read(),
        "teardown_script": open("data/G1trardown", 'r', encoding='utf-8').read(),
    }
    env = {
        "base_url": "https://bkk-staging-api.everonet.com",
        "headers": {
            "content-type": "application/json"
        },
        "global_vars": {
            "token": "quanjubianliang",
            "mid": 1230
        },
        "local_vars": {
            "token": "jububianliang",
            "mid": 1230
        },
        "global_fun": open('data/funtion_tools.py', 'r', encoding='utf-8').read(),
        'db': [
            {
                'name': 'lockhost',
                'type': 'mysql',
                'config': {
                    'host': '127.0.0.1',
                    'port': 3306,
                    'user': 'root',
                    'password': '123456',
                }
            },
            {
                'name': 'huawei',
                'type': 'mysql',
                'config': {
                    'host': '115.120.244.181',
                    'port': 3306,
                    'user': 'root',
                    'password': 'Dx3826729123',
                }
            }
        ]
    }

    test = BaseCase(env)
    test.run_case(case,"ecv2")
