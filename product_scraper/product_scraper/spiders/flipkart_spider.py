from scrapy import Spider, Request

class FlipkartSpider(Spider):
    name = "flipkart_spider"
    allowed_domains = ["flipkart.com"]

    def start_requests(self):
        query = getattr(self, 'query', None)
        if query:
            url = f"https://www.flipkart.com/search?q={query}"
            self.logger.info(f"Starting Flipkart spider with URL: {url}")
            yield Request(
                url=url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                callback=self.parse,
                errback=self.errback_httpbin,
                dont_filter=True
            )
        else:
            self.logger.error("No query provided!")

    def errback_httpbin(self, failure):
        self.logger.error(f"Request failed: {failure.value}")

    def parse(self, response):
        self.logger.info(f"Parsing Flipkart response: {response.url}")
        products = response.css('div.cPHDOP')
        self.logger.info(f"Found {len(products)} products")

        for product in products:
            title = product.css('div.KzDlHZ::text').get()
            price = product.css('div.Nx9bqj::text').get()
            image_url = product.css('img.DByuf4::attr(src)').get()
            rating = product.css('div._3LWZlK::text').get()

            if title and price:
                # Remove "₹" and commas from price and convert to float for consistency
                clean_price = price.replace("₹", "").replace(",", "").strip()
                rating_value = float(rating) if rating else 0
                
                yield {
                    'name': title.strip(),
                    'price': clean_price,
                    'image': response.urljoin(image_url) if image_url else None,
                    'rating': rating_value,
                    'url': response.urljoin(product.css('a._1fQZEK::attr(href)').get()),
                    'source': "Flipkart"
                }
                print("product is flip:", title)

        # Handle pagination
        next_page = response.css('a._1LKTO3::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
