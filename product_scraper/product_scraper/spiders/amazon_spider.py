from scrapy import Spider, Request

class AmazonSpider(Spider):
    name = "amazon_spider"
    allowed_domains = ["amazon.com"]
    start_urls = []

    def start_requests(self):
        query = getattr(self, 'query', None)
        if query:
            url = f"https://www.amazon.com/s?k={query}"
            self.logger.info(f"Starting Amazon spider with URL: {url}")
            yield Request(
                url=url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                callback=self.parse,
                errback=self.errback_httpbin,
                dont_filter=True
            )

    def errback_httpbin(self, failure):
        self.logger.error(f"Request failed: {failure.value}")

    def parse(self, response):
        self.logger.info(f"Parsing Amazon response: {response.url}")
        products = response.css('div[data-component-type="s-search-result"]')
        
        for product in products:
            yield {
                'name': product.css('h2 a span::text').get(),
                'price': product.css('.a-price-whole::text').get('0'),
                'url': response.urljoin(product.css('h2 a::attr(href)').get()),
                'image': product.css('img.s-image::attr(src)').get(),
                'rating': product.css('.a-icon-star-small .a-icon-alt::text').re_first(r'(\d+\.?\d*)'),
                'source': 'Amazon'
            }
            print("product is:  amazon", product)
