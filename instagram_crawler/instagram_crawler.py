# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
import json, time
from datetime import datetime
import pandas as pd
from ..middlewares import TooManyRequestsRetryMiddleware
from dateutil.relativedelta import relativedelta

# user_df = pd.read_csv('/home/ubuntu/workspace/influencer_list.txt', header=None)
# user_accounts = list(user_df[0])

class InstagramSpider(scrapy.Spider):
    name = 'instagram'

    todays_date = datetime.today() # 2021-06-03
    last_month_date = (todays_date - relativedelta(months=1)).strftime('%Y-%m-%d')
    
    # cookie정보
    cookies = {
        'id_did':'id_did',
        'mid':'mid-J',
        'ig_nrcb':'ig_nrcb',
        'csrftoken':'csrftoken',
        'ds_user_id':'ds_user_id',
        'sessionid':'sessionid%3AlJ4H1vPrWEXqIJ%3A1',
        'rur':'rur', 
        }

    def start_requests(self):
        for user_id in user_accounts:
            profile_url = 'https://www.instagram.com/{}/?__a=1'.format(user_id)
            yield scrapy.Request(profile_url, callback=self.parse_profile, meta={'user_id':user_id}, cookies=InstagramSpider.cookies)

    # 프로필 + 포스트 첫번째 페이지(12개 게시물)
    def parse_profile(self, response):
        time.sleep(1)
        
        res = response.json()
        user_id = response.meta['user_id'] # ssoing
        unique_id = res['graphql']['user']['id'] # 241234513512
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

            comments_count = node['edge_media_to_comment']['count']
            like_count = node['edge_media_preview_like']['count']

            yield {
                'user_id': user_id,
                'unique_id': unique_id,
                'user_name': user_name,
                'shortcode': shortcode,
                'follower': follower,
                'comments_count': comments_count,
                'like_count': like_count,
                'post_date': post_date
            }

        end_cursor = res['graphql']["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        
        # 두번째 페이지로 이동하기 위한 리퀘스트
        post_page = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A24%2C%22after%22%3A%22{}%3D%3D%22%7D".format(unique_id, end_cursor)
        yield scrapy.Request(post_page, callback=self.parse_posts, meta={'user_id': user_id, 'user_name': user_name, 'unique_id': unique_id, 'follower': follower}, cookies=InstagramSpider.cookies)

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
                'user_id': user_id,
                'unique_id': unique_id,
                'user_name': user_name,
                'follower': follower,
                'post_url': post_url,
                'comments_count': comments_count,
                'like_count': like_count,
                'post_date': post_date
            }

        # end_cursor 추출
        end_cursor = res['data']["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]

        # 스크롤하고 다음 페이지 주소 가져오기
        if end_cursor:
            time.sleep(3)
            next_page = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A24%2C%22after%22%3A%22{}%3D%3D%22%7D".format(unique_id, end_cursor)
            print("다음 포스트 페이지--------------------", next_page)
            yield scrapy.Request(next_page, callback=self.parse_posts, meta={'user_id': user_id, 'user_name': user_name, 'unique_id': unique_id, 'follower': follower}, cookies=InstagramSpider.cookies)