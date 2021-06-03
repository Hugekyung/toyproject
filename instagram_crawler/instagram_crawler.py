# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
import json, time
from datetime import datetime
from dateutil.relativedelta import relativedelta
API = 'API-KEY' # https://webscraping.ai/ 에서 받은 프록시 api를 활용한 크롤링
user_accounts = ['namooactors', 'i_icaruswalks', '8oong', 's.soom', 'dailyjjun', '2hae1', 'ini_iii', 'niniz_official',
                'converse_kr', 'nunu___s2', 'ore.zeno', 'hyuuuk___', 'oneonones_', 'seo.co_', 'dukong126'
]


def get_url(url):
    payload = {'api_key': API, 'proxy': 'residential', 'timeout': '20000', 'url': url}
    proxy_url = 'https://api.webscraping.ai/html?' + urlencode(payload)
    return proxy_url

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['api.webscraping.ai']
    custom_settings = {'CONCURRENT_REQUESTS_PER_DOMAIN': 5} # 동시 스레드(무료플랜에서 제공하는 수)
    requests_count = 0
    todays_date = datetime.today()
    last_month_date = (todays_date - relativedelta(days=30)).strftime('%Y-%m-%d')

    def start_requests(self):
        for user_id in user_accounts:
            profile_url = 'https://www.instagram.com/{}/?__a=1'.format(user_id)
            self.requests_count += 1
            yield scrapy.Request(get_url(profile_url), callback=self.parse_profile, meta={'user_id':user_id})

    # 프로필 + 포스트 첫번째 페이지(12개 게시물)
    def parse_profile(self, response):
        time.sleep(1)
        
        res = response.json()
        user_id = response.meta['user_id']
        unique_id = res['graphql']['user']['id']
        user_name = res['graphql']['user']['full_name']
        follower = res['graphql']['user']['edge_followed_by']['count']

        edges = res['graphql']['user']['edge_owner_to_timeline_media']['edges']
        for edge in edges:
            node = edge['node']

            shortcode = node['shortcode']
            timestamp = node['taken_at_timestamp'] # timestamp 형식을 날짜-시간 형식으로 변환

            post_date = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
            if post_date < self.last_month_date: # 게시물의 업로드 날짜가 지난 한달 동안의 범위를 벗어날 경우
                return

            post_url = 'https://www.instagram.com/p/{}/'.format(shortcode)
            comments_count = node['edge_media_to_comment']['count']
            like_count = node['edge_media_preview_like']['count']

            yield {
                'total_requests_count': self.requests_count,
                'user_id': user_id,
                'unique_id': unique_id,
                'user_name': user_name,
                'follower': follower,
                'post_url': post_url,
                'comments_count': comments_count,
                'like_count': like_count,
                'post_date': post_date
            }

        end_cursor = res['graphql']["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"][:-2]
        
        # 두번째 페이지로 이동하기 위한 리퀘스트
        post_page = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A13%2C%22after%22%3A%22{}%3D%3D%22%7D".format(unique_id, end_cursor)
        self.requests_count += 1
        yield scrapy.Request(get_url(post_page), callback=self.parse_posts, meta={'user_id': user_id, 'user_name': user_name, 'unique_id': unique_id, 'follower': follower})

    # 포스트 두번쨰~마지막페이지(12개씩)
    def parse_posts(self, response):
        time.sleep(1)

        user_id = response.meta['user_id']
        user_name = response.meta['user_name']
        unique_id = response.meta['unique_id']
        follower = response.meta['follower']

        res = response.json()
        edges = res['data']['user']['edge_owner_to_timeline_media']['edges']
        for edge in edges:
            node = edge['node']

            shortcode = node['shortcode']
            timestamp = node['taken_at_timestamp'] # timestamp 형식을 날짜-시간 형식으로 변환

            post_date = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
            if post_date < self.last_month_date: # 게시물의 업로드 날짜가 지난 한달 동안의 범위를 벗어날 경우
                return

            post_url = 'https://www.instagram.com/p/{}/'.format(shortcode)
            comments_count = node['edge_media_to_comment']['count']
            like_count = node['edge_media_preview_like']['count']

            yield {
                'total_requests_count': self.requests_count,
                'user_id': user_id,
                'unique_id': unique_id,
                'user_name': user_name,
                'follower': follower,
                'post_url': post_url,
                'comments_count': comments_count,
                'like_count': like_count,
                'post_date': post_date
            }

        print(f"크롤링 중 ~~ {self.requests_count} 번째 리퀘스트 진행 중..")

        # end_cursor 추출
        try:
            end_cursor = res['data']["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"][:-2]
            print('=======================================')
            print("end_cursor :", end_cursor)
            print('=======================================')
        except:
            end_cursor = None
            print('엔드커서 없음')
            return

        # 스크롤하고 다음 페이지 주소 가져오기
        if end_cursor:
            time.sleep(3)
            next_page = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A13%2C%22after%22%3A%22{}%3D%3D%22%7D".format(unique_id, end_cursor)
            print("다음 포스트 페이지--------------------", next_page)
            self.requests_count += 1
            yield scrapy.Request(get_url(next_page), callback=self.parse_posts, meta={'user_id': user_id, 'user_name': user_name, 'unique_id': unique_id, 'follower': follower})