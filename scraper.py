from selenium import webdriver
import re
import chardet

BASE = 'https://bqg123.net'
FIRST_LINK = '/v3_uni_0110101?2#/v3/27542350/403316/994.html'
FILE_NAME = '蛊真人.txt'

ALL_CHAPTERS = []

# 配置无头模式
option = webdriver.ChromeOptions()
option.add_argument('--headless')
browser = webdriver.Chrome(options=option)

# 获取下一页的 link
# findNextPage = re.compile(r'< id="pb_next" class="chapter" rel="nofollow" href="(.*?)">')

# 爬取页面内容
def scrape_page(link):
  try:
    if not link.startswith('http'):
      browser.get(BASE + link)
    else:
      browser.get(link)
  except:
    print('Error: 无法访问页面')
    print(link)

def analyze_page():
  # 获取章节内容
  content = browser.find_element('id', 'nr1')
  # 获取标题
  title = browser.find_element('id', 'nr_title')
  # 获取下一页的 link
  # next_link = findNextPage.search(browser.page_source).group(1)
  next_link = browser.find_element('id', 'pb_next').get_attribute('href')
  return title.text, content.text, next_link

def write_to_file(title, txt, link):
  print('==' + title + '=================')
  if title in ALL_CHAPTERS:
    print('重复章节')
    return
  ALL_CHAPTERS.append(title)
  if '序' in title or '节' in title:
    context = txt + '\n\n'
    # 导出为 text 文件
    with open(FILE_NAME, 'a+', encoding='utf-8') as f:
      f.write(context)
  else:
    print(link)


if __name__ == '__main__':
  scrape_page(FIRST_LINK)
  title, txt, next_link = analyze_page()
  write_to_file(title, txt, next_link)
  while next_link:
    current_link = browser.current_url
    scrape_page(next_link)
    title, txt, next_link = analyze_page()
    write_to_file(title, txt, current_link)
  




  # (第\d+.*)(\n.)  # 匹配章节标题