import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

class IndeedScraper:
    def __init__(self, headless=True):
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--disable-gpu')
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

        self.jobs_data = []

    def scrape_jobs(self, job_title, location="Canada"):
        """Scrape ONLY PAGE 1 for one job title."""
        self.jobs_data = []  # reset list

        url = f"https://ca.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location}"
        print(f"\nScraping: {job_title}")
        print(f"URL: {url}")

        self.driver.get(url)
        time.sleep(random.uniform(3, 5))

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
            )
        except:
            print("No job cards found.")
            return []

        self._handle_cookie_consent()
        self._extract_page_jobs_improved()

        return self.jobs_data

    def _handle_cookie_consent(self):
        """Handle cookie consent popup if it appears"""
        try:
            cookie_selectors = [
                'button[aria-label="reject"]',
                'button[aria-label="Reject All"]',
                'button#onetrust-reject-all-handler',
                'button[data-testid="reject-button"]'
            ]
            
            for selector in cookie_selectors:
                try:
                    reject_button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    reject_button.click()
                    print("Cookie consent handled")
                    time.sleep(1)
                    break
                except:
                    continue
        except:
            pass

    def _safe_extract(self, parent, selector, attribute='text'):
        try:
            element = parent.find_element(By.CSS_SELECTOR, selector)
            if attribute == 'text':
                return element.text.strip()
            else:
                return element.get_attribute(attribute)
        except:
            return None

    def _extract_page_jobs_improved(self):
        try:
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.job_seen_beacon')
            print(f"Found {len(job_cards)} job cards")
            
            for i, card in enumerate(job_cards):
                # Add delay to avoid being blocked
                if i > 0 and i % 3 == 0:
                    time.sleep(random.uniform(1, 2))
                
                job_info = self._extract_job_info_improved(card)
                if job_info:
                    self.jobs_data.append(job_info)
                    
        except Exception as e:
            print(f"Error extracting jobs: {e}")

    def _extract_job_info_improved(self, card):
        try:
            # Extract basic info first
            title = self._safe_extract(card, 'h2.jobTitle a', 'text')
            if not title:
                title = self._safe_extract(card, 'h2 a', 'text')
            if title:
                title = re.sub(r'^New\s*', '', title).strip()
            
            company = self._safe_extract(card, '[data-testid="company-name"]', 'text')
            if not company:
                company = self._safe_extract(card, '.companyName', 'text')
            if not company:
                company = self._safe_extract(card, '[class*="companyName"]', 'text')
            
            location = self._safe_extract(card, '[data-testid="text-location"]', 'text')
            if not location:
                location = self._safe_extract(card, '.companyLocation', 'text')
            if not location:
                location = self._safe_extract(card, '[class*="companyLocation"]', 'text')
            
            # Now extract description using the basic info we have
            description = self._extract_job_description_improved(card, title, company, location)
            
            # Salary - Improved extraction
            salary = "Salary not specified"
            salary_selectors = [
                '[data-testid="attribute_snippet_testid"]',
                '.salary-snippet-container',
                '.metadata salary-snippet-container'
            ]
            
            for selector in salary_selectors:
                salary_text = self._safe_extract(card, selector, 'text')
                if salary_text and ('$' in salary_text or 'hour' in salary_text.lower() or 'year' in salary_text.lower()):
                    salary = salary_text
                    break
            
            # Link
            link = self._safe_extract(card, 'h2.jobTitle a', 'href')
            if not link:
                link = self._safe_extract(card, 'h2 a', 'href')
            if link and link.startswith('/'):
                link = 'https://ca.indeed.com' + link
            
            # Job Type - Improved extraction
            job_type = self._extract_job_type_improved(card)
            
            if title:
                return {
                    'title': title,
                    'company': company or "Company not found",
                    'location': location or "Location not specified",
                    'salary': salary,
                    'job_type': job_type,
                    'link': link or "Link not available",
                    'description': description or "Description not available",
                    'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            print(f"Error extracting job info: {e}")
        
        return None

    def _extract_job_description_improved(self, card, title, company, location):
        """Improved job description extraction with proper parameters"""
        try:
            # Try the job snippet/summary section first
            description_selectors = [
                'div.job-snippet',
                'div[class*="job-snippet"]',
                'div[class*="snippet"]',
                'div[class*="summary"]',
                'ul[style*="list-style-type:circle"]',
                '.css-e9ucx3',  # From the HTML structure
                '[data-testid="belowJobSnippet"]'
            ]
            
            for selector in description_selectors:
                description = self._safe_extract(card, selector, 'text')
                if description and len(description.strip()) > 20:
                    description = description.strip()
                    description = re.sub(r'\s+', ' ', description)
                    return description[:1000]  # Limit to 1000 characters
            
            # Try to extract from the entire card text with better filtering
            card_text = card.text
            if card_text:
                lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                
                # Look for description content after basic info
                basic_info_indicators = ['$', 'salary', 'full-time', 'part-time', 'contract', 
                                       'remote', 'temporary', 'permanent', 'urgently hiring',
                                       'apply', 'save', 'bookmark', 'easily apply']
                
                description_lines = []
                
                for line in lines:
                    line_lower = line.lower()
                    
                    # Skip if it's basic info we've already captured
                    if any(indicator in line_lower for indicator in basic_info_indicators):
                        continue
                    
                    # Skip if it's title, company, or location (usually shorter lines that match exactly)
                    if (title and title.lower() in line_lower) or \
                       (company and company.lower() in line_lower) or \
                       (location and location.lower() in line_lower):
                        continue
                    
                    # Skip very short lines (likely navigation or buttons)
                    if len(line) < 20:
                        continue
                        
                    # If we find a reasonably long line that's not basic info, consider it description
                    if len(line) > 30:
                        description_lines.append(line)
                
                if description_lines:
                    description = ' '.join(description_lines[:3])  # Take first 3 description lines
                    description = re.sub(r'\s+', ' ', description).strip()
                    if len(description) > 30:
                        return description[:800]
            
            return "Description snippet not available"
            
        except Exception as e:
            print(f"Error extracting description: {e}")
            return "Error extracting description"

    def _extract_job_type_improved(self, card):
        """Improved job type extraction"""
        try:
            card_text = card.text.lower()
            
            # Check for job type in metadata
            metadata_selectors = [
                '[data-testid="attribute_snippet_testid"]',
                '.metadata',
                '.css-5ooe72'
            ]
            
            for selector in metadata_selectors:
                try:
                    elements = card.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.lower()
                        if 'full-time' in text:
                            return 'Full-time'
                        elif 'part-time' in text:
                            return 'Part-time'
                        elif 'contract' in text:
                            return 'Contract'
                        elif 'temporary' in text:
                            return 'Temporary'
                        elif 'permanent' in text:
                            return 'Permanent'
                        elif 'remote' in text:
                            return 'Remote'
                except:
                    continue
            
            # Fallback to text analysis
            if 'full-time' in card_text:
                return 'Full-time'
            elif 'part-time' in card_text:
                return 'Part-time'
            elif 'contract' in card_text:
                return 'Contract'
            elif 'temporary' in card_text:
                return 'Temporary'
            elif 'remote' in card_text:
                return 'Remote'
            else:
                return 'Not specified'
                
        except:
            return 'Not specified'
