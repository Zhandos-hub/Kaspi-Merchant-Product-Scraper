import time
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict, Set, Optional

# SETTINGS
# Set up logging to see errors and progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get merchant ID from user input
MERCHANT_ID = input("Enter the numerical Merchant ID (e.g., 30108317): ").strip()
USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; Mobile; rv:89.0) "
    "Gecko/89.0 Firefox/89.0"
)
WINDOW_SIZE = "360,640"
BASE_URL = f"https://kaspi.kz/shop/search?redirect=listing&q=%3AallMerchants%{MERCHANT_ID}"


# How many times to scroll without finding new items before stopping
# Sometimes new items take a while to load, so we allow a few empty scrolls
MAX_EMPTY_SCROLLS = 3

def create_driver() -> webdriver.Chrome:
    """
    Initializes and returns a Chrome webdriver with mobile emulation.
    """
    logging.info("Initializing Chrome driver with mobile emulation...")
    mobile_emulation = {"deviceName": "iPhone SE"}
    options = Options()
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument(f"--window-size={WINDOW_SIZE}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    
    try:
        # Assumes "chromedriver" is in your systems PATH
        service = Service() 
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logging.error(f"Failed to create webdriver. Is chromedriver in your PATH? Error: {e}")
        return None

def parse_card(card: WebElement) -> Optional[Dict]:
    """
    Extracts product data from a single item card element.
    Returns a dictionary or None if essential data (like SKU) is missing.
    """
    title = price_int = link = sku = reviews = None

# Extract title
    try:
        title = card.find_element(By.CSS_SELECTOR, ".product-card-header__title").text
    except NoSuchElementException:
        logging.warning("Could not find title for a card.")
        pass  # Title is not essential
# Extract price
    try:
        price_str = card.find_element(By.CSS_SELECTOR, ".product-card-price__origin").text
        price_int = int(''.join(filter(str.isdigit, price_str)))
    except NoSuchElementException:
        logging.warning(f"Could not find price for item: {title or 'Unknown'}")
        pass # Price is not essential
# Extract link and SKU
    try:
        link = card.get_attribute("href")
        sku = link.split("-")[-1].split("/")[0]
        if not sku.isdigit(): # Basic validation
             raise ValueError("Extracted SKU is not valid.")
    except (AttributeError, IndexError, ValueError):
        logging.warning(f"Could not extract a valid SKU from link: {link}")
        return None  # SKU is essential, skip this card
# Extract reviews
    try:
        reviews_str = card.find_element(By.CSS_SELECTOR, ".product-card-rating__reviews-quantity").text
        reviews = int(reviews_str.strip("()").split()[0])
    except (NoSuchElementException, IndexError, ValueError):
        reviews = 0  # Default to 0 if reviews are not found

    return {
        "Title": title,
        "SKU": sku,
        "Price": price_int,
        "Link": link,
        "Reviews": reviews
    }

def scroll_and_parse(driver: webdriver.Chrome, all_data: List[Dict], seen_skus: Set[str]):
    """
    Performs deep scrolling, parses new items, and stops when no new items are found.
    """
    scroll_pause = 1.5
    empty_scroll_attempts = 0

    while True:
        time.sleep(scroll_pause)
        
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, ".list-product-card")
        except NoSuchElementException:
            logging.warning("No item cards found on this scroll.")
            time.sleep(scroll_pause) 
            continue

        new_items_found_count = 0
        for card in cards:
            product_data = parse_card(card)
            
            if product_data and product_data["SKU"] not in seen_skus:
                seen_skus.add(product_data["SKU"])
                all_data.append(product_data)
                new_items_found_count += 1
                logging.info(
                    f"{len(all_data)}. {product_data['Title']} | "
                    f"Price: {product_data['Price']} | Reviews: {product_data['Reviews']}"
                )

        logging.info(f"Scroll: Found {new_items_found_count} new items...")

        if new_items_found_count == 0:
            empty_scroll_attempts += 1
            if empty_scroll_attempts >= MAX_EMPTY_SCROLLS:
                logging.info("No new products found after several scrolls. Stopping.")
                break
        else:
            empty_scroll_attempts = 0  # Reset counter if new items were found

        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def save_to_excel(data: List[Dict], filename: str):
    """
    Saves the collected data to an Excel file.
    """
    if not data:
        logging.warning("No data was collected. Excel file will not be created.")
        return
        
    logging.info(f"Saving {len(data)} items to {filename}...")
    try:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        logging.info(f"Successfully saved data to {filename}")
    except Exception as e:
        logging.error(f"Failed to save data to Excel: {e}")

def main():
    """
    Main function to orchestrate the scraping process.
    """
    driver = create_driver()
    if not driver:
        logging.error("Driver creation failed. Exiting.")
        return

    all_data: List[Dict] = []
    seen_skus: Set[str] = set()

    try:
        logging.info(f"Opening page: {BASE_URL}")
        driver.get(BASE_URL)
        # Wait for the initial product card to be visible
        logging.info("Waiting for the first product card to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".list-product-card"))
        )
        logging.info("Page loaded. Starting deep scroll...")
        scroll_and_parse(driver, all_data, seen_skus)

    except TimeoutException:
        logging.error("Error: Page timed out or failed to load the initial content.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}")
    finally:
        try:
            driver.quit()
            logging.info("Driver has been closed.")
        except Exception as e:
            logging.error(f"Error while closing driver: {e}")

    # Save results to Excel
    filename = f"kaspi_merchant_{MERCHANT_ID}.xlsx"
    save_to_excel(all_data, filename)
    
    print(f"\nDone! Total unique products found: {len(all_data)}.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

