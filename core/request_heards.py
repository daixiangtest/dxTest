"""
特殊请求方法处理
"""

import time
import requests
import json
import hashlib
import datetime
import random



class TestApi:
    # merchantTransID = "",
    # merTransTime = "",
    origMerTransID = "",
    datetime = "",
    authorization = ""
    BaseUrl = "https://bkk-staging-api.everonet.com"
    BasePath = "/v3/payment/sys/GRB/90231910/evo.e-commerce."

    def __create_transid(self):
        # 生成交易id
        now = datetime.datetime.now()
        day = str(now.day).zfill(2)
        month_index = str(now.month).zfill(2)
        # 生成pubDate
        pub_date = month_index + day + str(int(now.timestamp())).zfill(10)[0:10] + str(random.randint(100, 999))
        merchant_trans_id = "T8a" + pub_date
        return merchant_trans_id

    def __creare_datetime(self):
        # 获取当前日期时间
        now = datetime.datetime.now()
        hours = str(now.hour).zfill(2)
        minutes = str(now.minute).zfill(2)
        seconds = str(now.second).zfill(2)
        day = str(now.day).zfill(2)
        month_index = str(now.month).zfill(2)
        year = str(now.year)
        self.datetime = year + month_index + day + hours + minutes + seconds + "+0800"
        # return year + month_index + day + hours + minutes + seconds + "+0800"

    def __create_transTime(self):
        now_utc = datetime.datetime.utcnow()
        formatted_time = now_utc.strftime('%Y-%m-%dT%H:%M:%S%Z')
        return formatted_time + "Z"

    def __script(self, body, type, transid=None):
        # 定义URL
        if type == 1:
            url = self.BasePath + "authorise"
        elif type == 2:
            # print(self.origMerTransID)
            if transid is None:
                url = self.BasePath + f"refund/{self.origMerTransID}"
            else:
                url = self.BasePath + f"refund/{transid}"
        elif type == 3:
            url = self.BasePath + f"cancel/{self.origMerTransID}"
        elif type == 4:
            if transid is None:
                url = self.BasePath + f"capture/{self.origMerTransID}"
            else:
                url = self.BasePath + f"capture/{transid}"
        else:
            raise ValueError("不支持该接口类型请根本规范输入")
        # print("url:", url)
        self.__creare_datetime()
        signkey = "239hr93f374fg584f934hf"
        sign_string = 'POST\n' + url + '\n' + self.datetime + '\n' + signkey + '\n' + json.dumps(body)
        # print(sign_string)
        # print(sign_string)
        # 计算SHA256哈希值
        authorization = hashlib.sha256(sign_string.encode()).hexdigest()
        # print(authorization)
        self.authorization = authorization

    def send_api(self, value, capture_after_hours=0):
        url = self.BaseUrl + self.BasePath + "authorise"
        trans_id = self.__create_transid()
        body = {
            "webhook": f"http://115.120.244.181:8001/webhook/{trans_id}/1/",
            "captureAfterHours": f"{capture_after_hours}",
            "authorise": {
                "merchantTransID": f"{trans_id}",
                "merchantTransTime": f"{self.__create_transTime()}",
                "storeNum": "S12345678",
                "transAmount": {
                    "currency": "THB",
                    "value": f"{value}"
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
        # print(body)
        self.__script(body, 1)
        payload = json.dumps(body)

        headers = {
            'Authorization': f'{self.authorization}',
            'SignType': 'SHA256',
            'DateTime': f'{self.datetime}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'bkk-staging-api.everonet.com',
            'Connection': 'keep-alive'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        text = response.json()
        self.origMerTransID = text["authorise"]["merchantTransID"]
        print("预售权响应头：", response.headers)
        print("预售权响应体：", response.text)
        return response.json()

    def send_api_refund(self, value, transid=None):
        if transid is None:
            refund_url = self.BaseUrl + self.BasePath + f"refund/{self.origMerTransID}"
        else:
            refund_url = self.BaseUrl + self.BasePath + f"refund/{transid}"
        trans_id = self.__create_transid()
        # print(refund_url)
        body = {
            "webhook": f"http://115.120.244.181:8001/webhook/{trans_id}/1/",
            "refund": {
                "merchantTransID": f"{trans_id}",
                "storeNum": "S12345678",
                "merchantTransTime": f"{self.__create_transTime()}",

                "transAmount": {
                    "currency": "THB",
                    "value": f"{value}"
                }
            }
        }
        self.__script(body, 2, transid)
        payload = json.dumps(body)
        headers = {
            'Authorization': f'{self.authorization}',
            'SignType': 'SHA256',
            'DateTime': f'{self.datetime}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'bkk-staging-api.everonet.com',
            'Connection': 'keep-alive'
        }
        print(refund_url, headers, payload)
        response = requests.request("POST", refund_url, headers=headers, data=payload)
        print("退款响应头：", response.headers)
        print("退款响应体：", response.text)
        return response.json()

    def send_api_cancel(self):
        url = "https://bkk-staging-api.everonet.com/v3/payment/sys/GRB/90231910/evo.e-commerce.cancel/{{authmerchantTransID}}"
        url = self.BaseUrl + self.BasePath + f"cancel/{self.origMerTransID}"
        body = {
            "webhook": "https://test-api.stg-grablink.co/v0/payment/webhook/kbank/evo.ec.notification/21042713512500040007",
            "cancel": {
                "merchantTransID": f"{self.__create_transid()}",
                "storeNum": "S12345678",
                "merchantTransTime": f"{self.__create_transTime()}",
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
        self.__script(body, 3)
        payload = json.dumps(body)
        headers = {
            'Authorization': f'{self.authorization}',
            'SignType': 'SHA256',
            'DateTime': f'{self.datetime}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'bkk-staging-api.everonet.com',
            'Connection': 'keep-alive'
        }
        # print(url, headers, payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        print("撤销响应头：", response.headers)
        print("撤销响应体：", response.text)

    def send_api_capture(self, value, transid=None):
        if transid is None:
            refund_url = self.BaseUrl + self.BasePath + f"capture/{self.origMerTransID}"
        else:
            refund_url = self.BaseUrl + self.BasePath + f"capture/{transid}"
        trans_id = self.__create_transid()
        body = {
            "webhook": f"http://115.120.244.181:8001/webhook/{trans_id}/1/",
            "capture": {
                "merchantTransID": f"{trans_id}",
                "storeNum": "S12345678",
                "merchantTransTime": f"{self.__create_transTime()}",
                "transAmount": {
                    "currency": "THB",
                    "value": f"{value}"
                }
            }
        }
        self.__script(body, 4, transid)
        payload = json.dumps(body)
        headers = {
            'Authorization': f'{self.authorization}',
            'SignType': 'SHA256',
            'DateTime': f'{self.datetime}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'bkk-staging-api.everonet.com',
            'Connection': 'keep-alive'
        }
        # print(refund_url, headers, payload)
        response = requests.request("POST", refund_url, headers=headers, data=payload)
        print("退款响应头：", response.headers)
        print("退款响应体：", response.text)
        print(response.status_code)
        return response.json()


def grablink_headers(request_data):
    """G1 grablink 请求头处理"""
    print(request_data)
    time.sleep(3000)

def signature_sha256():
    """签名处理"""

if __name__ == '__main__':
    test = TestApi()
    res = test.send_api()
