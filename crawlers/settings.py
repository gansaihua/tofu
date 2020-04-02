BOT_NAME = 'hello'

SPIDER_MODULES = ['crawlers.spiders']
NEWSPIDER_MODULE = 'crawlers.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False


ITEM_PIPELINES = {
    'crawlers.pipelines.SQLPipeline': 300,
}

LOG_LEVEL = 'WARNING'
