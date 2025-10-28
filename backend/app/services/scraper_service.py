"""
Web scraping service for KIIT data sources.
Scrapes notices, exam schedules, academic calendar, and holiday lists.
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Optional, Dict, Any
import time
import logging
from datetime import datetime
import PyPDF2
import io

from app.config import settings
from app.models.notice import Notice, NoticeType, NoticeMetadata, NoticeCreate
from app.utils.hash_utils import generate_content_hash
from app.utils.date_parser import parse_date, extract_dates_from_text, get_current_datetime

logger = logging.getLogger(__name__)


class ScraperService:
    """Service for scraping the KIIT data sources"""

    def __init__(self):
        self.timeout = settings.SCRAPE_TIMEOUT_SECONDS
        self.max_retries = settings.SCRAPE_MAX_RETRIES
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _get_selenium_driver(self) -> webdriver.Chrome:
        """Create and configure Selenium WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(self.timeout)
        return driver

    def _fetch_page(self, url: str, use_selenium: bool = False) -> Optional[str]:
        """
        Fetch page content with retry logic.

        Args:
            url: URL to fetch
            use_selenium: Use Selenium for JavaScript-rendered content

        Returns:
            HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                if use_selenium:
                    driver = self._get_selenium_driver()
                    try:
                        driver.get(url)
                        time.sleep(2)  # Wait for JavaScript to load
                        content = driver.page_source
                        driver.quit()
                        return content
                    except Exception as e:
                        driver.quit()
                        raise e
                else:
                    response = self.session.get(url, timeout=self.timeout)
                    response.raise_for_status()
                    return response.text

            except Exception as e:
                wait_time = 5 * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None

    def scrape_general_notices(self) -> List[NoticeCreate]:
        """
        Scrape general notices from https://kiit.ac.in/notices/

        Returns:
            List of NoticeCreate objects
        """
        url = "https://kiit.ac.in/notices/"
        logger.info(f"Scraping general notices from {url}")

        html = self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        notices = []

        try:
            # Find notice containers (adjust selectors based on actual page structure)
            notice_items = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and ('notice' in x.lower() or 'post' in x.lower()))

            if not notice_items:
                # Fallback: Try finding all links in main content area
                content_area = soup.find(['main', 'div'], class_=lambda x: x and 'content' in x.lower()) or soup
                notice_items = content_area.find_all('a', href=True)

            for item in notice_items[:50]:  # Limit to recent 50 notices
                try:
                    # Extract title
                    title_elem = item.find(['h2', 'h3', 'h4', 'a', 'span'])
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    # Extract content
                    content_elem = item.find(['p', 'div'], class_=lambda x: x and 'content' in x.lower())
                    content = content_elem.get_text(strip=True) if content_elem else title

                    # Extract link
                    link_elem = item.find('a', href=True)
                    notice_url = link_elem['href'] if link_elem else url
                    if not notice_url.startswith('http'):
                        notice_url = 'https://kiit.ac.in' + notice_url

                    # Extract date
                    date_elem = item.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower())
                    date_str = date_elem.get_text(strip=True) if date_elem else None
                    date_published = parse_date(date_str) if date_str else get_current_datetime()

                    # Extract attachments
                    attachments = []
                    pdf_links = item.find_all('a', href=lambda x: x and x.endswith('.pdf'))
                    for pdf_link in pdf_links:
                        pdf_url = pdf_link['href']
                        if not pdf_url.startswith('http'):
                            pdf_url = 'https://kiit.ac.in' + pdf_url
                        attachments.append(pdf_url)

                    notice = NoticeCreate(
                        title=title,
                        content=content,
                        date_published=date_published,
                        source_url=notice_url,
                        source_type=NoticeType.GENERAL,
                        attachments=attachments
                    )
                    notices.append(notice)

                except Exception as e:
                    logger.warning(f"Error parsing notice item: {e}")
                    continue

            logger.info(f"Scraped {len(notices)} general notices")
            return notices

        except Exception as e:
            logger.error(f"Error scraping general notices: {e}")
            return []

    def scrape_exam_notices(self) -> List[NoticeCreate]:
        """
        Scrape exam notices from http://coe.kiit.ac.in/notices.php

        Returns:
            List of NoticeCreate objects
        """
        url = "http://coe.kiit.ac.in/notices.php"
        logger.info(f"Scraping exam notices from {url}")

        html = self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        notices = []

        try:
            # Find table or list containing exam notices
            tables = soup.find_all('table')
            notice_lists = soup.find_all(['ul', 'ol'], class_=lambda x: x and 'notice' in x.lower())

            items_to_parse = []

            # Parse tables
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header row
                items_to_parse.extend(rows)

            # Parse lists
            for notice_list in notice_lists:
                list_items = notice_list.find_all('li')
                items_to_parse.extend(list_items)

            # If no structured data, find all links
            if not items_to_parse:
                items_to_parse = soup.find_all('a', href=True)

            for item in items_to_parse[:50]:
                try:
                    # For table rows
                    if item.name == 'tr':
                        cells = item.find_all(['td', 'th'])
                        if len(cells) < 2:
                            continue

                        # Typically: Date | Title | Link structure
                        title_text = ' '.join(cell.get_text(strip=True) for cell in cells)
                        link_elem = item.find('a', href=True)
                        date_cell = cells[0].get_text(strip=True)
                        date_published = parse_date(date_cell) or get_current_datetime()

                    # For list items or links
                    else:
                        title_text = item.get_text(strip=True)
                        link_elem = item if item.name == 'a' else item.find('a', href=True)
                        date_published = get_current_datetime()

                    if not title_text or len(title_text) < 10:
                        continue

                    # Extract link
                    notice_url = link_elem['href'] if link_elem else url
                    if not notice_url.startswith('http'):
                        notice_url = 'http://coe.kiit.ac.in/' + notice_url.lstrip('/')

                    # Extract attachments
                    attachments = []
                    if '.pdf' in notice_url.lower():
                        attachments.append(notice_url)

                    notice = NoticeCreate(
                        title=title_text[:200],  # Limit title length
                        content=title_text,
                        date_published=date_published,
                        source_url=notice_url,
                        source_type=NoticeType.EXAM,
                        attachments=attachments
                    )
                    notices.append(notice)

                except Exception as e:
                    logger.warning(f"Error parsing exam notice item: {e}")
                    continue

            logger.info(f"Scraped {len(notices)} exam notices")
            return notices

        except Exception as e:
            logger.error(f"Error scraping exam notices: {e}")
            return []

    def scrape_holiday_list(self) -> List[NoticeCreate]:
        """
        Scrape holiday calendar from https://kiit.ac.in/notices/holidays/

        Returns:
            List of NoticeCreate objects
        """
        url = "https://kiit.ac.in/notices/holidays/"
        logger.info(f"Scraping holiday list from {url}")

        html = self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        notices = []

        try:
            # Find holiday tables
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header

                for row in rows:
                    try:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 2:
                            continue

                        # Typical structure: Date | Holiday Name | Category
                        date_str = cells[0].get_text(strip=True)
                        holiday_name = cells[1].get_text(strip=True) if len(cells) > 1 else "Holiday"
                        category = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                        if not holiday_name:
                            continue

                        date_published = parse_date(date_str) or get_current_datetime()

                        # Create content with category info
                        content = f"{holiday_name}"
                        if category:
                            content += f" - {category}"

                        notice = NoticeCreate(
                            title=f"Holiday: {holiday_name}",
                            content=content,
                            date_published=date_published,
                            source_url=url,
                            source_type=NoticeType.HOLIDAY,
                            attachments=[]
                        )
                        notices.append(notice)

                    except Exception as e:
                        logger.warning(f"Error parsing holiday row: {e}")
                        continue

            # If no tables found, try alternative structure
            if not notices:
                holiday_items = soup.find_all(['li', 'div'], class_=lambda x: x and 'holiday' in x.lower())
                for item in holiday_items:
                    try:
                        text = item.get_text(strip=True)
                        if len(text) < 5:
                            continue

                        notice = NoticeCreate(
                            title=f"Holiday: {text[:100]}",
                            content=text,
                            date_published=get_current_datetime(),
                            source_url=url,
                            source_type=NoticeType.HOLIDAY,
                            attachments=[]
                        )
                        notices.append(notice)
                    except Exception as e:
                        logger.warning(f"Error parsing holiday item: {e}")
                        continue

            logger.info(f"Scraped {len(notices)} holiday entries")
            return notices

        except Exception as e:
            logger.error(f"Error scraping holiday list: {e}")
            return []

    def scrape_academic_calendar(self) -> List[NoticeCreate]:
        """
        Scrape academic calendar from https://kiit.ac.in/academics/

        Returns:
            List of NoticeCreate objects
        """
        url = "https://kiit.ac.in/academics/"
        logger.info(f"Scraping academic calendar from {url}")

        html = self._fetch_page(url, use_selenium=True)  # May need JS rendering
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        notices = []

        try:
            # Find calendar tables or event lists
            tables = soup.find_all('table')
            calendar_sections = soup.find_all(['div', 'section'], class_=lambda x: x and ('calendar' in x.lower() or 'academic' in x.lower()))

            # Parse tables
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header

                for row in rows:
                    try:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 2:
                            continue

                        # Structure: Date/Period | Event | Details
                        date_or_period = cells[0].get_text(strip=True)
                        event_name = cells[1].get_text(strip=True)
                        details = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                        if not event_name:
                            continue

                        # Try to parse date
                        date_published = parse_date(date_or_period) or get_current_datetime()

                        content = event_name
                        if details:
                            content += f" - {details}"

                        notice = NoticeCreate(
                            title=f"Academic: {event_name}",
                            content=content,
                            date_published=date_published,
                            source_url=url,
                            source_type=NoticeType.ACADEMIC,
                            attachments=[]
                        )
                        notices.append(notice)

                    except Exception as e:
                        logger.warning(f"Error parsing academic calendar row: {e}")
                        continue

            # Parse calendar sections
            for section in calendar_sections:
                event_items = section.find_all(['li', 'div', 'p'])
                for item in event_items[:20]:
                    try:
                        text = item.get_text(strip=True)
                        if len(text) < 10:
                            continue

                        # Extract dates from content
                        dates = extract_dates_from_text(text)
                        date_published = dates[0] if dates else get_current_datetime()

                        notice = NoticeCreate(
                            title=f"Academic Event: {text[:100]}",
                            content=text,
                            date_published=date_published,
                            source_url=url,
                            source_type=NoticeType.ACADEMIC,
                            attachments=[]
                        )
                        notices.append(notice)

                    except Exception as e:
                        logger.warning(f"Error parsing academic event: {e}")
                        continue

            logger.info(f"Scraped {len(notices)} academic calendar entries")
            return notices

        except Exception as e:
            logger.error(f"Error scraping academic calendar: {e}")
            return []

    def extract_pdf_content(self, pdf_url: str) -> Optional[str]:
        """
        Download and extract text from PDF.

        Args:
            pdf_url: URL of PDF file

        Returns:
            Extracted text content or None
        """
        try:
            logger.info(f"Extracting PDF content from {pdf_url}")
            response = self.session.get(pdf_url, timeout=self.timeout)
            response.raise_for_status()

            # Read PDF content
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extract text from all pages
            text_content = []
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())

            full_text = '\n\n'.join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text

        except Exception as e:
            logger.error(f"Failed to extract PDF content from {pdf_url}: {e}")
            return None

    def scrape_all_sources(self) -> Dict[str, List[NoticeCreate]]:
        """
        Scrape all KIIT data sources.

        Returns:
            Dictionary mapping source type to list of notices
        """
        logger.info("Starting scrape of all KIIT sources")

        results = {
            'general': self.scrape_general_notices(),
            'exam': self.scrape_exam_notices(),
            'holiday': self.scrape_holiday_list(),
            'academic': self.scrape_academic_calendar()
        }

        total = sum(len(notices) for notices in results.values())
        logger.info(f"Scraping completed. Total notices: {total}")

        return results


# Singleton instance
_scraper_service: Optional[ScraperService] = None


def get_scraper_service() -> ScraperService:
    """Get scraper service singleton"""
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService()
    return _scraper_service
