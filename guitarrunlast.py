import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
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
        EC.element_to_be_clickable((By.XPATH, "//div[text()='All']"))
    )
    all_button.click()  # Click the "All" button
    
    # Optional: Delay after clicking to allow page content to load
    time.sleep(5)  # Increase this if necessary

    # Scroll to the bottom of the page to load all dynamic content
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Adjust time depending on loading speed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "LRSRs"))
    )
    
    elements = driver.find_elements(By.CSS_SELECTOR, 'div.LRSRs a[href]')
    filtered_urls = [elem.get_attribute('href') for elem in elements if 'chords' in elem.get_attribute('href')]

    os.makedirs('songs', exist_ok=True)

    for url in filtered_urls:
        try:
            driver.get(url)  # Visit the URL
            
            # Extract the page source and use BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract text from <h1> for the filename
            try:
                h1_element = soup.find('h1')
                h1_text = h1_element.get_text(strip=True)
                # Sanitize the filename
                file_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', f"{h1_text}.txt")
            except Exception as e:
                print(f"Failed to get <h1> text for URL {url}: {e}")
                file_name = "unknown.txt"

            # Limit filename length to avoid exceeding max length
            if len(file_name) > 255:  # Adjust this limit if needed
                file_name = file_name[:255]

            # Extract content from <pre> element (adjust the selector if needed)
            try:
                pre_element = soup.find('pre', class_='tK8GG Ty_RP')
                song_content = pre_element.get_text(strip=True) if pre_element else "Content not found."
            except Exception as e:
                print(f"Failed to extract content from URL {url}: {e}")
                song_content = "Content not found."

            # Save content to a file with <h1> text as filename
            with open(os.path.join('songs', file_name), 'w') as f:
                f.write(song_content)
            
            print(f"Saved {file_name}")

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
