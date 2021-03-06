import scrapy
import re
from bgm.items import Record, Index, Friend
from bgm.util import parsedate,getnextpage


class IndexSpider(scrapy.Spider):
    name='index'
    def __init__(self, *args, **kwargs):
        super(recordspider, self).__init__(*args, **kwargs)
        if not hasattr(self, 'id_max'):
            self.id_max=20000
        if not hasattr(self, 'id_min'):
            self.id_min=1
        self.start_urls = ["http://chii.in/index/"+str(i) for i in xrange(int(self.id_min),int(self.id_max))]

    def parse(self, response):
        if len(response.xpath(".//*[@id='columnSubjectBrowserA']/div[1]/a"))==0:
            return
        indexid = response.url.split('/')[-1]
        creator = response.xpath(".//*[@id='columnSubjectBrowserA']/div[1]/a/@href").extract()[0].split('/')[-1]
        td = response.xpath(".//*[@id='columnSubjectBrowserA']/div[1]/span/span[1]/text()").extract()[0]
        date = parsedate(td.split(' ')[0])
        favourite = response.xpath(".//*[@id='columnSubjectBrowserA']/div[1]/span/span[2]/text()").extract()[0]
        items = response.xpath(".//*[@id='columnSubjectBrowserA']/ul/li/@id").extract()
        items = [int(itm.split('_')[-1]) for itm in items]
        yield Index(indexid=indexid, creator=creator, favourite=favourite, date=date, items=items)

class RecordSpider(scrapy.Spider):
    name='record'
    def __init__(self, *args, **kwargs):
        super(recordspider, self).__init__(*args, **kwargs)
        if not hasattr(self, 'id_max'):
            self.id_max=300000
        if not hasattr(self, 'id_min'):
            self.id_min=1
        self.start_urls = ["http://chii.in/user/"+str(i) for i in xrange(int(self.id_min),int(self.id_max))]

    def parse(self, response):
        username = response.url.split('/')[-1]

        if len(response.xpath(".//*[@id='anime']")):
            yield scrapy.Request("http://chii.in/anime/list/"+username, callback = self.merge)

        if len(response.xpath(".//*[@id='game']")):
            yield scrapy.Request("http://chii.in/game/list/"+username, callback = self.merge)

        if len(response.xpath(".//*[@id='book']")):
            yield scrapy.Request("http://chii.in/book/list/"+username, callback = self.merge)

        if len(response.xpath(".//*[@id='music']")):
            yield scrapy.Request("http://chii.in/music/list/"+username, callback = self.merge)

        if len(response.xpath(".//*[@id='real']")):
            yield scrapy.Request("http://chii.in/real/list/"+username, callback = self.merge)



    def merge(self, response):
        followlinks = response.xpath(".//*[@id='headerProfile']/div/div[2]/ul//@href").extract() # a list of links
        for link in followlinks:
            yield scrapy.Request(u"http://chii.in"+link, callback = self.parse_recorder)

    def parse_recorder(self, response):
        name = response.url.split('/')[-2]
        state = response.url.split('/')[-1].split('?')[0]
        tp = response.url.split('/')[-4]

        items = response.xpath(".//*[@id='browserItemList']/li")
        for item in items:
            item_id = int(re.match(r"item_(\d+)",item.xpath("./@id").extract()[0]).group(1))
            item_date = parsedate(item.xpath("./div/p[@class='collectInfo']/span[@class='tip_j']/text()").extract()[0])
            if item.xpath("./div/p[@class='collectInfo']/span[@class='tip']"):
                item_tags = item.xpath("./div/p[@class='collectInfo']/span[@class='tip']/text()").extract()[0].split(u' ')[1:-1]
            else:
                item_tags=None

            try_match = re.match(r'sstars(\d+) starsinfo', item.xpath("./div/p[@class='collectInfo']/span[1]/@class").extract()[0])
            if try_match:
                item_rate = try_match.group(1)
            else:
                item_rate = None

            if item.xpath("./div/div[@id='comment_box']"):
                item_comment = item.xpath("./div/div[@id='comment_box']/div/div/div[1]/text()").extract()[0]
            else:
                item_comment = None

            watchRecord = Record(name=name,typ=tp,state=state,iid=item_id,date=item_date)
            if item_tags:
                watchRecord["tags"]=item_tags
            if item_rate:
                watchRecord["rate"]=item_rate
            if item_comment:
                watchRecord["comment"]=item_comment
            yield watchRecord

        if len(items)==24:
            request = scrapy.Request(getnextpage(response.url),callback = self.parse_recorder)
            yield request

class FriendsSpider(scrapy.Spider):
    name='friends'
    def __init__(self, *args, **kwargs):
        super(recordspider, self).__init__(*args, **kwargs)
        if not hasattr(self, 'id_max'):
            self.id_max=300000
        if not hasattr(self, 'id_min'):
            self.id_min=1
        self.start_urls = ["http://chii.in/user/"+str(i)+"/friends" for i in xrange(int(self.id_min),int(self.id_max))]

    def parse(self, response):
        user - response.url.split('/')[-2]
        lst = response.xpath(".//*[@id='memberUserList']/li//@href").extract()
        for itm in lst:
            yield Friend(user = user, friend = itm.split('/')[-1])
