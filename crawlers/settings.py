BOT_NAME = 'hello'

SPIDER_MODULES = ['crawlers.spiders']
NEWSPIDER_MODULE = 'crawlers.spiders'


ROBOTSTXT_OBEY = False


LOG_LEVEL = 'WARNING'
ITEM_PIPELINES = {
    'crawlers.pipelines.SQLPipeline': 300,
}
