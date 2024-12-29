

import pymysql


class DBClient:
    "数据库的链接类"

    def init_connect(self, dbs):
        """
        处理数据库的链接
        :return:
        """
        self.dbs=dbs
        print(type(dbs))
        if isinstance(dbs, dict):
            # 单个数据库
            self.create_connect(dbs)
        elif isinstance(dbs, list):
            # 多个数据库
            for db in dbs:
                self.create_connect(db)
        else:
            raise TypeError("数据库的配置格式错误")

    def create_connect(self, db):
        """
        创建数据库的连接对象
        :param db:
        :return:
        """
        print(db)
        if not db.get('name') and db.get('type') and db.get('config'):
            raise TypeError("数据库的配置格式错误")
        if db.get('type') == 'mysql':
            obj = MySqlDB(db.get('config'))
            print(11111)
            setattr(self, db.get('name'), obj)
            # self.huawei.test()
        elif db.get('name') == 'mongodb':
            pass
    def test(self):
        self.huawei.test()
    def close_connect(self):
        for db in self.dbs:
            if isinstance(self.__dict__[db['name']], MySqlDB):
                self.__dict__[db['name']].close()


class MySqlDB:
    def __init__(self, db_config):
        self.conn = pymysql.connect(**db_config, autocommit=True)
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def execute(self, sql, args=None):
        """
        执行sql 语句
        :param sql:
        :param args:
        :return:
        """
        try:
            self.cursor.execute(sql, args)
            return self.cursor.fetchall()
        except Exception as e:
            raise e
    def test(self):
        print("ceshi")
    def close(self):
        """
        断开数据库连接
        :return:
        """
        print('关闭数据库')
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    dbs = [
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

    db=DBClient()
    db.init_connect(dbs)
    value=db.lockhost.execute("select * from test003.auth_permission")
    print(value)
    data=db.huawei.execute("select * from books.result")
    print("data",data)
    # print(dbaa)
    db.close_connect()