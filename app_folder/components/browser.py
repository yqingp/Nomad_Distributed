import json
from json.decoder import JSONDecodeError
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

"""
Custom Exceptions
"""


class ElementNotFound(Exception):

    def __init__(self, message, url):

        super().__init__(message)

        self.url = url


class PageNotAvailable(Exception):

    def __init__(self, message, url):

        super().__init__(message)

        self.url = url


"""
Custom Selenium Waits
"""


class PageStatusReady(object):

    """
    A very simple Wait condition

    Executes JavaScript script that returns document.readyState

    :returns: True if 'complete', else False

    """

    def __init__(self):
        pass

    def __call__(self, driver):
        ready_state = driver.execute_script("return document.readyState")
        if ready_state == 'complete':
            time.sleep(2)
            return True
        else:
            return False


class ElementExistsWithAttribute(object):

    """
    A Wait condition that tests:
        - Element exists
        - Element has attribute
        - Attribute matches attribute_pattern

    :returns: True if all conditions met, False if not
    """

    def __init__(self, locator, attribute, attribute_pattern):
        self.locator = locator
        self.attribute = attribute
        self.attribute_pattern = re.compile(attribute_pattern)

    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Unpacking a tuple like (By.CSS_SELECTOR, ".class_name")
        if not element:
            return False
        element_attr = element.get_property(self.attribute)
        if not element_attr:
            return False
        if self.attribute_pattern.search(element_attr):
            return element
        else:
            return False


class PageConditions(object):

    def __init__(self, attr=None, attr_pattern=None, locator=None):
        if not attr:
            self.attr = 'href'
        if not attr_pattern:
            self.attr_pattern = r"https://www.linkedin.com/recruiter/profile/[0-9]{3,15},"
        else:
            self.attr_pattern = attr_pattern
        if not locator:
            self.locator = (By.CSS_SELECTOR, "a[data-control-name='view_profile_in_recruiter']")
        else:
            self.locator = locator

    @staticmethod
    def check_page_invalid(url, requested_url):
        if 'unavailable' in url.lower():
            raise PageNotAvailable("Page {} is unavailable or invalid".format(requested_url), requested_url)
        else:
            return False

    def wait_for_target(self, driver, wait):
        try:
            wait.until(ElementExistsWithAttribute(self.locator, 'href', self.attr_pattern))
        except TimeoutException:
            raise ElementNotFound("Element {} not found on page {}".format(self.locator, driver.current_url),
                                  driver.current_url)


class NomadDriver(object):

    def __init__(self, service_path, page_conditions=PageConditions(), start_page=None):
        self.service_path = service_path
        self.service = self.start_service()
        self.driver = self.start_driver(start_page)
        self.wait = WebDriverWait(self.driver, 20)
        self.page_conditions = page_conditions

    @property
    def driver_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        return chrome_options

    def start_service(self):
        service = webdriver.chrome.service.Service(self.service_path)
        service.start()
        return service

    def start_driver(self, start_page):
        driver = webdriver.Chrome(executable_path=self.service_path, chrome_options=self.driver_options)
        if start_page:
            driver.get(start_page)
        return driver

    def maximize_window(self):
        if self.driver:
            self.driver.maximize_window()

    def shutdown(self):
        if self.driver:
            self.driver.close()
            self.driver.quit()
        if self.service:
            self.service.stop()

    def go_to_page(self, url):
        try:
            self.driver.get(url)
            page_ready = self.wait.until(PageStatusReady())
            return page_ready
        except TimeoutException:
            raise ElementNotFound("Page Not Ready for URL {}".format(url), url)

    def get_page_link(self, url):
        try:
            self.page_conditions.wait_for_target(self.driver, self.wait)
        except ElementNotFound as e:
            print(e)
            return False, e.url
        try:
            page_link = self.driver.execute_script(
                "return document.querySelector(\"a[data-control-name='view_profile_in_recruiter']\").href")
        except WebDriverException as e:
            print(e)
            return False, url
        return True, page_link

    def do_task(self, url):
        try:
            self.go_to_page(url)
        except ElementNotFound as e:  # Page never shows pageStatus == 'complete'
            print(e)
            return False, e.url

        # Handle occurrences of LinkedIn redirecting to 'https://www.linkedin.com/in/unavailable'
        try:
            self.page_conditions.check_page_invalid(self.driver.current_url, url)
        except PageNotAvailable as e:
            print(e)
            return False, e.url

        success_flag_page_link, page_link = self.get_page_link(url)

        if not success_flag_page_link:
            return False, url

        success_flag_raw_response, raw_response = self.fetch_ajax(page_link)

        if not success_flag_raw_response:
            return False, url

        success_flag_json_response, json_response = self.to_json(raw_response)

        if not success_flag_json_response:
            return False, url

        return True, json_response


    @property
    def data_search_re(self):
        code_search = re.compile(
            r"<code id=\"templates/desktop\/profile\/profile_streaming-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-content\"><!--")
        return code_search

    def fetch_ajax(self, url):
        try:
            response = self.driver.execute_script(self.generate_script(url))
            return True, response
        except WebDriverException:
            return False, None

    def to_json(self, response):
        try:
            data_start = self.data_search_re.split(response)[1]
        except IndexError:
            return False, None
        data = data_start.split("--></code>")[0]
        try:
            return True, json.loads(data)
        except JSONDecodeError:
            return False, None

    @staticmethod
    def generate_script(page_link):
        script_begin = """var xhttp = new XMLHttpRequest();
                        xhttp.onreadystatechange = function() {
                            if (this.readyState == 4 && this.status == 200) {
                                return (xhttp.responseText);
                          }
                    };"""
        script_mid = "xhttp.open('GET', '{url}', false);".format(url=page_link)
        script_end = """xhttp.setRequestHeader('Accept', 'application/json, text/javascript, */*; q=0.01');
                    xhttp.setRequestHeader('Accept-Language', 'en-US,en;q=0.8');
                    xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                    xhttp.send();
                    return xhttp.responseText;"""

        full_script = script_begin + script_mid + script_end
        return full_script.replace("\n", " ")
