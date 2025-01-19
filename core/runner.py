from unittest import TestResult

from core.base_case import BaseCase


class TestResult:

    def __init__(self, all, name="调试用例"):
        self.all = all
        self.success = 0
        self.fail = 0
        self.error = 0
        self.cases = []
        self.name = name

    def add_case(self, test, status):
        data = {
            'name': getattr(test, 'title', None),
            'method': getattr(test, 'method', None),
            'url': getattr(test, 'url', None),
            'request_headers': getattr(test, 'request_headers', None),
            'request_data': getattr(test, 'request_body', None),
            'status_code': getattr(test, 'status_code', None),
            'response_headers': getattr(test, 'response_headers', None),
            'response_body': getattr(test, 'response_body', None),
            'status': status,
            'time': getattr(test, 'time', None),
            'log_data': getattr(test, 'logs', None),
        }
        self.cases.append(data)

    def add_success(self, test: BaseCase):
        self.success += 1
        test.log_info(f"{getattr(test, 'title', None)}:用例执行成功")
        self.add_case(test, "success")

    def add_fail(self, test: BaseCase, error):
        self.fail += 1
        test.log_critical(error)
        self.add_case(test, "fail")

    def add_error(self, test: BaseCase, error):
        self.error += 1
        test.log_error(error)
        self.add_fail(test, 'error')

    def get_result(self):
        res = {
            'name': self.name,
            "all": self.all,
            'fail': self.fail,
            'error': self.error,
            'success': self.success,
            'cases': self.cases,

        }
        return res


class TestRunner:
    def __init__(self, cases, env_data):
        self.cases = cases
        self.env = env_data
        self.results = []

    def run_cases(self):
        for items in self.cases:
            test = BaseCase(self.env)
            result = TestResult(len(items['cases']), items['name'])
            type = items['type']
            for item in items['cases']:
                try:
                    test.run_case(item, type)
                    # print("用例执行通过")
                    result.add_success(test)
                except AssertionError as e:
                    # print("用例执行失败，断言错误", e)
                    result.add_error(test, e)
                except Exception as e:
                    # print("用例执行异常：", e)
                    result.add_fail(test, e)
            self.results.append(result.get_result())
        return self.results
        # return self.results


if __name__ == '__main__':
    cases_task = [
        {'type': "ecv2",
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
            'type': "接口类型",
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
                    "teardown_script": "case.add_let('token',response.json()['token'])",
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
            ]},
        {
            'type': "ecv2",
            "name": "G1granlink",
            'cases': [
                {
                    "title": "支付",
                    "interface": {
                        "url": "https://bkk-staging-api.everonet.com/v3/payment/sys/GRB/90231910/evo.e-commerce.authorise",
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
                },
                {
                    "title": "撤销",
                    "interface": {
                        "url": "https://bkk-staging-api.everonet.com/v3/payment/sys/GRB/90231910/evo.e-commerce.cancel/${{orgtrans_id}}",
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
                            "webhook": "https://test-api.stg-grablink.co/v0/payment/webhook/kbank/evo.ec.notification/21042713512500040007",
                            "cancel": {
                                "merchantTransID": "${{trans_id}}",
                                "storeNum": "S12345678",
                                "merchantTransTime": "${{transTime}}",
                            }, "metadata": {
                                "currency": "THB",
                                "code": "02"
                            },
                            "pspInfo": {
                                "sponsorCode": "90231910",
                                "name": "kbank",
                                "merchantName": "testMerchant",
                                "merchantID": "4010120212740012"
                            }
                        }
                    },
                    "setup_script": open("data/G1setup", 'r', encoding='utf-8').read(),
                    "teardown_script": open("data/G1trardown", 'r', encoding='utf-8').read(),
                }
            ]
        }

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
        "global_fun": open('data/funtion_tools.py', 'r', encoding='utf-8').read(),
        "global_vars": {
            "token": "quanjubianliang",
            "mid": 1230
        },
        "local_vars": {
            "token": "jububianliang",
            "mid": 1230
        },
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
    requests = TestRunner(cases_task, env).run_cases()
    print(requests)
