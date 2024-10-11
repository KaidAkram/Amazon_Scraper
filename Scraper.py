from playwright.sync_api import sync_playwright
import agentql
from agentql.ext.playwright.sync_api import Page
import time
import pandas as pd

PRODUCT_DATA_QUERY = """
{
       products[]{
       product_name
       product_url
       product_image_url
       product_price
       product_rating
    
      
   }
}
"""


def _extract_product_data(page: Page) -> dict:
    """Extract product data from the page using AgentQL."""
    data = page.query_data(PRODUCT_DATA_QUERY, mode="fast")
    return data

def scroll_and_collect_data(page: Page, scroll_count: int) -> list:
    """Scroll the page and collect product data."""
    all_product_data = []

    for _ in range(scroll_count):
        products_data = _extract_product_data(page)
        all_product_data.extend(products_data["products"])  
        
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)  

    return all_product_data

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = agentql.wrap(browser.new_page())
    page.goto("https://www.amazon.co.uk/gp/bestsellers/?ref_=nav_cs_bestsellers")
    page.wait_for_load_state("networkidle")
    scroll_count = 2  
    products_data = scroll_and_collect_data(page, scroll_count)
    print(products_data)
    browser.close()
    
    
df = pd.DataFrame(products_data)
df.to_csv('data.csv')
