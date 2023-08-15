from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
from time import sleep

app = Flask(__name__)

BASE_URL = "https://www.iheartjane.com/brands/34404/camino/products/1184332/camino-10-3-sleep-blackberry-dream-10-pk-100-mg-thc-30-mg-cbn?page={}"

@app.route('/')
def scrape_reviews():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

    page = 1
    all_reviews = []
    
    try:
        while True:
            driver.get(BASE_URL.format(page))

            # Handling the age verification popup
            try:
                confirm_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[name='Confirm'].css-a9cjuw"))
                )
                confirm_button.click()
            except:
                pass  # If not found, just continue

            # Handling the address input popup
            try:
                close_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-swyrt1 div[role='button'].css-kw7h5n"))
                )
                close_button.click()
            except:
                pass  # If not found, just continue

            sleep(2)  # Pause for 2 seconds for the page to load properly

            # Parsing the page content with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            reviews_list = soup.find('ul', {'class': 'ais-Hits-list'})
            
            if reviews_list:
                reviews = [li.text.strip() for li in reviews_list.find_all('li', {'class': 'ais-Hits-item'})]
                all_reviews.extend(reviews)

                prev_page_button = soup.find('button', {'aria-label': 'previous-page', 'class': 'css-d85ps1'})
                if prev_page_button is None:
                    break

                page += 1
                sleep(2)  # Pause for 2 seconds before the next request
            else:
                break
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()

    return '<br>'.join(all_reviews)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
