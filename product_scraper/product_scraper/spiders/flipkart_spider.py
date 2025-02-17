from scrapy import Spider, Request

class FlipkartSpider(Spider):
    name = "flipkart_spider"
    allowed_domains = ["flipkart.com"]

    def start_requests(self):
        base_url = "https://www.flipkart.com/search?q="
        query = getattr(self, 'query', None)
        
        if query:
            url = base_url + query
            print("Here is url: ", url)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            yield Request(url=url, headers=headers, callback=self.parse)
        else:
            self.logger.error("No query provided!")

    def parse(self, response):
        products = response.css('div.cPHDOP')
        print("Here is product details: ", len(products))

        for product in products:
            title = product.css('div.KzDlHZ::text').get()
            price = product.css('div.Nx9bqj::text').get()
            image_url = product.css('img.DByuf4::attr(src)').get()

            if title and price:
                # Remove "₹" and commas from price and convert to float for consistency
                clean_price = price.replace("₹", "").replace(",", "").strip()
                
                yield {
                    'title': title.strip(),
                    'price': clean_price,
                    'image_url': response.urljoin(image_url),
                    'source': "Flipkart"
                }

        # Handle pagination
        next_page = response.css('a._1LKTO3::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
