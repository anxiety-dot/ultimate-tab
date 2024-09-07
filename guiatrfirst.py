import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Uncomment if you don't need a visible browser

# Initialize WebDriver (assuming chromedriver is in your system path)
driver = webdriver.Chrome(options=chrome_options)

# Open the site to set cookies
driver.get("https://www.ultimate-guitar.com")

# Load cookies from cookies.txt
def load_cookies_from_file(file_path):
    cookies = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    cookie = {
                        'domain': parts[0],
                        'name': parts[5],
                        'value': parts[6],
                        'path': parts[2],
                        'secure': parts[3] == 'TRUE'
                    }
                    cookies.append(cookie)
                else:
                    print(f"Skipping line due to insufficient parts: {line.strip()}")
    return cookies

cookies = load_cookies_from_file('cookie.txt')
for cookie in cookies:
    driver.add_cookie(cookie)

# Refresh to apply cookies
driver.refresh()

# Navigate to the page you want to scrape
driver.get("https://www.ultimate-guitar.com/user/mytabs")

# Wait for the "All" button to appear and click it
try:
    all_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "lNgmp"))
    )
    all_button.click()  # Click the "All" button
    
    # Optional: Delay after clicking to allow page content to load
    time.sleep(5)  # Increase this if necessary

    # Scroll to the bottom of the page to load all dynamic content
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page
        time.sleep(3)  # Adjust time depending on loading speed
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Wait for the content to load after scrolling
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "LRSRs"))
    )
    
    # Scrape the links after scrolling and loading all content
    elements = driver.find_elements(By.CSS_SELECTOR, 'div.LRSRs a[href]')
    filtered_urls = [elem.get_attribute('href') for elem in elements if 'chords' in elem.get_attribute('href')]

    # Write filtered URLs to a file
    with open('filtered_links.txt', 'w') as file:
        for url in filtered_urls:
            file.write(url + '\n')

    print(f"Filtered URLs written to 'filtered_links.txt'.")
except Exception as e:
    print(f"An error occurred: {e}")

driver.quit()
