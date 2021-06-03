# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
import pandas as pd
import time
import json
import requests

# 티몬 베스트탭-실시간베스트 상품 정보 스크래핑
class CrawlTmon(scrapy.Spider):
    name = "tmon"
    allowed_domains = ["tmon.co.kr"]
    url_format = "http://www.tmon.co.kr/best?bestType=best_100&gender=0&age=0&price=0"


    def __init__(self):
        self.start_urls = []
        for cur_date in pd.date_range(startdate, enddate):
            self.start_urls.append(self.url_format.format(cur_date.strftime("%Y%m%d")))


    def start_requests(self):
        for start_url in self.start_urls: # 가져올 페이지를 리스트에 저장
            yield scrapy.Request(url=start_url, callback=self.parse, meta={"start_url" : start_url, "page_num": 1})
            time.sleep(5)


    def parse(self, response):