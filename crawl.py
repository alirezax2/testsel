import os, time
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://gurufocus.com/stock/GOOGL/summary"
OUT = Path("artifacts")

def make_driver():
    OUT.mkdir(parents=True, exist_ok=True)

    # Use Chrome installed by the workflow (if present)
    chrome_path = os.environ.get("CHROME_PATH") or os.environ.get("GOOGLE_CHROME_BIN")

    opts = uc.ChromeOptions()
    # Headless “new” is implied when running headless on recent Chrome
    # Toggle headful locally by setting HEADFUL=1
    headful = os.environ.get("HEADFUL", "0") == "1"
    if not headful:
        opts.add_argument("--headless=new")

    # Hardening for CI stability
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")

    # Realistic UA; UC already randomizes/stealths, but this helps consistency
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )

    if chrome_path:
        # UC supports passing the Chrome binary path explicitly
        driver = uc.Chrome(options=opts, browser_executable_path=chrome_path)
    else:
        driver = uc.Chrome(options=opts)

    # Optional: small human-ish delays between actions
    driver.implicitly_wait(0.2)
    return driver

def wait_past_cloudflare(driver, timeout=45):
    """
    Try to wait out CF's JS challenge if shown.
    Looks for common patterns like 'Just a moment...' or challenge iframes.
    """
    end = time.time() + timeout
    while time.time() < end:
        html = driver.page_source.lower()
        if ("just a moment" in html) or ("checking your browser" in html) or ("cf-chl-widget" in html):
            time.sleep(2)
            continue
        # Body is present and no obvious CF text; consider it passed
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        except Exception:
            time.sleep(1)
    return False

def main():
    driver = make_driver()
    try:
        driver.get(URL)

        # Let Cloudflare do its thing
        if not wait_past_cloudflare(driver, timeout=60):
            print("Warning: Cloudflare challenge may not be fully passed; saving anyway.")

        # Give heavy JS a moment to render
        time.sleep(3)

        # Save results
        (OUT / "page.html").write_text(driver.page_source, encoding="utf-8")
        driver.save_screenshot(str(OUT / "page.png"))
        print("Saved:", (OUT / "page.html").resolve(), (OUT / "page.png").resolve())

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
