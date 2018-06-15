import re
import json
import os
import re
import time
from app_config import Config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class ElementNotFound(Exception):

    def __init__(self, message, url):

        super().__init__(message)

        self.url = url


class PageStatusReady(object):

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

    def __init__(self, locator, attribute, attribute_pattern):
        self.locator = locator
        self.attribute = attribute
        self.attribute_pattern = re.compile(attribute_pattern)

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if not element:
            return False
        element_attr = element.get_property(self.attribute)
        if not element_attr:
            return False
        if self.attribute_pattern.search(element_attr):
            return element
        else:
            return False


class NomadDriver(object):

    def __init__(self, start_page=None, attr_pattern=None, locator=None):
        self.service = self.start_service()
        self.driver = self.start_driver(start_page)
        self.wait = WebDriverWait(self.driver, 60)
        if not attr_pattern:
            self.attr_pattern = r"https://www.linkedin.com/recruiter/profile/[0-9]{5,15},"
        else:
            self.attr_pattern = attr_pattern
        if not locator:
            self.locator = (By.CSS_SELECTOR, "a[data-control-name='view_profile_in_recruiter']")
        else:
            self.locator = locator

    def get_chromedriver_path(self):
        CHROME_PATH = Config.CHROME_PATH
        return CHROME_PATH

    def start_service(self):
        service_path = self.get_chromedriver_path()
        service = webdriver.chrome.service.Service(
            os.path.abspath(service_path))
        service.start()
        return service

    def start_driver(self, start_page):
        service_path = self.get_chromedriver_path()
        driver = webdriver.Chrome(service_path)
        if start_page:
            driver.get(start_page)
        return driver

    def go_to_page(self, url):
        try:
            self.driver.get(url)
            page_ready = self.wait.until(PageStatusReady())
            return page_ready
        except:
            raise ElementNotFound("Page Not Ready for URL {}".format(url), url)

    def get_page_link(self, url):
        try:
            page_link_element = self.wait.until(
                ElementExistsWithAttribute(
                    locator=self.locator, attribute='href', attribute_pattern=self.attr_pattern
                ))

            if not page_link_element:
                raise ElementNotFound("Target Element Does Not Exist", url)

            page_link = self.driver.execute_script(
                "return document.querySelector(\"a[data-control-name='view_profile_in_recruiter']\").href")
            return page_link
        except:
            raise ElementNotFound("Target Element Does Not Exist", url)

    def do_task(self, url):
        page = self.go_to_page(url)
        if not page:
            return False
        page_link = self.get_page_link(url)
        if not page_link:
            return False
        raw_response = self.fetch_ajax(page_link)
        json_response = self.to_json(raw_response)
        return json_response


    @property
    def data_search_re(self):
        code_search = re.compile(
            r"<code id=\"templates/desktop\/profile\/profile_streaming-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-content\"><!--")
        return code_search

    def fetch_ajax(self, url):
        response = self.driver.execute_script(self.generate_script(url))
        return response

    def to_json(self, response):
        data_start = self.data_search_re.split(response)[1]
        data = data_start.split("--></code>")[0]
        return json.loads(data)

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
