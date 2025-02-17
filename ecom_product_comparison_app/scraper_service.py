import subprocess
import json
import os
import time

class ScraperService:
    def scrape_products(self, query):
        results = []

        # Unique filename to avoid duplicate feed errors
        timestamp = int(time.time())
        spider_names = ["flipkart_spider", "amazon_spider"]

        for spider_name in spider_names:
            spider_output = f"output_{spider_name}_{timestamp}.json"
            output_path = os.path.join("product_scraper", spider_output)

            # Run Scrapy spider
            process = subprocess.run(
                ["scrapy", "crawl", spider_name, "-o", spider_output, "-a", f"query={query}"],
                cwd="product_scraper"
            )

            # Check if the spider ran successfully
            if process.returncode == 0:
                try:
                    # Ensure file has finished writing before reading
                    time.sleep(1)
                    with open(output_path, "r") as file:
                        scraped_data = json.load(file)
                        print(f"Scraped data from {spider_name}: ", scraped_data)

                        # Format the data
                        formatted_data = [
                            {
                                "name": item.get("title", "No title available"),
                                "price": item.get("price", "N/A"),
                                "image": item.get("image_url", "https://via.placeholder.com/150"),
                                "source": spider_name.replace("_spider", "").capitalize(),
                                "stores": [spider_name.replace("_spider", "").capitalize()]
                            }
                            for item in scraped_data
                        ]

                        results.extend(formatted_data)

                except (FileNotFoundError, json.JSONDecodeError):
                    print(f"Error reading {spider_output}. Spider may have failed.")
            else:
                print(f"Error: Spider '{spider_name}' failed to execute.")

            # Cleanup the JSON file after processing
            if os.path.exists(output_path):
                os.remove(output_path)

        print("Final Scraped Results:", results)
        return results
