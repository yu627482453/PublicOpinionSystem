# -*- coding: utf-8 -*-
# @Time : 2020/1/2 12:19
# @Author : Nero
# @FileName: weiboSpider.py
# @Software: PyCharm
# @e-mail: 627482453@qq.com


import json
from abc import ABC

import scrapy
import html2text

from weiboSpider.items import WeibospiderItem

CONTAINER_URL = "https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0"
COMMENT_URL = "https://m.weibo.cn/comments/hotflow?id={id}&mid={id}&max_id_type=0"


class WeiboSpider(scrapy.Spider, ABC):
    """
    Spider 类
    """
    name = "weibo"

    def start_requests(self):
        """
        请求开始
        :return: yield
        """

        urls = [CONTAINER_URL]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        数据处理
        :param response: 请求
        :return: yield
        """
        rs = json.loads(response.text)
        print(rs)

        if rs.get('ok') == 1:
            for card in rs.get('data').get('cards'):
                item = WeibospiderItem()
                mblog = card.get('mblog')
                item['id'] = mblog.get('id')
                item['scheme'] = card.get('scheme').replace("\"", "\'")
                item['create_time'] = mblog.get('created_at').replace("\"", "\'")

                h2t = html2text.HTML2Text()
                h2t.ignore_links = True
                h2t.ignore_images = True
                h2t.ignore_emphasis = True
                h2t.ignore_tables = True
                item['text'] = h2t.handle(mblog.get('text')).replace("\"", "\'")
                item['text_length'] = mblog.get('textLength')

                user0 = [{
                    'id': mblog.get('user').get('id'),
                    'name': mblog.get('user').get('screen_name').replace("\"", "\'"),
                    'url': mblog.get('user').get('profile_url').replace("\"", "\'"),
                    'description': mblog.get('user').get('description').replace("\"", "\'")
                }]

                item['user0'] = user0

                yield scrapy.Request(url=COMMENT_URL.format(id=item["id"]),
                                     meta={'item': item, 'h2t': h2t},
                                     callback=self.parse_comment,
                                     dont_filter=True)

    def parse_comment(self, response):

        item = response.meta['item']
        h2t = response.meta['h2t']
        if json.loads(response.text).get('ok') == 1:
            datas = json.loads(response.text).get("data").get("data")
            comments = []

            for data in datas:
                comment = {
                    "id": data.get('id'),
                    "text": h2t.handle(data.get('text')).replace("\"", "\'"),
                    "user": {
                        'id': data.get('user').get('id'),
                        'name': data.get('user').get('screen_name').replace("\"", "\'"),
                        'url': data.get('user').get('profile_url').replace("\"", "\'"),
                        'description': data.get('user').get('description').replace("\"", "\'")
                    }
                }
                comments.append(comment)

            item['comments'] = comments

            yield item
