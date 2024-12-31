from selenium import webdriver
import re
import chardet

base = 'https://bqg123.net'
first_link = '/v3_uni_1231151?1#/v3/59162794/438626/793.html'

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
      browser.get(base + link)
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

def write_to_file(title, txt):
  if '章' in title:
    # parts = title.split(' ')
    # content = txt.replace(parts[0] + parts[1], '')
    context = txt + '\n\n\n'
    # 导出为 text 文件
    with open('左道倾天.txt', 'a+', encoding='utf-8') as f:
      f.write(context)


if __name__ == '__main__':
  scrape_page(first_link)
  title, txt, next_link = analyze_page()
  print('==' + title + '=================')
  write_to_file(title, txt)
  while next_link:
    scrape_page(next_link)
    title, txt, next_link = analyze_page()
    print('==' + title + '=================')
    write_to_file(title, txt)
  




  # (第\d+.*)(\n.)  # 匹配章节标题