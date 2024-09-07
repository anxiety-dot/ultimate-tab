from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
import time
import os

# Ensure the output directory exists
OUTPUT_DIR = 'scraped_content'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

def close_popups(driver):
    try:
        # Handle JavaScript alerts
        alert = Alert(driver)
        alert.accept()
    except:
        pass

def get_filename_from_xpath(driver):
    try:
        # Get text from the specified XPath
        element = driver.find_element(By.XPATH, '/html/body/div/div[3]/main/div[2]/article[1]/section[1]/header/div')
        filename = element.text.strip().replace('/', '_').replace('\\', '_')  # Sanitize filename
        return filename
    except Exception as e:
        print(f"Error getting filename: {e}")
        return None

def scrape_page(url):
    driver.get(url)
    time.sleep(2)  # Give the page some time to load

    close_popups(driver)

    filename = get_filename_from_xpath(driver)
    if not filename:
        return None, None

    try:
        # Scrape content from <pre class="tK8GG Ty_RP">
        content = driver.find_element(By.CSS_SELECTOR, 'pre.tK8GG.Ty_RP').text
        return filename, content
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

def main():
    with open('filtered_links.txt', 'r') as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()
        if url:
            print(f"Scraping {url}")
            filename, content = scrape_page(url)
            if filename and content:
                file_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
                with open(file_path, 'w') as file:
                    file.write(f"URL: {url}\n")
                    file.write(content + "\n\n")
            time.sleep(1)  # Be polite and don't hammer the server

    driver.quit()

if __name__ == "__main__":
    main()
