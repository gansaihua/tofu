BOT_NAME = 'tofu'

SPIDER_MODULES = ['crawlers.spiders']
NEWSPIDER_MODULE = 'crawlers.spiders'


ROBOTSTXT_OBEY = False

LOG_LEVEL = 'WARNING'
ITEM_PIPELINES = {
    'crawlers.pipelines.FuturesPipeline': 800,
    'crawlers.pipelines.StockPipeline': 800,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,

    # 'crawlers.middlewares.ProxyMiddleware': 110,
}
