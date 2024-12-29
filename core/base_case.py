import re
import run_funtion_tools as run_fun
import requests
from jsonpath import jsonpath
from core.case_log import LogCase

class BaseCase(LogCase):
    """
        测试执行框架的类
    """

    def __init__(self, env):
        self.env = env
        # 识别字符串中的Python代码,将代码加载到run_fun模块中 可以通过该模块名称调用字符串中的类和方法
        # 该代码用来执行数据库保存的全局工具函数的Python代码
        exec(self.env['global_fun'],run_fun.__dict__)
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

    def __run_script(self,data):
        """
        自定义前后置脚本的夹具
        :param data:
        :return:
        """
        # 实例化一个对象方便调用里面的方法
        case=self
        # 创建一个环境变量的对象
        env_var=self.env['envs']
        print=self.log_print
        # 执行前置脚本内容
        setup_script = data['setup_script']
        exec(setup_script)


        request_data,response = yield

        # 执行后置脚本内容
        teardown_script = data['teardown_script']
        exec(teardown_script)
        yield

    def __setup_script(self, data):
        """
        执行前置脚本
        :param data:
        :return:
        """
        # 创建一个生成器函数对象先调用第一步
        self.script_hook=self.__run_script(data)
        # 执行第一步内容
        next(self.script_hook)

        # setup_script=data['setup_script']
        # exec(setup_script)

    def __teardown_script(self, data,request_data,response):
        """
        执行后置脚本
        :param data:
        :return:
        """
        # 根据生成器对象中添加response 参数并执行
        self.script_hook.send((request_data,response))
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
        if data['params'] != {}:
            params = data['params']
            request_data['params'] = params
        body = data['body']
        if BaseCase.is_value(body, "json"):
            request_data['json'] = body['json']
        elif BaseCase.is_value(body, "data"):
            request_data['data'] = body['data']
        elif BaseCase.is_value(body, "files"):
            request_data['files'] = body['files']
        return self.__replace_data(request_data)
    def __replace_data(self, data):
        """
        处理请求数据中的变量进行替换 ${{}}
        :param data:
        :return:
        """

        # 正则匹配校验规则
        pattern=r'\${{(.+?)}}'
        data=str(data)
        # print(re.search(pattern, data))
        while re.search(pattern, data):
            # 匹配到变量名称
            match = re.search(pattern, data)
            # 获取变量进行替换
            key=match.group(1)
            # 获取变量
            value=self.env['envs'][key]
            # 替换变量
            data=data.replace(match.group(), str(value))
        return eval(data)


    def __send_request(self, data):
        """
        发送接口请求
        :param data:
        :return:
        """
        request_data = self.__process_request_data(data)
        self.log_info("请求数据：",request_data)
        responses=requests.request(**request_data)
        self.log_info("响应数据：",responses.text)
        return request_data,responses
    def run_case(self, data):
        """
        运行测试用例
        :param data: 用例参数
        :return:
        """
        self.__setup_script(data)
        request_data,responses=self.__send_request(data)
        self.__teardown_script(data,request_data,responses)
        for i in self.logs:
            print(i)
        # next(self.script_hook)
    def add_var(self, variables,value):
        """
        添加值到环境变量中
        :param variables: 变量名
        :param value: 变量的值
        :return:
        """
        self.log_debug(f"添加变量名：{variables}变量值：{value}")
        self.env['envs'][variables] = value

    def del_var(self, variables):
        """
        删除环境中的变量
        :param variables:
        :param value:
        :return:
        """
        self.log_debug(f"删除变量名：{variables}变量值：{self.env['envs'][variables]}")
        del self.env['envs'][variables]

    def re_extract(self,obj,ext):
        """
        正则提取数据的方法
        :param obj: 数据对象
        :param ext: 匹配的正则规则
        :return:
        """

        obj=str(obj) if not isinstance(obj,str) else obj
        self.log_debug("数据源：",obj)
        # ext=r'message":"(.+?)"'
        value=re.search(ext,obj)
        value=value.group(1) if value else ''
        self.log_debug("正则提取数据值为:",value)
        return value

    def json_extract(self,obj,ext,list=False):
        """
        通过jsonpath提取数据
        :param obj: json数据对象
        :param ext: 匹配规则 $.
        :return:
        """
        value=jsonpath(obj,ext)
        if list:
            value = value if value else []
        else:
            value=value[0] if value else ''
        self.log_debug("json提取数据：",value)
        return value

    def assert_data(self,expected_value,actual_value,method="eq"):
        """
        对响应结果进行断言
        :param expected_value: 预期结果
        :param actual_value:  实际结果
        :return:
        """
        self.log_info('对响应结果断言')
        result = "PASS"
        # 多重断言
        if isinstance(expected_value,dict):
            for k ,v in expected_value.items():
                value=actual_value.get(k,None)
                if v==value:
                    self.log_info(f"断言结果：PASS 预期结果：{v}实际结果：{value}")
                else:
                    result="FAIL"
                    self.log_error(f"断言结果：{result} 预期结果：{v}实际结果：{value}")
            if result=="PASS":
                self.log_info(f"最终断言结果：{result}")
            else:
                self.log_error(f"最终断言结果：{result}")
        else:
            # 单数据断言
            method_map={
                "eq":lambda x,y:x==y,
                "neq":lambda x,y:x!=y,
                "gt":lambda x,y:x>y,
                "gte":lambda x,y:x>=y,
                "lt":lambda x,y:x<y,
                "lte":lambda x,y:x<=y,
                "in":lambda x,y:x in y,
                "nin":lambda x,y:x not in y,
            }
            results=method_map[method](expected_value,actual_value)
            if results:
                result="PASS"
                self.log_info(f'断言结果：{result}预期结果：{expected_value}实际结果：{actual_value}断言方法：{method}')
            else:
                result="FAIL"
                self.log_error(f'断言结果：{result}预期结果：{expected_value}实际结果：{actual_value}断言方法：{method}')
        return result
if __name__ == '__main__':
    case = {
        "title": "测试调试",
        "interface": {
            "url": "http://115.120.244.181:8001/webhook/${{mid}}/1202/",
            "method": "GET",
        },
        "headers": {
            "content-type": "application/json",
            "Content-MD5": "${{token}}"
        },
        "params": {},
        "body": {
            "files": {},
            "data": {},
            "json": {"age":19,"phone":"${{phone}}"}
        },
        "setup_script": open("data/setup_script", 'r',encoding='utf-8').read(),
        "teardown_script": open("data/teardown_script", 'r',encoding='utf-8').read(),
    }
    env = {
        "base_url": "http://115.120.244.181:8001",
        "headers": {
            "content-type": "application/json"
        },
        "envs":{
            "token": "sjjwiskwo=",
            "mid":1230
        },
        "global_fun":open('data/funtion_tools.py','r',encoding='utf-8').read()
    }


    test = BaseCase(env)
    test.run_case(case)
