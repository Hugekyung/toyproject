from selenium import webdriver
from bs4 import BeautifulSoup
import time, os
from datetime import datetime
import pandas as pd
import requests

# 구글 플레이스토어 크롤러(셀레니움+뷰티풀숩)
# 앱-인기차트-인기앱/게임
# link = 'https://play.google.com/store/apps/collection/cluster?clp=0g4jCiEKG3RvcHNlbGxpbmdfZnJlZV9BUFBMSUNBVElPThAHGAM%3D:S:ANO1ljKs-KA&gsr=CibSDiMKIQobdG9wc2VsbGluZ19mcmVlX0FQUExJQ0FUSU9OEAcYAw%3D%3D:S:ANO1ljL40zU'

# 몇 번 스크롤 할건지
# scroll_cnt = 4

# download chrome driver https://sites.google.com/a/chromium.org/chromedriver/home
# driver = webdriver.Chrome('C:/Users/haech/chromedriver.exe')
# driver.get(link)


##################
# for i in range(scroll_cnt):
#   print('스크롤 {} 번째 진행 중...'.format(i+1))
#   # scroll to bottom
#   driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') # 맨 아래로 스크롤
#   time.sleep(2)
###################

# driver.execute_script('window.scrollTo(0, document.body.scrollHeight-100000);') # 맨 위로 스크롤
# time.sleep(5)

# 순서대로 앱 클릭
# app_name = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/div[1]/c-wiz/div/div/div[2]/div/div/div[1]/div/div/div[1]/a/div')
# app_name.click()
# print('앱 클릭 !!!')

# 앱 연결 페이지 주소 리스트로 저장
# app_lst = []

url = 'https://play.google.com/store/apps/collection/topselling_free'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

url_lst = []
a_tags = soup.select("div a.JC71ub")
for a_tag in a_tags:
  url = a_tag.attrs['href']
  url_lst.append(url)
print(url_lst)
print(len(url_lst))

# 주소 리스트에서 순서대로 이동-for문으로 반복하면서 페이지 내 데이터 수집





#   # click 'Load more' button, if exists
#   try:
#     load_more = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div/span/span')
#     load_more.click()
#     print('button click!!!')
#   except:
#     print('Cannot find load more button...')

# # get review containers
# reviews = driver.find_elements_by_xpath('//*[@jsname="fk8dgd"]//div[@class="d15Mdf bAhLNe"]')

# print('There are %d reviews avaliable!' % len(reviews))
# print('Writing the data...')

# # create empty dataframe to store data
# df = pd.DataFrame(columns=['name', 'ratings', 'date', 'helpful', 'comment'])

# # get review data(beautifulsoup 사용)
# for review in reviews:
#   # parse string to html using bs4
#   soup = BeautifulSoup(review.get_attribute('innerHTML'), 'html.parser')

#   # reviewer
#   name = soup.find(class_='X43Kjb').text

#   # rating
#   ratings = int(soup.find('div', role='img').get('aria-label').replace('별표 5개 만점에', '').replace('개를 받았습니다.', '').strip())

#   # review date
#   date = soup.find(class_='p2TkOb').text
#   date = datetime.strptime(date, '%Y년 %m월 %d일')
#   date = date.strftime('%Y-%m-%d')

#   # helpful
#   helpful = soup.find(class_='jUL89d y92BAb').text
#   if not helpful:
#     helpful = 0
  
#   # review text
#   comment = soup.find('span', jsname='fbQN7e').text
#   if not comment:
#     comment = soup.find('span', jsname='bN97Pc').text
  
#   # 개발자 답변
#   developer_comment = None
#   dc_div = soup.find('div', class_='LVQB0b')
#   if dc_div:
#     developer_comment = dc_div.text.replace('\n', ' ')
  
#   # append to dataframe
#   df = df.append({
#     'name': name,
#     'ratings': ratings,
#     'date': date,
#     'helpful': helpful, # 유용한 리뷰
#     'comment': comment
#     'developer_comment': developer_comment
#   }, ignore_index=True)

# # csv파일로 저장
# filename = 'V4.csv'
# df.to_csv(filename, encoding='utf-8-sig', index=False)
# driver.stop_client()
# driver.close()
# print('Done!')