import subprocess
import json
import os
import time
from django.conf import settings

class ScraperService:
    def scrape_products(self, query):
        try:
            results = []
            timestamp = int(time.time())
            spider_names = ["flipkart_spider", "amazon_spider"]
            
            # Get the product_scraper directory path
            scraper_dir = os.path.join(settings.BASE_DIR, 'product_scraper')
            
            for spider_name in spider_names:
                print("This spider is: ", spider_name)
                spider_output = f"output_{spider_name}_{timestamp}.json"
                output_path = os.path.join(scraper_dir, spider_output)
                
                print(f"Running spider: {spider_name}")
                print(f"Output path: {output_path}")
                print(f"Working directory: {scraper_dir}")

                # Run the spider
                process = subprocess.Popen(
                    [
                        "scrapy", "crawl", spider_name,
                        "-a", f"query={query}",
                        "-o", output_path
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=scraper_dir
                )
                stdout, stderr = process.communicate()
                
                print(f"Spider output: {stdout.decode()}")
                print(f"Spider errors: {stderr.decode()}")

                if process.returncode == 0:
                    try:
                        if os.path.exists(output_path):
                            with open(output_path, 'r') as f:
                                spider_data = json.load(f)
                                print(f"Loaded data from {output_path}: {len(spider_data)} products")
                                results.extend(spider_data)
                        else:
                            print(f"Output file not found: {output_path}")
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        print(f"Error processing {spider_output}: {str(e)}")
                else:
                    print(f"Spider {spider_name} failed with return code {process.returncode}")
                    print(f"Error: {stderr.decode()}")

                # Cleanup
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"Cleaned up {output_path}")

            print(f"Total scraped products: {len(results)}")
            return results

        except Exception as e:
            print(f"Scraping error: {str(e)}")
            return []
