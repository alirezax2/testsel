import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

# Configure Chrome for GitHub Actions headless
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=opts)

try:
    ticker = "MSFT"
    url = f"https://gurufocus.com/stock/{ticker}/summary"
    driver.get(url)

    # Wait until page loads — adjust selector if you want specific element
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Save HTML to a file
    Path("artifacts").mkdir(exist_ok=True)
    html_path = Path(f"artifacts/{ticker}.html")
    html_path.write_text(driver.page_source, encoding="utf-8")

    print(f"HTML saved to {html_path.resolve()}")

finally:
    driver.quit()

