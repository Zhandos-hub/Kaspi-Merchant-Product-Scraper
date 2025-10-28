# Kaspi Merchant Product Scraper

This project is a Python-based web scraper for collecting product data from **Kaspi.kz** merchant pages using **Selenium**. It emulates a mobile browser session to improve compatibility with the site layout and extracts key product details such as title, price, SKU, reviews, and links.


---

## Features

* Automated data extraction from Kaspi merchant listings
* Mobile emulation (iPhone SE viewport) for stable page layout
* Auto-scrolling to load all products dynamically
* Duplicate detection via SKU tracking
* Data export to Excel (`.xlsx`)
* Built-in logging for progress and errors

---

## Requirements

* **Python 3.8+**
* **Google Chrome** browser
* **ChromeDriver** (matching your Chrome version)

### Python Libraries

Install dependencies using pip:

```bash
pip install selenium pandas openpyxl
```

---

## Setup

1. Make sure **Google Chrome** is installed and the **ChromeDriver** version matches your Chrome browser.
2. Place `chromedriver` in your system PATH or in the same directory as the script.
3. Save the script file as `kaspi_scraper.py`.

---

## Usage

Run the script from your terminal or command prompt:

```bash
python kaspi_scraper.py
```

You will be prompted to enter a **Merchant ID**.
For example:

```
Enter the numerical Merchant ID (e.g., 30108317): [enter M_ID]
```
## How to get merchant ID?

To get a Merchant ID, open the mobile browser version of Kaspi Market (not the mobile app).
Then follow these steps:

1. Go to the merchant’s page.

2. Click the “See all products of merchant” button.

3. Look at the link in your browser’s address bar — it will look like this:
```
https://kaspi.kz/shop/search?redirect=listing&q=%3AallMerchants%{MERCHANT_ID}
```

5. Copy the numerical part that replaces {MERCHANT_ID}.
Be careful to copy only the number.

Example (you can include this if you want):
```
https://kaspi.kz/shop/search?redirect=listing&q=%3AallMerchants%30108317
```

Here, the Merchant ID is:

30108317

The scraper will then:

1. Launch a mobile Chrome session
2. Load all available product listings
3. Scroll through the page until no new products are found
4. Save the results to an Excel file named:

   ```
   kaspi_merchant_<merchant_id>.xlsx
   ```

Example output:

```
kaspi_merchant_30108317.xlsx
```

---

## Output Format

Each row in the generated Excel file includes:

| Field   | Description                     |
| ------- | ------------------------------- |
| Title   | Product name                    |
| SKU     | Unique product ID               |
| Price   | Product price in KZT (integer)  |
| Link    | Direct link to the product page |
| Reviews | Number of customer reviews      |

---


## Notes

* If the script fails to start, ensure that:

  * ChromeDriver is installed and accessible in PATH.
  * The Kaspi website structure has not changed.
* For large merchants, scraping may take several minutes depending on your internet speed and computer performance.

---

## License

This project is released under the MIT License.
You are free to use, modify, and distribute it for personal or commercial purposes.

~ designed & coded by Zhandos (ofc !without help of copilot)
