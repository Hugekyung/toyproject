import scrapy
import json
import time
import re
import datetime
import pandas as pd
import numpy as np

# 앱스토어 앱 정보 카테고리별 수집
class Apple_Store_Spider(scrapy.Spider):

    name = "App"

    def __init__(self):
        try:
            id_file = input("id 파일명(경로 포함)을 입력해 주세요(ex. D:\Scrapy\insta_crawling\insta_crawling\jl_1.csv)\n")
            self.df = pd.read_csv(r"{}".format(id_file))
            self.inner_id_ls = list(map(str, list(np.unique(self.df['inner_id']))))
        except:
            print("id_file_error!")
            self.inner_id_ls = []
        self.starttime = time.time()
        self.request_count = 0
        # self.id2npage = {}
    
      