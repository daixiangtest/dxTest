class LogCase:
    """
    处理用例的日志记录
    """

    def save_log(self, level, msg):
        if not hasattr(self, 'logs'):
            setattr(self, 'logs', [])
        getattr(self, 'logs').append((level, msg))
        # print(self.logs)
    def log_info(self, *args):
        msg = "".join([str(i) for i in args])
        self.save_log(level='INFO', msg=msg)

    def log_error(self, *args):
        msg = "".join([str(i) for i in args])
        self.save_log(level='ERROR', msg=msg)

    def log_critical(self, *args):
        msg = "".join([str(i) for i in args])
        self.save_log(level='CRITICAL', msg=msg)

    def log_warn(self, *args):
        msg = "".join([str(i) for i in args])
        self.save_log(level='WARN', msg=msg)

    def log_debug(self, *args):
        msg = "".join([str(i) for i in args])
        self.save_log(level='DEBUG', msg=msg)

    def log_print(self, *args):
        msg = "".join([str(i) for i in args])
        self.save_log(level='PRINT', msg=msg)

if __name__ == '__main__':
    log = LogCase()
    log.log_info("info", {"code": 10}, (12, 13))
