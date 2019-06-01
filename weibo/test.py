import requests
from weibo.settings import COOKIES_URL
import json



PROXY_URL = 'http://proxy.tongmingmedia.com/http/get'
PROXY_URL2 = 'http://0.0.0.0:5555/random'

def init_re():
    print('------------------------------获取COOKIES------------------------------------')
    print(COOKIES_URL)
    response = requests.get(url=COOKIES_URL)
    print(response)
    print(response.text)
    print(type(response.text))
    if response.status_code == 200:
        cookies = json.loads(response.text)
        print(cookies)
        print(type(cookies))


    print('------------------------------获取代理------------------------------------')
    print(PROXY_URL)
    response = requests.get(url=PROXY_URL)
    print(response)
    print(response.text)
    print(type(response.text))
    if response.status_code == 200:
        proxy_result = json.loads(response.text)
        print(proxy_result)
        print(type(proxy_result))
        proxy = proxy_result.get('proxy').get('host') + ':' + str(proxy_result.get('proxy').get('port'))
        print(proxy)


    print('------------------------------获取代理------------------------------------')
    print(PROXY_URL2)
    response = requests.get(url=PROXY_URL2)
    print(response)
    print(response.text)
    print(type(response.text))
    # if response.status_code == 200:
    #     proxy_result = json.loads(response.text)
    #     print(proxy_result)
    #     print(type(proxy_result))
    #     # proxy = proxy_result.get('proxy').get('host') + ':' + str(proxy_result.get('proxy').get('port'))
    #     # print(proxy)


def test_yield():
    for i in range(0, 10):
        # print(i)
        yield i
        print(str(i) + '  test')


if __name__ == "__main__":
    # init_re()
    # test_yield()
    f = test_yield()

    print(next(f))
    print(next(f))
    # print(next(f))
    # print(next(f))
    # print(next(f))
    # print(next(f))
    # print(next(f))
    # print(next(f))
    # print(next(f))
    # print(next(f))



    # f.next()
    # f.next()
    # f.next()
    # f.next()

'''
{
    'proxy': {
        'host': '121.233.40.151', 
        'port': 894, 
        'address': 'http://121.233.40.151:894', 
        'expires_at': 1559373304, 
        'headers': {
            'Proxy-Authorization': 'Basic ZGV2ZWxvcGVyQHRvbW1tdC5jb206VG9tbW10NjY2'
        }
    }
}
'''
