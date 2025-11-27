import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class CourseraScraper:
    def __init__(self, headless=True):
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--disable-extensions')

        self.options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        if headless:
            self.options.add_argument('--headless')

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )

        self.courses = []

    def scrape_courses(self, query):
        """Scrape Coursera search results - PAGE 1 ONLY"""
        self.courses = []

        url = f"https://www.coursera.org/search?query={query.replace(' ', '%20')}"
        print(f"\nScraping Coursera for: {query}")
        print("URL:", url)

        self.driver.get(url)
        time.sleep(random.uniform(3, 6))

        # Wait until product cards load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="product-card-cds"]'))
            )
        except:
            print("No course cards found.")
            return []

        cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-card-cds"]')
        print(f"Found {len(cards)} course cards")

        for card in cards:
            course = self._extract_course_info(card)
            if course:
                self.courses.append(course)

        return self.courses

    def _safe_extract(self, parent, selector, attr='text'):
        """Safe element extraction"""
        try:
            el = parent.find_element(By.CSS_SELECTOR, selector)
            if attr == "text":
                return el.text.strip()
            return el.get_attribute(attr)
        except:
            return None

    def _extract_course_info(self, card):
        try:
            # Title
            title = self._safe_extract(card, ".cds-CommonCard-title")
            if not title:
                return None

            # Organization / Partner (e.g., IBM, Google, Meta)
            organization = self._safe_extract(card, ".cds-CommonCard-subtitle")

            # Course URL
            link_el = card.find_element(By.CSS_SELECTOR, "a[href]")
            url = "https://www.coursera.org" + link_el.get_attribute("href")

            # Skills
            skills = None
            try:
                skill_block = card.find_element(By.CSS_SELECTOR, ".css-vac8rf")
                skills = skill_block.text.replace("Skills you'll gain:", "").strip()
            except:
                pass

            # Rating
            rating = None
            try:
                rating_el = card.find_element(By.CSS_SELECTOR, ".cds-RatingStat-meter span")
                rating = rating_el.text.strip()
            except:
                rating = None

            # Students enrolled (Coursera shows "123k already enrolled")
            students = None
            try:
                enroll_el = card.find_element(By.CSS_SELECTOR, ".css-1xrh3fl")
                students = enroll_el.text.replace("already enrolled", "").strip()
            except:
                students = None

            return {
                "course_title": title,
                "organization": organization,
                "skills": skills,
                "rating": float(rating) if rating else None,
                "course_students_enrolled": students,
                "url": url,
                "scraped_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            print("Error extracting course:", e)
            return None
