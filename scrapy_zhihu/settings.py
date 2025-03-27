# -*- coding: utf-8 -*-
BOT_NAME = 'scrapy_zhihu'

SPIDER_MODULES = ['scrapy_zhihu.spiders']
NEWSPIDER_MODULE = 'scrapy_zhihu.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2

# The path of downloading
DOWNLOAD_PATH = 'D:\\scrapy_zhihu\\data\\'
COOKIES_ENABLED = False
# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Priority': 'u=0, i',
    'Cookie': 'q_c1=2cffd82328ad49fa92675f841c0eb7b7|1741524998000|1741524998000; __snaker__id=f7SsrSSRtN6uNJ99; d_c0=KrLTaDXSHhqPTugEC6m1OBhzIZgE7qap80c=|1741524969; _zap=884a7f22-b425-43ab-8813-d2217cbda179; gdxidpyhxdE=IxfdNC9gMs5lNlKR6Kmlm8X7TNivpxajp0fpqYzhL4gWeAC6hv%2Futag%5CZZpdEvQjtuXBpcvuHSlneXpXzTa%2BR8c8%2Fr7Ws47VATvrekhzk62yp6MiVRPDOUjH49R%2Fhff%2Bae6I6a8kTOZKNpDlS2AJKD6xZU%2FX0OaV6dby4ix%2BzJ0%2B4XOD%3A1742218717209; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1741524965,1742217395,1742217813,1742217827; captcha_session_v2=2|1:0|10:1742217833|18:captcha_session_v2|88:V1N2eFY0ViswNi9pVnZ6aWoyOS80NVhTb2wrTm9zV0VxbVhsV0twcm03WVJETnVITFFVNk0xdVNtVTRxbjBWbQ==|14b4f566e9efecc74c876bbfefea8d2e0d73c350c7bc6fe6fef9caa6f4ea85dd; captcha_ticket_v2=2|1:0|10:1742217848|17:captcha_ticket_v2|728:eyJ2YWxpZGF0ZSI6IkNOMzFfWDY0Mk9iX1RWSC5VTVdDVVZ0UXl2aTREQVFLcm5lVXZjeGdDMG9xRkowckMqcEhXNnhjRnZjUFhBbmE0cGRCb3ozNmN6eU96V2FZUWZaTlpDQ0R4QVFSTjR2clY4QVZXZzFOQU1kY3BOa1oxSXZ0SzBiWHlwT3c5NUlOUENmbXg5WF9XOFFUMm9WM3o0TmFqYjlvVGtVYUEwcVZoKlFKOC5LUVNNcmhiZ1MqZ3hpX0pRZ3drVDVkOHdNTzhnMTNGd3VGVUpFb2pWelRFdzhJQnF0SzlEcnFFVHgyYkN2SSpqLkFWc01FdVYyV1NFakhsUUpGWWcuVy5IZFIuWWNNQ2lsaTBGeHRodmJNUmh6Lnk0VjMweXN0YWFxZFlOT1FyYlRuUWxFamZzamJycFZXTDllWldLM2RoNi56SCpBZzlULkVoT3MqKm9IUnd1X2VZLl84cUVhZXMyZzBYRXg2ZlJLeHVaS3Z1RWpaWVNwOEJZOTZyTE1wQVUxTElORzFUMjBQMm5BMGlUZ2Z1YVBOSnY5V2xidWpzTjRJWU1PQ1JqcEtaLm1GWVhlNGpGRFJmMWd6S2s4SGp4MExBTFFacUl2MlVxWXdtYTR5bmVyQU5uV2VMSjNUNnNyRWhQNVptbE4xTjZQeEpyc2pxSXZTclpVUVdOclZ0NU0zVGgyVEFURHdHOFk3N192X2lfMSJ9|77d2e3e74ac07b4f5ccc6e845bac39b3e854f1ab985523e7ce87dad42c68f2ef; z_c0=2|1:0|10:1742217848|4:z_c0|92:Mi4xVGRUa0xBQUFBQUFxc3ROb05kSWVHaVlBQUFCZ0FsVk5lSERGYUFEN19IdWx3UWZGSDBlZFNoTTFET2c0SVFacTRn|baa0232c802eab1b898bcf5a17fcbc4c929f3b460a5fa574ad3ffb7930c583fd; _xsrf=6835ee7a-c5f7-4e95-b7db-2a9c36b49a04; HMACCOUNT=C038F0EC6F6CF6DA; BEC=6bca8f185b99e85d761c7a0d8d692864; tst=r; SESSIONID=9elxd7kxzyhfEHHjs57N3mALee0K3pneOQJmNgGD2ae; JOID=Ul8SBk788GAPkEpNW7BjNMCnnVFGwpUOd_F6JiGDjghr1QcCMTpavm2STU9ZwIl5NvvGE-4wFPchBm9ViKmP5Ys=; osd=U1AVAkr9_2cLlEtCXLRnNc-gmVVHzZIKc_B1ISWHjwds0QMDPj1eumydSktdwYZ-Mv_HHOk0EPYuAWtRiaaI4Y8=; __zse_ck=004_U5BNyOQ=K=1LjCYsgVogQFNooU1Bzpfnvxann09hzEM8Ek/My93qigV7eGnqO/E4Z/AIk4eyUgYpkYZUEsvOGvTxB2Ltbx5NAnKnBigTs=X34mYpcz0SwblUdOfu/HUS-YhOYtelcA4gMKNmPgGlJz97RYNJTcvSDbMgh4+2tOvM0Aemz7E4xwa26c5nEAaSArW5+/9ZAlnadwJ25rSpPxIPM2hNNhARmxPB8tasAWbc8HGOWkWPgtAVSwc9JUTMO; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1742514448',
}
#USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_zhihu.pipelines.MyPipeline': 300,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy_zhihu.middlewares.RandomUserAgentMiddlware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

LOG_LEVEL = 'DEBUG'
LOG_FILE = 'scrapy_DEBUG.log' 
RANDOM_UA_TYPE = 'random'

# These IPs are samples to fetch data.
IP_LIST = [
    #"http://65.21.79.163:7777",
    # "http://14.109.107.1:8998",
    # "http://106.46.136.159:808",
    # "http://175.155.24.107:808",
    # "http://124.88.67.10:80",
    # "http://124.88.67.14:80",
    # "http://58.23.122.79:8118",
    # "http://123.157.146.116:8123",
    # "http://124.88.67.21:843",
    # "http://106.46.136.226:808",
    # "http://101.81.120.58:8118",
    # "http://180.175.145.148:808"
]

# Store the data in mongo db.
MONGO_URI = 'URI of your mongodb'
DB_NAME = 'zhihu'
USER_NAME = 'Your name'
PASSWORD = 'xxx'
USE_DB = False