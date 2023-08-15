from flask import Flask, render_template, send_from_directory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Scrape reviews
    reviews_list = scrape_reviews()
    
    # Render a template to display results
    return render_template('index.html', reviews=reviews_list)

@app.route('/download')
def download():
    # Scrape reviews
    reviews_list = scrape_reviews()

    # Convert reviews_list to CSV
    csv_output = "Reviewer Name, Date, Review Content\n"
    for review in reviews_list:
        csv_output += f"{review['Reviewer Name']}, {review['Date']}, {review['Review Content']}\n"

    # Save CSV to a file
    with open('reviews.csv', 'w') as file:
        file.write(csv_output)
    
    # Serve the file to be downloaded
    return send_from_directory('.', 'reviews.csv', as_attachment=True)

def scrape_reviews():
    url = "https://www.iheartjane.com/products/221079/camino-5-1-sleep-midnight-blueberry-20pk-100mg-thc-20mg-cbn"

    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    browser.get(url)

    # Close age verification
    confirm_button = browser.find_element_by_xpath("//button[contains(@name, 'Confirm')]")
    confirm_button.click()

    # Close address popup
    close_address_popup = browser.find_element_by_xpath("//svg[contains(@aria-label, 'dismiss-modal')]")
    close_address_popup.click()

    # Extract the reviews
    reviews_list = []
    review_items = browser.find_elements_by_xpath("//li[contains(@class, 'ais-Hits-item')]")
    for item in review_items:
        reviewer_name = item.find_element_by_xpath(".//div[contains(@class, 'css-zg1vud')]/span").text
        date = item.find_element_by_xpath(".//span[contains(@class, 'css-1ejtsw0')]").text
        review_content = item.find_element_by_xpath(".//p[contains(@class, 'css-sf485e')]").text

        reviews_list.append({
            'Reviewer Name': reviewer_name,
            'Date': date,
            'Review Content': review_content
        })

    browser.close()

    return reviews_list

if __name__ == '__main__':
    app.run()
