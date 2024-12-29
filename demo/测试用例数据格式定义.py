"""
测试用例数据包含以下内容来进行定义

1.用例的名称

2.接口的信息：
    请求地址
    请求方式
3.接口的请求头：

4.接口的请求体：
    表单格式
    json格式
    表单格式
    其他特殊格式
5.前置脚本处理：
    执行一些工具函数
    链接数据库操作
    对接口数据进行加密处理操作

6.后置脚本处理：
    提取接口数数据进行断言
    查询数据库断言

7.生成用例运行后的测试结果

8.记录执行日志信息
"""
from distutils.core import setup

case={
    "title":"",
    "interface":{
        "url":"",
        "method":"GET",
    },
    "headers":{
        "content-type":"application/json",
    },
    "body":{
        "params":{},
        "data":{},
        "json":{}
    },
    "setup_script":"print('前置脚本')",
    "teardown_script":"print('后置脚本')",
}