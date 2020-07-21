import scrapy
import datetime
import re

class ArticleSpider(scrapy.Spider):
    name = 'articles'
    allowed_domains = ['rtbsquare.work']
    
    def __init__(self, start_date=None, end_date=None, crawl_start_pagenum=None, crawl_end_pagenum=None, *args, **kwargs):
        super(ArticleSpider, self).__init__(*args, **kwargs)
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        self.crawl_start_pagenum = int(crawl_start_pagenum)
        self.crawl_end_pagenum = int(crawl_end_pagenum)
        print("----- Crawling term : [ {} < ] AND [ <= {} ] -----".format(self.start_date, self.end_date))
    
    def start_requests(self):
        if self.start_date != self.end_date:
            yield scrapy.Request("https://rtbsquare.work/?paged=" + str(self.crawl_start_pagenum), callback=self.parse_list)

    def parse_list(self, response):
        repatter = re.compile(r'\D*(\d+)')
        articleDate = None
        for i in range(0, len(response.css('div.post h2'))):
            articleDate = datetime.datetime.strptime(response.css('div.post li::text')[i].get().strip(' '), "%Y/%m/%d").date()
            if(articleDate <= self.end_date and articleDate > self.start_date):
                yield scrapy.Request(response.css('div.post h2 a')[i].attrib['href'], callback=self.parse_article)
        a = response.css('div.pagination a.next')
        if((len(a) != 0) and (int(repatter.match(a.attrib['href']).group(1)) <= self.crawl_end_pagenum)):
            nextPage = response.urljoin(a.attrib['href'])
            yield scrapy.Request(nextPage, callback=self.parse_list)
        pass

    def parse_article(self, response):
        item = {}
        date = response.css('ul.post-by li::text').get()
        title = response.css('div.post .entry-title a::text').get()
        content = " ".join(response.css('div.post p::text').getall())
        tags = response.css('div.tags a::text').getall()
        
        item['url'] = response.url
        item['date'] = date
        item['title'] = title
        item['content'] = content
        item['tags'] = tags
        yield item
