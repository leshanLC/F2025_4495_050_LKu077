from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import re
import sqlite3
import os
from datetime import datetime

class ImprovedIndeedScraper:
    def __init__(self, headless=True):
        self.options = Options()
        
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if headless:
            self.options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        
        self.jobs_data = []
        self.db_connection = None
        
    def setup_sqlite_database(self, db_path="pathfinder_db.sqlite"):
        try:
            self.db_connection = sqlite3.connect(db_path)
            self._create_jobs_table()
            print(f"SQLite database connected: {db_path}")
            return True
            
        except Exception as e:
            print(f"Error setting up SQLite database: {e}")
            return False

    def _create_jobs_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            salary TEXT,
            job_type TEXT,
            link TEXT,
            description TEXT,
            scraped_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, company, location)
        )
        """
        
        cursor = self.db_connection.cursor()
        cursor.execute(create_table_sql)
        self.db_connection.commit()
        cursor.close()
        print("Jobs table created/verified")

    def scrape_jobs(self, job_title="", location="Canada", max_pages=5):
        try:
            for page in range(max_pages):
                if page == 0:
                    url = f"https://ca.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location.replace(' ', '+').replace(',', '%2C')}"
                else:
                    url = f"https://ca.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location.replace(' ', '+').replace(',', '%2C')}&start={page * 10}"
                
                print(f"Scraping page {page + 1}...")
                print(f"URL: {url}")
                
                self.driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                # Wait for job cards
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.job_seen_beacon'))
                    )
                except:
                    print(f"No job cards found on page {page + 1}")
                    continue
                
                # Handle cookie consent if present
                self._handle_cookie_consent()
                
                jobs_count_before = len(self.jobs_data)
                self._extract_page_jobs_improved()
                jobs_added = len(self.jobs_data) - jobs_count_before
                
                print(f"Added jobs from page {page + 1}")
                
                # Save to database after each page
                if jobs_added > 0 and self.db_connection:
                    saved_count = self.save_to_database()
                    print(f"Saved jobs to database")
                
                if page < max_pages - 1:
                    time.sleep(random.uniform(2, 4))
                    
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        finally:
            self.driver.quit()
            if self.db_connection:
                self.db_connection.close()
                print("Database connection closed")
        
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

    def _safe_extract(self, parent, selector, attribute='text'):
        try:
            element = parent.find_element(By.CSS_SELECTOR, selector)
            if attribute == 'text':
                return element.text.strip()
            else:
                return element.get_attribute(attribute)
        except:
            return None

    def save_to_database(self):
        if not self.jobs_data or not self.db_connection:
            print("No data to save or database not connected")
            return 0
        
        try:
            cursor = self.db_connection.cursor()
            saved_count = 0
            
            insert_sql = """
            INSERT OR IGNORE INTO jobs (title, company, location, salary, job_type, link, description, scraped_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for job in self.jobs_data:
                try:
                    cursor.execute(insert_sql, (
                        job['title'],
                        job['company'],
                        job['location'],
                        job['salary'],
                        job['job_type'],
                        job['link'],
                        job['description'],
                        job['scraped_date']
                    ))
                    if cursor.rowcount > 0:
                        saved_count += 1
                except Exception as e:
                    print(f"Error inserting job: {e}")
                    continue
            
            self.db_connection.commit()
            cursor.close()
            return saved_count
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            return 0

    def query_jobs_from_database(self, limit=10):
        if not self.db_connection:
            print("Database not connected")
            return []
        
        try:
            # Reconnect if needed
            if not os.path.exists("pathfinder_db.sqlite"):
                return []
                
            conn = sqlite3.connect("pathfinder_db.sqlite")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT title, company, location, salary, job_type, link, description, scraped_date 
                FROM jobs 
                ORDER BY scraped_date DESC 
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            jobs = []
            for row in results:
                jobs.append({
                    'title': row[0],
                    'company': row[1],
                    'location': row[2],
                    'salary': row[3],
                    'job_type': row[4],
                    'link': row[5],
                    'description': row[6],
                    'scraped_date': row[7]
                })
            
            return jobs
            
        except Exception as e:
            print(f"Error querying database: {e}")
            return []

    def get_database_stats(self):
        if not os.path.exists("pathfinder_db.sqlite"):
            return {}
        
        try:
            conn = sqlite3.connect("pathfinder_db.sqlite")
            cursor = conn.cursor()
            
            # Total jobs count
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total_jobs = cursor.fetchone()[0]
            
            # Companies count
            cursor.execute("SELECT COUNT(DISTINCT company) FROM jobs")
            unique_companies = cursor.fetchone()[0]
            
            # Locations count
            cursor.execute("SELECT COUNT(DISTINCT location) FROM jobs")
            unique_locations = cursor.fetchone()[0]
            
            # Jobs with descriptions
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE description != 'Description snippet not available' AND description != 'Error extracting description'")
            jobs_with_descriptions = cursor.fetchone()[0]
            
            # Latest scrape date
            cursor.execute("SELECT MAX(scraped_date) FROM jobs")
            latest_scrape = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return {
                'total_jobs': total_jobs,
                'unique_companies': unique_companies,
                'unique_locations': unique_locations,
                'jobs_with_descriptions': jobs_with_descriptions,
                'latest_scrape': latest_scrape
            }
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}

    def save_to_csv(self, filename="indeed_jobs_backup.csv"):
        if not os.path.exists("pathfinder_db.sqlite"):
            print("Database file not found")
            return False
        
        try:
            conn = sqlite3.connect("pathfinder_db.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs")
            
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            
            df = pd.DataFrame(data, columns=columns)
            df.to_csv(filename, index=False, encoding='utf-8')
            
            cursor.close()
            conn.close()
            print(f"Database backed up to {filename}")
            return True
            
        except Exception as e:
            print(f"Error backing up to CSV: {e}")
            return False

    def export_to_excel(self, filename="indeed_jobs.xlsx"):
        if not os.path.exists("pathfinder_db.sqlite"):
            print("Database file not found")
            return False
        
        try:
            conn = sqlite3.connect("pathfinder_db.sqlite")
            df = pd.read_sql_query("SELECT * FROM jobs", conn)
            df.to_excel(filename, index=False)
            conn.close()
            print(f"Database exported to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False

def main():
    # Initialize scraper
    scraper = ImprovedIndeedScraper(headless=True)
    
    # Setup SQLite database
    if not scraper.setup_sqlite_database("pathfinder_db.sqlite"):
        print("Failed to setup database. Exiting.")
        return
    
    job_title = ""  
    location = "Canada"
    pages = 3  # Start with fewer pages for testing
    
    print(f"\nScraping all jobs in '{location}' ({pages} pages)...")
    
    # Scrape and save to database
    start_time = time.time()
    jobs = scraper.scrape_jobs(
        job_title=job_title,
        location=location,
        max_pages=pages
    )
    end_time = time.time()
    
    # Display results
    if jobs:
        print(f"\nSuccessfully processed jobs in {end_time - start_time:.1f} seconds")

        # Backup to CSV
        scraper.save_to_csv("indeed_jobs_backup.csv")
        
    else:
        print("No jobs were scraped")
    
    print(f"\nDatabase file: pathfinder_db.sqlite")
    print("CSV backup: indeed_jobs_backup.csv")

if __name__ == "__main__":
    main()