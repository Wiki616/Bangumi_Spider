# -*- coding: utf-8 -*-

# Scrapy settings for bgm project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'bgmSpider'

SPIDER_MODULES = ['bgm.spiders']
NEWSPIDER_MODULE = 'bgm.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'bgm (+http://www.yourdomain.com)'
ITEM_PIPELINES = {
    'bgm.pipelines.BgmPipeline': 300,
}

MYSQL_HOST = 'localhost'
MYSQL_DBNAME = 'bgm'
MYSQL_USER = 'bgmer'
MYSQL_PASSWD = 'sai'

DOWNLOAD_DELAY = 0.25