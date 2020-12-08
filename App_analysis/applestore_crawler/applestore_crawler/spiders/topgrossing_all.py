import scrapy
import json
import re
import pandas as pd
import numpy as np

# 앱스토어 앱 정보 많이 성장한 앱 top200 수집
# https://itunes.apple.com/kr/rss/topgrossingapplications/limit=200/json
class Top_Grossing_Spider(scrapy.Spider):

    name = "topgrossing"
    allowed_domains = ["itunes.apple.com", "apps.apple.com"]

    def start_requests(self):
        start_url = 'https://itunes.apple.com/kr/rss/topgrossingapplications/limit=200/json'
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        yield scrapy.Request(url=start_url, callback=self.get_apppage, headers=headers)


    def get_apppage(self, response):
        query = response.json()
        entrys = query['feed']['entry']
        link = 'https://apps.apple.com/kr/app/id' # 애플 앱스토어 기본 링크

        # 앱 정보 추출
        for entry in entrys:
            title = entry['im:name']['label'] # 앱 이름
            developer = entry['im:artist']['label'] # 앱 개발자
            release_year = entry['im:releaseDate']['label'] # 앱 출시연도
            release_year = release_year.split('-')[0]
            category_code = entry['category']['attributes']['im:id'] # 앱 카테고리 코드
            id_num = entry['id']['attributes']['im:id'] # 앱 id
            app_url = link+id_num # 애플 앱스토어 링크
            yield scrapy.Request(url=link+id_num, callback=self.get_details, meta={"title" : title, "developer" : developer, "release_year" : release_year, "category_code" : category_code, "app_url" : app_url})
        

    def get_details(self, response):
        title = response.meta['title']
        developer = response.meta['developer']

        dd_text = response.xpath('//dd/text()').extract()

        # 앱 크기(MB): 앱 크기 추출 후 단위를 MB로 맞춤
        try:
            app_size = [dd for dd in dd_text if 'MB' in dd or 'GB' in dd][0]
            app_size_num = re.sub('[a-zA-Z]', '', app_size)
            size_unit = app_size[-2:]
            if size_unit == "GB":
                app_size = float(app_size_num) * 1000
            elif size_unit == "MB":
                app_size = float(app_size_num)
            else:
                pass
        except:
            app_size = None

        category_code = response.meta['category_code']
        category = response.xpath('//dd/a/text()')[0].extract().replace('\n', '').strip()

        # 앱 리뷰 개수: 정수형으로 추출
        review_num = response.css('p.we-customer-ratings__count.medium-hide::text').get().replace('\n', '').strip()
        try:
            review_number = re.sub('[가-힣]', '', review_num)
            review_unit = re.sub('[0-9.0-9]', '', review_num)
            review_unit = re.sub('개의 평가', '', review_unit)
            if review_unit == "만":
                review_num = int(float(review_number) * 10000)
            elif review_unit == "천":
                review_num = int(float(review_number) * 1000)
            else:
                review_num = int(review_number)
        except:
            pass

        # 앱 리뷰 평점(실수형)
        review_score = response.css('span.we-customer-ratings__averages__display::text').get().replace('\n', '').strip()
        review_score = float(review_score)

        p_text = response.xpath('//p/text()').extract()

        # 앱 호환 버전: 추출한 버전 이상(최소사양)
        try:
            version = [p.split('필요')[0] for p in p_text if '필요.' in p][0]
            version = re.search('iOS [0-9.]+.', version).group()
            version = re.sub('[a-zA-Z]', '', version).strip()
            version = float(version)
        except:
            version =None

        # 지원하는 언어 종류 및 개수
        try:
            lang = [p for p in p_text if '한국어' in p or '영어' in p or '중국어' in p][-1]
            if ',' in lang:
                lang_lst = lang.split(',')
                lang_num = len(lang_lst)
            else:
                lang_num = 1
        except:
            lang = None
            lang_num = None

        # 앱 무료/유료 여부 및 가격
        for dd in dd_text:
            if "무료" in dd:
                pricing = "free"
                price = 0
            elif "￦" in dd:
                pricing = "paid"
                price = ''.join(re.findall('[0-9]', dd))
            else:
                pass

        release_year = int(response.meta['release_year'])
        app_url = response.meta['app_url']

        yield {
            'title' : title,
            'developer' : developer,
            'app_size(MB)' : app_size,
            'category_code' : category_code,
            'category' : category,
            'review_num' : review_num,
            'review_score' : review_score,
            'version' : version,
            'lang' : lang,
            'lang_num' : lang_num,
            'pricing' : pricing,
            'price(won)' : price,
            'release_year' : release_year,
            'app_url' : app_url
        }