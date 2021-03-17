import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from onvista.items import Article


class OnvistaSpider(scrapy.Spider):
    name = 'onvista'
    start_urls = ['https://www.onvista.de/news/alle-news/']
    news_limit = 2000
    news = 0

    def parse(self, response):
        if self.news > self.news_limit:
            return

        links = response.xpath('//span[@class=" headline-medium"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="WEITER"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()
        else:
            return

        self.news += 1

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@property="schema:articleBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
