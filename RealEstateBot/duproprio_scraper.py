from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from time import sleep
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
CHROME_BINARY_PATH = os.getenv("CHROME_BINARY_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PRICE_TO_ASSESSMENT_RATIO = float(os.getenv("PRICE_TO_ASSESSMENT_RATIO", "2.0"))
REFRESH_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL_SECONDS", "900"))



LAST_VISITED_FILE = "lastVisited.txt"
RESULTS_FILE = "list.txt"

# URL to scrape
# URL includes user desired filters such as price range, property type, and region
SEARCH_URL = (
    "https://duproprio.com/en/search/list?search=true&regions%5B0%5D=13&regions%5B1%5D=15&regions%5B2%5D=6&"
    "max_price=1000000&type%5B0%5D=house&type%5B1%5D=cottage&type%5B2%5D=multiplex&type%5B3%5D=terr&type%5B4%5D=farm&"
    "is_for_sale=1&with_builders=1&parent=1&pageNumber=1&sort=-published_at"
)


class DuProprioScraper:
    def __init__(self):
        print("Starting scraper...")

        options = Options()
        # options.add_argument('--headless=new')  # Uncomment to enable headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.binary_location = CHROME_BINARY_PATH

        service = Service(CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def run(self):
        print("Opening search page...")
        self.driver.get(SEARCH_URL)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-results-listings-list__item-image-link")))

        page_number = 1
        while True:
            self.process_listings()
            page_number += 1
            print(f"Navigating to page {page_number}...")
            try:
                next_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/main/div[2]/div/div/div[3]/div/nav/div[2]/a")))
                next_btn.click()
            except Exception as e:
                print("No more pages or navigation error:", e)
                break

    def process_listings(self):
        listings = self.driver.find_elements(By.CLASS_NAME, "search-results-listings-list__item-image-link")

        for i in range(len(listings)):
            listings = self.driver.find_elements(By.CLASS_NAME, "search-results-listings-list__item-image-link")
            while True:
                try:
                    print(f"Clicking listing #{i}...")
                    self.driver.execute_script("arguments[0].click();", listings[i])
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))

                    if not self.has_been_visited():
                        print("New listing found.")
                        self.analyze_listing()
                        self.save_last_visited(self.driver.current_url)
                    else:
                        print("Listing already visited. Sleeping 15 minutes.")
                        sleep(REFRESH_INTERVAL_SECONDS) # restart web scrap every XX mins to capture the newest listings
                        self.run()
                    break
                except Exception as e:
                    print("Click or popup error:", e)
                    try:
                        close_btn = self.driver.find_element(By.XPATH,
                            "/html/body/main/div[2]/div/div/div[2]/div/div/div/div[1]")
                        close_btn.click()
                        print("Popup closed.")
                        sleep(2)
                    except:
                        print("Skipping listing.")
                        break
            self.driver.back()
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-results-listings-list__item-image-link")))
            sleep(2)

    def has_been_visited(self):
        url = self.driver.current_url
        try:
            with open(LAST_VISITED_FILE, "r") as f:
                return f.readline().strip() == url
        except FileNotFoundError:
            return False

    def save_last_visited(self, url):
        with open(LAST_VISITED_FILE, "w") as f:
            f.write(url + "\n")

    def append_result(self, url):
        with open(RESULTS_FILE, "a") as f:
            f.write(url + "\n")

    def analyze_listing(self):
        print("Analyzing listing...")
        try:
            text = self.driver.find_element(By.XPATH,
                "/html/body/main/div[1]/div/div[1]/section[1]/article/div[3]/div[1]").text
            if "Municipal Assessment" in text:
                ratio = self.extract_price_to_assessment_ratio(text)
                print(f"Price/Assessment ratio: {ratio:.2f}")
                if ratio < PRICE_TO_ASSESSMENT_RATIO:
                    self.append_result(self.driver.current_url)
                    self.send_email_notification(self.driver.current_url)
        except Exception as e:
            print("Error during analysis:", e)

    def extract_price_to_assessment_ratio(self, text):
        def extract_number(label, offset):
            index = text.find(label) + offset
            raw = text[index:index + 10].strip().strip("$")
            return int(''.join(filter(str.isdigit, raw)))

        try:
            assessment = extract_number("Municipal Assessment", 20)
            price = extract_number("Asking Price", 13)
            return price / assessment if assessment else float('inf')
        except Exception as e:
            print("Failed to extract values:", e)
            return float('inf')

    def send_email_notification(self, url):
        print("Sending notification...")
        try:
            msg = MIMEText(url, 'html')
            msg["Subject"] = "New Property Alert"
            msg["From"] = EMAIL_SENDER
            msg["To"] = EMAIL_RECEIVER

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            print("Notification sent.")
        except Exception as e:
            print("Email failed:", e)


if __name__ == "__main__":
    scraper = DuProprioScraper()
    scraper.run()
