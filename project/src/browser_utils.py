# src/browser_utils.py

import undetected_chromedriver as uc
from extension.build_extension import create_proxy_extension

def setup_browser_with_proxy(proxy_details):
    """
    Creates an undetected ChromeDriver instance using a proxy extension.
    """
    # Create the proxy extension directory
    extension_dir = create_proxy_extension(
        proxy_details['host'],
        proxy_details['port'],
        proxy_details['user'],
        proxy_details['pass']
    )

    # Set up Chrome options to load the proxy extension
    options = uc.ChromeOptions()
    options.add_argument(f'--load-extension={extension_dir}')
    options.add_argument("--window-size=1920,1080")

    # Initialize and return the driver
    driver = uc.Chrome(options=options)
    return driver

def navigate_to_url(driver, url, max_load_time=10):
    """
    Navigates to the given URL. If the page does not load within the timeout,
    it attempts to stop further loading.
    """
    driver.set_page_load_timeout(max_load_time)
    try:
        driver.get(url)
        print("Page loaded successfully.")
    except Exception as e:
        print("Error loading page:", e)
        try:
            driver.execute_script("window.stop();")
            print("Stopped page load.")
        except Exception as e:
            print("Error stopping page load:", e)
    return driver

def safe_quit(driver):
    """
    Attempts to safely quit the driver.
    """
    if driver:
        try:
            driver.quit()
        except Exception as e:
            print("Error quitting driver:", e)
