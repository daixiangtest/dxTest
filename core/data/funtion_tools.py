from faker import Faker


fk=Faker(locale='zh_CN')
def random_phone_number():
    return fk.phone_number()

def random_email():
    return fk.email()

if __name__ == '__main__':
    print(random_email())