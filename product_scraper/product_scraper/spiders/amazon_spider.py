from scrapy import Spider, Request

class AmazonSpider(Spider):
    name = "amazon_spider"
    allowed_domains = ["amazon.com"]
    start_urls = []

    def start_requests(self):
        query = getattr(self, 'query', None)
        if query:
            url = f"https://www.amazon.com/s?k={query}"
            yield Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    def parse(self, response):
        products = response.css('div[role="listitem"]')
        print("Products are: ", products)

        for product in products:
            title = product.css('h2[aria-label] span::text').get()
            price_whole = product.css('span.a-price-whole::text').get()
            price_fraction = product.css('span.a-price-fraction::text').get()
            image_url = product.css('img.s-image::attr(src)').get()
            
            if title and price_whole:
                price = f"{price_whole}.{price_fraction if price_fraction else '00'}"
                yield {
                    'title': title.strip(),
                    'price': price.strip(),
                    'image_url': image_url,
                    'source': "Amazon"
                }
