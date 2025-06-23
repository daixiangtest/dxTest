"""
测试执行类日志记录
"""
import time


class Logger:
    def save_log(self, level,message):
        """
        保存日志
        :param level: 日志级别
        :param message: 日志内容
        :return:
        """
        # 获取时间
        tm=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        message=str(tm)+" | "+str(message)
        if not hasattr(self,"log_data"):
            setattr(self,"log_data",[])
        # 动态获取log_data属性
        time.sleep(3)
        log_data=getattr(self,"log_data")
        log_data.append((level,message))
        print(level,message)

    def info(self,*args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'INFO')

    def debug(self,*args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'DEBUG')

    def warning(self,*args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'WARNING')

    def error(self,*args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'ERROR')

    def critical(self,*args):
        msg = ' '.join([str(i) for i in args])
        self.save_log(msg, 'CRITICAL')

    def get_log(self):
        if hasattr(self, "log_data"):
            log_data = getattr(self, "log_data")
        else:
            log_data = []
        return log_data