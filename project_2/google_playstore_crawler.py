from selenium import webdriver
from bs4 import BeautifulSoup
import time, os
from datetime import datetime
import pandas as pd

# 구글 플레이스토어 앱리뷰 크롤러(셀레니움+뷰티풀숩)
# review link link
# V4
link = 'https://play.google.com/store/apps/details?id=com.nexon.v4kr&showAllReviews=true'

# 몇 번 스크롤 할건지
scroll_cnt = 100

# download chrome driver https://sites.google.com/a/chromium.org/chromedriver/home
driver = webdriver.Chrome('C:/Users/haech/chromedriver.exe')
driver.get(link)

# 리뷰 결과를 최신순으로 변경

# 옵션 클릭
search_option = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/c-wiz/div[1]/div/div[1]/div[1]/div[3]/span')
search_option.click()
time.sleep(3)

# '최신' 클릭
search_option_new = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/c-wiz/div[1]/div/div[2]/div[1]/span')
search_option_new.click()
print('최신순으로 변경 완료!!!')

# os.makedirs('result', exist_ok=True) # 결과 폴더 생성

for i in range(scroll_cnt):
  print('스크롤 {} 번째 진행 중...'.format(i+1))
  # scroll to bottom
  driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') # 맨 아래로 스크롤
  time.sleep(1)
  driver.execute_script('window.scrollTo(0, document.body.scrollHeight-1200);') # 위로 살짝 스크롤(더보기 버튼이 화면에 있어야 누를 수 있다)
  time.sleep(5)

  # click 'Load more' button, if exists
  try:
    load_more = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div/span/span')
    load_more.click()
    print('button click!!!')
  except:
    print('Cannot find load more button...')

# get review containers
reviews = driver.find_elements_by_xpath('//*[@jsname="fk8dgd"]//div[@class="d15Mdf bAhLNe"]')

print('There are %d reviews avaliable!' % len(reviews))
print('Writing the data...')

# create empty dataframe to store data
df = pd.DataFrame(columns=['name', 'ratings', 'date', 'helpful', 'comment'])

# get review data(beautifulsoup 사용)
for review in reviews:
  # parse string to html using bs4
  soup = BeautifulSoup(review.get_attribute('innerHTML'), 'html.parser')

  # reviewer
  name = soup.find(class_='X43Kjb').text

  # rating
  ratings = int(soup.find('div', role='img').get('aria-label').replace('별표 5개 만점에', '').replace('개를 받았습니다.', '').strip())

  # review date
  date = soup.find(class_='p2TkOb').text
  date = datetime.strptime(date, '%Y년 %m월 %d일')
  date = date.strftime('%Y-%m-%d')

  # helpful
  helpful = soup.find(class_='jUL89d y92BAb').text
  if not helpful:
    helpful = 0
  
  # review text
  comment = soup.find('span', jsname='fbQN7e').text
  if not comment:
    comment = soup.find('span', jsname='bN97Pc').text
  
  # 개발자 답변
  developer_comment = None
  dc_div = soup.find('div', class_='LVQB0b')
  if dc_div:
    developer_comment = dc_div.text.replace('\n', ' ')
  
  # append to dataframe
  df = df.append({
    'name': name,
    'ratings': ratings,
    'date': date,
    'helpful': helpful, # 유용한 리뷰
    'comment': comment
    'developer_comment': developer_comment
  }, ignore_index=True)

# csv파일로 저장
filename = 'V4.csv'
df.to_csv(filename, encoding='utf-8-sig', index=False)
driver.stop_client()
driver.close()
print('Done!')