# src/main.py

import os
from browser_utils import setup_browser_with_proxy, navigate_to_url, safe_quit

def main():
    # Replace the proxy details with your own values
    proxy_details = {
        "host": "evo-pro.wiredproxies.com",
        "port": 61234,
        "user": "PP_ED1KDQX-country-US-session-r29x2WLns6AU-sessionduration-5",
        "pass": "gxuwyllk"
    }
    
    target_url = "https://safer.fmcsa.dot.gov/CompanySnapshot.aspx"

    # Setup browser with proxy
    driver = setup_browser_with_proxy(proxy_details)
    
    # Navigate to the target website
    driver = navigate_to_url(driver, target_url)
    
    # Optional: Print page title to confirm successful load
    print("Page title:", driver.title)
    
    # Wait for user input before closing
    input("Press Enter to exit and close the browser...")
    safe_quit(driver)

if __name__ == '__main__':
    main()
