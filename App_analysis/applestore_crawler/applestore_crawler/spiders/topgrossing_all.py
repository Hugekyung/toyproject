import scrapy
import json
import time
import re
import datetime
import pandas as pd
import numpy as np

# 앱스토어 앱 정보 많이 성장한 순위별 수집
# https://itunes.apple.com/kr/rss/topgrossingapplications/limit=200/json
class Top_Grossing_Spider(scrapy.Spider):

    name = "topgrossing"
    allowed_domains = ["itunes.apple.com", "apps.apple.com"]

    def start_requests(self):
        start_url = 'https://itunes.apple.com/kr/rss/topgrossingapplications/limit=10/json'
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        yield scrapy.Request(url=start_url, callback=self.get_apppage, headers=headers)


    def get_apppage(self, response):
        query = response.json()

        entrys = query['feed']['entry']
        for entry in entrys:
            link = entry['link'][0]['attributes']['href']
            release_year = entry['im:releaseDate']['label']
            release_year = release_year.split('-')[0]
            yield scrapy.Request(url=link, callback=self.get_details, meta={"release_year" : release_year})
        

    def get_details(self, response):
        title = response.css('h1::text').get()
        developer = response.xpath('//dd/text()')[0].extract()
        app_size = response.xpath('//dd/text()')[1].extract()
        cetegory_code = response.xpath('//dd/a/text()')[0].extract()
        review_num = response.css('p.we-customer-ratings__count.medium-hide::text').get()
        try:
            review_number = re.sub('[가-힣]', '', review_num)
            review_unit = re.sub('[0-9].[0-9]', '', review_num)
            review_unit = re.sub('개의 평가', '', review_unit)
            if review_unit == "만":
                review_num = int(float(review_number) * 10000)
            elif review_unit == "천":
                review_num = int(float(review_number) * 1000)
            else:
                pass
        except:
            pass
        review_score = response.css('span.we-customer-ratings__averages__display::text').get()

        try:
            version = response.xpath('//p/text()')[-3].extract()
            version = re.findall('[0-9]+.[0-9]', version)[0]
        except:
            pass
        lang = response.xpath('//p/text()')[-2].extract()
        lang_num = len(lang)
        paid = response.xpath('//dd/text()')[-3].extract()
        if paid == "무료":
            paid = "F"
        else:
            paid = "P"
        release_year = response.meta["release_year"]

        yield {
            'title' : title,
            'developer' : developer,
            'app_size(mb)' : app_size,
            'category_code' : category_code,
            'review_num' : review_num,
            'review_score' : review_score,
            'version' : version,
            'lang' : lang,
            'lang_num' : lang_num,
            'paid' : paid,
            'release_year' : release_year
        }