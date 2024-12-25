import asyncio
import aiohttp
import logging

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
# 列表页配置
INDEX_URL = 'https://spa5.scrape.center/api/book/?limit=18&offset={offset}'
# 详情页配置
DETAIL_URL = 'https://spa5.scrape.center/api/book/{id}'
# 每页数量
PAGE_SIZE = 18
# 总页数
PAGE_NUMBER = 100
# 并发数量
CONCURRENCY = 5

semaphore = asyncio.Semaphore(CONCURRENCY)
session = None

# == 链接爬取控制 ====================
async def scrape_api(url):
  async with semaphore:
    try:
      logging.info('正在爬取：%s', url)
      async with session.get(url) as response:
        return await response.json()
    except aiohttp.ClientError:
      logging.error('爬取失败：%s', url, exc_info=True)


# == 爬取列表页 ====================
async def scrape_index(page):
  url = INDEX_URL.format(offset=(page - 1) * PAGE_SIZE)
  return await scrape_api(url)


# == 连接 MongoDB ====================
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_CONNECTION_STRING = 'mongodb://localhost:27017'
MONGO_DB_NAME = 'books'
MONGO_COLLECTION_NAME = 'books'

client = AsyncIOMotorClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]


# == 保存数据 ====================
async def save_data(data):
  logging.info('保存数据：%s', data)
  if data:
    return await collection.update_one(
      {'id': data.get('id')},
      {'$set': data},
      upsert=True
    )


# == 爬取详情页 ====================
async def scrape_detail(id):
  url = DETAIL_URL.format(id=id)
  data = await scrape_api(url)
  await save_data(data)


# == 主函数 ====================
import json

async def main():
  global session
  session = aiohttp.ClientSession()
  scrape_index_tasks = [asyncio.ensure_future(scrape_index(page)) for page in range(1, PAGE_NUMBER + 1)]
  results = await asyncio.gather(*scrape_index_tasks)
  ids = []
  for index_data in results:
    if not index_data: continue
    for item in index_data.get('results', []):
      ids.append(item.get('id'))
  scrape_detail_tasks = [asyncio.ensure_future(scrape_detail(id)) for id in ids]
  await asyncio.wait(scrape_detail_tasks)
  await session.close()
  logging.info('爬取结果：%s', json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
  asyncio.get_event_loop().run_until_complete(main())






