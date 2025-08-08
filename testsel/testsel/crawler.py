from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://gurufocus.com/stock/GOOGL/summary"

def make_driver():
    opts = Options()
    # Headless, but new mode (better JS support)
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    
    # Pretend to be a real Chrome on Windows
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    
    # Disable Selenium automation flags
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=opts)

    # Remove navigator.webdriver flag
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """
        },
    )
    return driver

def main():
    out = Path("artifacts")
    out.mkdir(parents=True, exist_ok=True)

    driver = make_driver()
    try:
        driver.get(URL)

        # Wait for body (or a specific selector if needed)
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Extra wait if Cloudflare challenge might show
        time.sleep(5)

        (out / "page.html").write_text(driver.page_source, encoding="utf-8")
        driver.save_screenshot(str(out / "page.png"))
        print("Saved:", (out / "page.html").resolve(), (out / "page.png").resolve())

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
