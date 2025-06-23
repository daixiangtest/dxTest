"""
关键封装demo
1.关键字执行驱动
2.关键字注册
3.动态注册关键字

"""

import inspect



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


class BaseCase(KeyWord):

    def __init__(self):
        self.name = '张三'

    @KeyWord.register("你好")
    def work(self):
        print('---------你好-------', self.name)

    def preform(self, step):
        """执行步骤"""
        keyword_=step.get("keyword")
        args=step.get("args")
        fun=self.get_map_method(keyword_)
        if fun:
            fun(self, *args)
        else:
            print("未注册关键字")

    @KeyWord.register("输入")
    def send_key(self,value):
        print("输入值",value)


if __name__ == '__main__':
    keywords = {
        "哈哈": """
def work1(self):
      print('---------哈哈-------',self.name)
""",
        "点击": """
def work2(self):
    print('---------正在执行点击方法----')
    """,
        "输入1": """
def work3(self,value):
    print(f'---------正在执行输入方法----输入值：{value}')
    """
    }
    # 动态注册注册关键字
    KeyWord.register_code("哈哈", keywords["哈哈"])
    KeyWord.register_code("点击", keywords["点击"])
    KeyWord.register_code("输入1", keywords["输入1"])
    # 步骤执行
    c = BaseCase()
    case=[{"keyword": "哈哈","args":{}},
          {"keyword": "点击","args":{}},
          {"keyword": "你好", "args":{}},
          {"keyword": "输入", "args":{"value": "输入的值"}},
          {"keyword":"输入1","args":{"value":"22123"}}]
    for i in case:
        c.preform(i)