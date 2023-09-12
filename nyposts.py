from datetime import datetime, timedelta
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
import os
import re
from typing import Tuple
from selenium.common.exceptions import NoSuchElementException
from SeleniumLibrary.errors import ElementNotFound, NoOpenBrowser
from excel import Excel
from directories import DIRS
from logger import logger
from news_model import NewsData
from workitems import workitems


class NyPosts:

    def __init__(self) -> None:
        """Initializes the object.
            Args:
                workitem: A dictionary containing the work item data.
            Returns:
                None.
            """
        self.workitem = workitems()
        self.browser = Selenium()
        self.phrase: str = self.workitem["phrase"]
        self.section: str = self.workitem["section"]
        self.months = self.workitem["months"]
        self.excel = Excel()
        self.http = HTTP()

    def open_website(self) -> None:
        """Opens the web browser and clicks on the Continue button if a pop-up window shows up.
            Parameters:
                None
            Returns:
                None.
        """
        self.browser.open_chrome_browser('https://nypost.com/')
        self.browser.maximize_browser_window()
        continue_bt = self.browser.is_element_enabled(
            '//button[text()="Allow All"]')

        if continue_bt:
            self.browser.click_element('//button[text()="Allow All"]')

        self.browser.wait_until_element_is_visible(
            "//button[@class='site-header__search-toggle']", timeout=20)

    def phrase_search(self) -> Tuple[str]:
        """Searches the website for the phrase and returns a msg indicating whether the news for the phrase is available or not.
            Parameters:
                phrase (str): The phrase to search for.
            Returns:
                str: A msg indicating whether the news for the phrase is available or not.
        """
        msg = ''

        self.browser.wait_until_element_is_visible(
            "//button[@class='site-header__search-toggle']", timeout=3)
        self.browser.click_element(
            "//button[@class='site-header__search-toggle']")
        self.browser.input_text(
            "//input[@id='search-input-header']", self.phrase)
        self.browser.click_element(
            "//span[contains(@class, 'search__submit-text') and text()='Search']")
        logger.info("Search phrase done.")

        try:
            self.browser.wait_until_element_is_visible(
                "//div[@class='search-results__stories']", 20)
            available_news = True
        except AssertionError:
            msg = f"No news found for the phrase {self.phrase}"

        if self.browser.is_element_visible("//h2[contains(text(), 'No Articles Found')]"):
            msg = f"No news found for the phrase {self.phrase}"

        return available_news, msg

    def set_dates(self) -> None:
        """Sets the date ranges for the search.
        Returns:
            None.
        """
        if self.months >= 0:
            date_ranges = self.get_date_ranges(self.months)
            all_dates = self.get_all_dates_in_ranges(date_ranges)

            formatted_dates = [self.format_date(date) for date in all_dates]
            return formatted_dates

        else:
            logger.info("Invalid input. Please enter a non-negative integer.")

    def get_date_ranges(self, months_back):
        """Gets date ranges for the specified number of months back.
        Parameters:
            months_back (int): Number of months back.
        Returns:
            List of tuples: Date ranges.
        """
        current_month = datetime.now().month
        current_year = datetime.now().year

        date_ranges = []

        for i in range(months_back + 1):
            if i == 0:
                target_month = current_month
            else:
                target_month = current_month - (i - 1)

            target_year = current_year

            while target_month <= 0:
                target_month += 12
                target_year -= 1

            first_day = datetime(target_year, target_month, 1)

            # Calculate the last day of the month
            if target_month == 12:
                last_day = datetime(target_year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(
                    target_year, target_month + 1, 1) - timedelta(days=1)

            date_ranges.append((first_day, last_day))

        return date_ranges

    def get_all_dates_in_ranges(self, date_ranges):
        """Gets all dates within the specified date ranges.
        Parameters:
            date_ranges (List of tuples): Date ranges.
        Returns:
            List of datetime objects: All dates in the ranges.
        """
        all_dates = []

        for start_date, end_date in date_ranges:
            current_date = start_date
            while current_date <= end_date:
                all_dates.append(current_date)
                current_date += timedelta(days=1)

        return all_dates

    def format_date(self, date):
        """Formats a date as 'Month Day, Year'.
        Parameters:
            date (datetime): The date to format.
        Returns:
            str: The formatted date.
        """
        return date.strftime('%B %d, %Y')

    def sort_by(self):
        """Sorts the news by the newest first.
        Returns:
            None.
        """
        logger.info("sorting...")
        self.browser.scroll_element_into_view(
            "//ul/li/a[normalize-space()='Newest']")
        self.browser.wait_until_element_is_enabled(
            "//ul/li/a[normalize-space()='Newest']", timeout=10)
        self.browser.click_element_when_visible(
            "//ul/li/a[normalize-space()='Newest']")

    def select_sections(self):
        """Selects the specified sections.
        Returns:
            None.
        """
        logger.info("selecting sections..")
        self.browser.wait_until_element_is_enabled(
            "//div/nav/h3[normalize-space()='Sections']")
        self.browser.scroll_element_into_view(
            "//div/nav/h3[normalize-space()='Sections']")
        self.browser.wait_until_element_is_enabled(
            "//ul/li/a[normalize-space()='All']", timeout=10)

        if self.section == '' or self.section is None:
            self.browser.click_element_when_visible(
                "//ul/li/a[normalize-space()='All']")

        elif type(self.section) == list:
            for sec in self.section:
                self.click_section(sec)

        elif type(self.section) == str:
            if ',' in self.section:
                # Split the string by commas
                sections = self.section.split(",")
                for sec in sections:
                    self.click_section(sec.strip())
            else:
                self.click_section(self.section)

        else:
            logger.info(f"Section {self.section} is not available.")
            raise AssertionError

        logger.info("done selecting sections..")

    def click_section(self, sec):
        ele = f"//ul[@class='interior-menu__nav']/li/a[normalize-space()='{sec}']"
        if self.browser.is_element_visible(ele) or self.browser.is_element_enabled(ele):
            self.browser.scroll_element_into_view(
                "//div/nav/h3[normalize-space()='Sections']")
            self.browser.wait_until_element_is_enabled(ele)
            self.browser.click_element_when_visible(ele)
        else:
            logger.info(f"Section {sec} is not available.")

    def number_of_pages(self):
        """ Gets Number of pages.
        Returns:
            int 
        """
        self.browser.wait_until_element_is_visible(
            "//h2[@class='search-results__heading']/em")
        page_str = self.browser.get_text(
            "//h2[@class='search-results__heading']/em")
        if ',' in page_str:
            page_str = page_str.replace(",", "")
        page_int = int(round(int(page_str)))
        if page_int > 1:
            page_int = page_int+1
        return page_int

    def get_required_data(self):
        """Gets the required news data.
        Returns:
            None.
        """
        if self.browser.is_element_visible("//h2[contains(text(), 'No Articles Found')]"):
            logger.info("No news found.")

        limit = self.number_of_pages()
        for page in range(1, limit):

            ele = f"//a[normalize-space()='See More Stories']"
            logger.info("getting required data...")
            self.browser.wait_until_element_is_enabled(ele)

            try:
                data_fetched = self.send_to_excel(page)
                if data_fetched == False:
                    break
                else:
                    logger.info(f"page {page} done..")
                    self.browser.scroll_element_into_view(ele)
                    self.browser.wait_until_element_is_enabled(
                        ele, timeout=10)
                    self.browser.click_element_when_visible(ele)
                    logger.info("Scrapped all data scuessfully ")

            except NoSuchElementException:
                logger.info(f"No News Found on {self.phrase}")

    def news_stories(self, index):
        """Fetching news stories.
        Returns:
            Tuple of lists: News data lists (titles, dates, descriptions, image filenames, money presence, phrase counts).
        """
        logger.info("Fetching news")
        title_list = []
        date_list = []
        description_list = []
        image_filename_list = []
        money_present_list = []
        phrase_list = []

        path = f"//div[@class='search-results__story']"
        i = len(self.browser.find_elements(path))

        for var in range(1, i+1):
            self.browser.scroll_element_into_view(
                f"//div[@class='search-results__story'][{var}]")

            date = self.browser.get_text(
                f"//div[@class='search-results__story'][{var}]//div/div[2]/span")

            date_string = re.findall(r"[A-Za-z]+\s\d{1,2},\s\d{4}", date)
            date_str = date_string[0]
            time_stamped_date = datetime.strptime(date_str, '%B %d, %Y')
            final_date = datetime.strftime(time_stamped_date, '%B %d, %Y')

            if final_date in self.set_dates():

                title = self.browser.get_text(
                    f"//div[@class='search-results__story'][{var}]//div/div[2]/h3/a")
                description = self.browser.get_text(
                    f"//div[@class='search-results__story'][{var}]//div/div[2]/p")
                is_image = self.browser.is_element_enabled(
                    f"//div[@class='search-results__story'][{var}]//div/div/a/img")
                if is_image:
                    image_src = self.browser.get_element_attribute(
                        f"//div[@class='search-results__story'][{var}]//div/div/a/img", 'src')

                    image_filename = f'page({index})_image-news({var}).png'
                    image_path = os.path.join(DIRS.IMAGE_DIR, image_filename)

                    self.download_picture(image_src, image_path)
                else:
                    image_filename = ''

                money_present = self.money_status(
                    title) or self.money_status(description)
                title_count = self.search_string_count(title, self.phrase)
                description_count = self.search_string_count(
                    description, self.phrase)

                title_list.append(title)
                date_list.append(final_date)
                description_list.append(description)
                image_filename_list.append(image_filename)
                money_present_list.append(money_present)
                phrase_list.append(
                    f'Title: {title_count}; Description: {description_count}')
            else:
                logger.info(
                    "Found a date from the last month. Stopping scraping.")
                # Stop scraping if the date is out of range
                break

        return title_list, date_list, description_list, image_filename_list, money_present_list, phrase_list

    def download_picture(self, image_src: str, image_path: str) -> None:
        """Downloads the picture from the URL and saves it to the specified path.
            Args:
                image_src (str): The URL of the image.
                image_path (str): The path to the file where the image should be saved.
            Returns:
                None.
        """
        self.http.download(url=image_src, target_file=image_path)

    def money_status(self, input_text: str) -> bool:
        """Checks if any money string is present in the given text.
            Parameters:
                input_text (str): The input string.
            Returns:
                bool: True if any money string is present in the given text, False otherwise.
        """
        pattern_of_money = r'\$\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:dollars|USD))?\b|\b\d+\s*(?:dollars|USD)\b'
        match = re.findall(pattern_of_money, input_text)
        if match:
            return True
        else:
            return False

    def search_string_count(self, input_string: str, search_string: str) -> int:
        """Returns the count of the search string in the input string.
            Parameters:
                input_string (str): The input string.
                search_string (str): The search string.
            Returns:
                int: The count of the search string in the input string.
        """
        for char in ".,;?!‘’":
            input_string = input_string.lower().replace(char, "")
        words = input_string.split()
        result = []

        for i in range(0, len(words), len(search_string.split())):
            result.append(' '.join(words[i:i+len(search_string.split())]))
        return result.count(search_string.lower())

    def send_to_excel(self, index) -> None:
        """Fetches all the news applying all the filters and exports them into an Excel sheet.
            Returns:
                None.
        """

        news_data = NewsData(self.news_stories(index))

        if news_data.date_list:
            check = news_data.date_list[-1]
            if check in self.set_dates():
                flag = True
            else:
                flag = False
            worksheet_data = {
                "Title": news_data.title_list,
                "Description":  news_data.description_list,
                "Date": news_data.date_list,
                "Image FileName": news_data.image_file_list,
                "Count of Search Phrase": news_data.count_phrase_list,
                "Money Present": news_data.money_present_list
            }
            self.excel.create_excel(worksheet_data, DIRS.File_Path, index)
        else:
            flag = False

        return flag

    def close(self):
        self.browser.close_browser()
