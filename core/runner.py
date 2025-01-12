from core.base_case import BaseCase


class TestRunner:
    def __init__(self, cases, env_data):
        self.cases = cases
        self.env = env_data

    def run_cases(self):
        for items in self.cases:
            print("######env#####",self.env)
            test = BaseCase(self.env)
            print('执行业务流：',items['name'])
            for item in items['cases']:
                test.run_case(item)


if __name__ == '__main__':
    cases_task = [
        {
            'name': "测试业务流1",
            'cases': [
                {
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
                        "json": {"age": 20, "phone": "${{phone}}"}
                    },
                    "setup_script": open("data/setup_script", 'r', encoding='utf-8').read(),
                    "teardown_script": open("data/teardown_script", 'r', encoding='utf-8').read(),
                },
            ]
        },
        {
            "name": "业务流2",
            'cases': [
                {
                    "title": "登录用户",
                    "interface": {
                        "url": "http://127.0.0.1:8000/api/users/login/",
                        "method": "POST",
                    },
                    "headers": {
                        "content-type": "application/json"
                    },
                    "params": {},
                    "body": {
                        "files": {},
                        "data": {},
                        "json": {"username": "admin", "password": "Dx3826729"}
                    },
                    "setup_script": "print('第二条用例开始')",
                    "teardown_script": "case.add_var('token',response.json()['token'])",
                },
                {
                    "title": "查看项目列表",
                    "interface": {
                        "url": "http://127.0.0.1:8000/api/testPro/projects/",
                        "method": "GET",
                    },
                    "headers": {
                        "content-type": "application/json",
                        "Authorization": "Bearer ${{token}}"
                    },
                    "params": {},
                    "body": {
                        "files": {},
                        "data": {},
                        "json": {}
                    },
                    "setup_script": "print('第三条用例开始')",
                    "teardown_script": "print('第三条用例结束')",
                }
            ]}

    ]

    env = {
        "base_url": "http://115.120.244.181:8001",
        "headers": {
            "content-type": "application/json"
        },
        "envs": {
            "token": "sjjwiskwo=",
            "mid": 1230
        },
        "global_fun": open('data/funtion_tools.py', 'r', encoding='utf-8').read()
    }
    TestRunner(cases_task, env).run_cases()
