import random

from faker import Faker
import datetime

fk = Faker(locale='zh_CN')


def random_phone_number():
    return fk.phone_number()


def random_email():
    return fk.email()


def create_transId():
    """生成交易ID"""
    now = datetime.datetime.now()
    day = str(now.day).zfill(2)
    month_index = str(now.month).zfill(2)
    # 生成pubDate
    pub_date = month_index + day + str(int(now.timestamp())).zfill(10)[0:10] + str(random.randint(100, 999))
    merchant_trans_id = "T8a" + pub_date
    return merchant_trans_id


def create_transTime():
    """生成交易时间"""
    now_utc = datetime.datetime.utcnow()
    formatted_time = now_utc.strftime('%Y-%m-%dT%H:%M:%S%Z')
    return formatted_time + "Z"


if __name__ == '__main__':
    print(create_transTime())
