# -*- coding: utf-8 -*-

# Scrapy settings for jd_comments_item project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'jd_comments_item'

SPIDER_MODULES = ['jd_comments_item.spiders']
NEWSPIDER_MODULE = 'jd_comments_item.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jd_comments_item (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'jd_comments_item.middlewares.JdCommentsItemSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'jd_comments_item.middlewares.JdCommentsItemDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'jd_comments_item.pipelines.JdCommentsItemPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DOWNLOADER_MIDDLEWARES = {
   'jd_comments_item.middlewares.MyproxiesSpiderMiddleware': 543,
    'jd_comments_item.middlewares.UserAgentMiddleware': 43,
}
HTTPERROR_ALLOWED_CODES = [302]

# 重新请求
RETRY_ENABLED = True
# 重试次数
RETRY_TIMES = 13
REDIRECT_ENABLED = False
DOWMLOAD_DELY=1

MYSQL_HOST = 'rm-bp1w32i5xm39t6cxd.mysql.rds.aliyuncs.com'
MYSQL_PORT = 3306
MYSQL_DBNAME = 'spider_data'
MYSQL_USER = 'marketing'
MYSQL_PASSWD = 'c131dVQYFqNI2rum'

CAT=['https://list.jd.com/list.html?cat=1320,5019,5020',
 'https://list.jd.com/list.html?cat=1320,5019,5021',
 'https://list.jd.com/list.html?cat=1320,5019,5022',
 'https://list.jd.com/list.html?cat=1320,5019,5023',
 'https://list.jd.com/list.html?cat=1320,5019,5024',
 'https://list.jd.com/list.html?cat=1320,5019,12215',
 'https://list.jd.com/list.html?cat=1320,1581,12217',
 'https://list.jd.com/list.html?cat=1320,1581,1589',
 'https://list.jd.com/list.html?cat=1320,1581,2644',
 'https://list.jd.com/list.html?cat=1320,1581,2647',
 'https://list.jd.com/list.html?cat=1320,1581,2648',
 'https://list.jd.com/list.html?cat=1320,1581,2653',
 'https://list.jd.com/list.html?cat=1320,1581,2656',
 'https://list.jd.com/list.html?cat=1320,1581,2669',
 'https://list.jd.com/list.html?cat=1320,1581,2670',
 'https://list.jd.com/list.html?cat=1320,1581,4693',
 'https://list.jd.com/list.html?cat=1320,1583,1590',
 'https://list.jd.com/list.html?cat=1320,1583,1591',
 'https://list.jd.com/list.html?cat=1320,1583,1592',
 'https://list.jd.com/list.html?cat=1320,1583,1593',
 'https://list.jd.com/list.html?cat=1320,1583,1594',
 'https://list.jd.com/list.html?cat=1320,1583,1595',
 'https://list.jd.com/list.html?cat=1320,1583,7121',
 'https://list.jd.com/list.html?cat=1320,1584,2675',
 'https://list.jd.com/list.html?cat=1320,1584,2676',
 'https://list.jd.com/list.html?cat=1320,1584,2677',
 'https://list.jd.com/list.html?cat=1320,1584,2678',
 'https://list.jd.com/list.html?cat=1320,1584,2679',
 'https://list.jd.com/list.html?cat=1320,1584,2680',
 'https://list.jd.com/list.html?cat=1320,1585,10975',
 'https://list.jd.com/list.html?cat=1320,1585,1602',
 'https://list.jd.com/list.html?cat=1320,1585,9434',
 'https://list.jd.com/list.html?cat=1320,1585,3986',
 'https://list.jd.com/list.html?cat=1320,1585,1601',
 'https://list.jd.com/list.html?cat=1320,1585,12200',
 'https://list.jd.com/list.html?cat=1320,1585,12201',
 'https://list.jd.com/list.html?cat=1320,2641,2642',
 'https://list.jd.com/list.html?cat=1320,2641,2643',
 'https://list.jd.com/list.html?cat=1320,2641,4935',
 'https://list.jd.com/list.html?cat=1320,2641,12216',
 'https://list.jd.com/list.html?cat=1320,12202,12203',
 'https://list.jd.com/list.html?cat=1320,12202,12204',
 'https://list.jd.com/list.html?cat=1320,12202,12205',
 'https://list.jd.com/list.html?cat=1320,12202,12206',
 'https://list.jd.com/list.html?cat=1320,12202,12207',
 'https://list.jd.com/list.html?cat=1320,12202,12208',
 'https://list.jd.com/list.html?cat=1320,12202,12209',
 'https://list.jd.com/list.html?cat=1320,12202,12210',
 'https://list.jd.com/list.html?cat=1320,12202,12211',
 'https://list.jd.com/list.html?cat=1320,12202,12212',
 'https://list.jd.com/list.html?cat=1320,12202,12213',
 'https://list.jd.com/list.html?cat=1320,12202,12214']