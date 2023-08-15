from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from time import sleep

app = Flask(__name__)

BASE_URL = "https://www.iheartjane.com/brands/34404/camino/products/1184332/camino-10-3-sleep-blackberry-dream-10-pk-100-mg-thc-30-mg-cbn?page={}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

@app.route('/')
def scrape_reviews():
    page = 1
    all_reviews = []
    session = requests.Session()  # Use session for consistent headers and cookies.

    while True:
        try:
            response = session.get(BASE_URL.format(page), headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            reviews_list = soup.find('ul', {'class': 'ais-Hits-list'})
            
            reviews = [li.text.strip() for li in reviews_list.find_all('li', {'class': 'ais-Hits-item'})]
            all_reviews.extend(reviews)
            
            prev_page_button = soup.find('button', {'aria-label': 'previous-page', 'class': 'css-d85ps1'})
            if prev_page_button is None:
                break

            page += 1
            sleep(2)  # Pause for 2 seconds before the next request

        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break  # Stop scraping on error or adjust based on your needs.

    return '<br>'.join(all_reviews)

if __name__ == "__main__":
    app.run(debug=True)
