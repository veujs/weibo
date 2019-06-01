# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from weibo.items import UserItem, UserRelationItem, WeiboItem
import re
import time


class WeibocnSpider(scrapy.Spider):
    name = 'weibocn'
    allowed_domains = ['m.weibo.cn']
    start_urls = ['http://m.weibo.cn/']

    # uid 用户id（唯一标识）

    # 用户页
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    # 关注
    follow_url = 'https://m.weibo.cn/api/container/' \
                 'getIndex?containerid=231051_-_followers_-_{uid}_-_1042015:tagCategory_050&page={page}'
    # 粉丝
    fan_url = 'https://m.weibo.cn/api/container/' \
              'getIndex?containerid=231051_-_fans_-_{uid}_-_1042015:tagCategory_050&page={page}'
    # 发布的微博
    weibo_url = 'https://m.weibo.cn/api/container/' \
                'getIndex?uid={uid}&type=uid&value={uid}&containerid=107603{uid}&page={page}'

    # 需爬取的用户
    # start_users = ['3125046087']  # 刘烨、谢娜、张译
    start_users = ['3125046087', '1192329374']  # 刘烨、谢娜、张译
    # start_users = ['3125046087', '1192329374', '1235733435']  # 刘烨、谢娜、张译

    def parse_user(self, response):
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()

            field_map = {'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                         'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                         'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                         'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
            }

            # 用户的详情
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
            yield user_item
            import time
            time.sleep(5)

            print('parser_user % s' % user_info.get('id'))

            # # 用户的关注
            # uid = user_info.get('id')
            # yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
            #               meta={'page': 1, 'uid': uid})
            #
            # # 用户的粉丝
            # yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans,
            #               meta={'page': 1, 'uid': uid})
            #
            # # 用户的微博
            # yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
            #               meta={'page': 1, 'uid': uid})

    def parse_follows(self, response):
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) \
                and result.get('data').get('cards')[-1].get('card_group'):

            # 解析用户 (所关注的用户)
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid), callback=self.parse_user)

            # 关注列表
            uid = response.meta.get('uid')
            user_relation_item = UserRelationItem()
            follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')}
                       for follow in follows]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            yield user_relation_item

            # 下一页关注
            page = response.meta.get('page') + 1
            yield Request(self.follow_url.format(uid=uid, page=page), callback=self.parse_follows,
                          meta={'page': page, 'uid': uid})

    def parse_fans(self, response):
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) \
                and result.get('data').get('cards')[-1].get('card_group'):

            # 解析用户 (粉丝)
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('i   d')
                    yield Request(self.user_url.format(uid=uid), callback=self.parse_user)

            # 粉丝列表
            uid = response.meta.get('uid')  # 上一个请求传递过来的参数  通过meta来传递
            user_relation_item = UserRelationItem()
            fans = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')}
                    for fan in fans]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = []
            user_relation_item['fans'] = fans
            yield user_relation_item

            # 下一页粉丝
            page = response.meta.get('page') + 1
            yield Request(self.follow_url.format(uid=uid, page=page), callback=self.parse_follows,
                          meta={'page': page, 'uid': uid})

    def parse_weibos(self, response):
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')):
            weibos = result.get('data').get('cards')

            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count', 'created_at': 'created_at', 'text': 'text',
                        'source': 'source', 'pictures': 'pics', 'picture': 'original_pic', 'raw_text': 'raw_text',
                        'thumbnail': 'thumbnail_pic'
                    }

                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item

            # 下一页微博
            page = response.meta.get('page') + 1
            uid = response.meta.get('uid')
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})

    def start_requests(self):
        for uid in self.start_users:
            print('start_requests %s' % uid )
            yield Request(url=self.user_url.format(uid=uid), callback=self.parse_user)




"""
"Host: m.weibo.cn
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate, br
X-Requested-With: XMLHttpRequest
MWeibo-Pwa: 1
Referer: https://m.weibo.cn/p/index?containerid=231051_-_followers_-_3125046087_-_1042015%3AtagCategory_050&luicode=10000011&lfid=1076033125046087
"
"""
