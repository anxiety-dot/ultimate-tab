# Downloads the Tab from ultimateguitar.com

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def scrape_pre_content(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors

    # Set up WebDriver
    service = Service()  # Use the default ChromeDriver from system path
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)  # Adjust sleep time if needed

    try:
        # Find the <pre> element with the specific class
        pre_element = driver.find_element(By.CSS_SELECTOR, 'pre.tK8GG.Ty_RP')
        pre_content = pre_element.get_attribute('outerHTML')
        return pre_content
    except Exception as e:
        print(f'Error: {e}')
        return None
    finally:
        driver.quit()

def save_content_to_file(content, filename='pre_content.html'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == '__main__':
    url = input('Enter the URL of the page to scrape: ')
    pre_content = scrape_pre_content(url)
    if pre_content:
        save_content_to_file(pre_content)
        print(f'Successfully scraped and saved content to pre_content.html')
    else:
        print('Failed to retrieve content.')
