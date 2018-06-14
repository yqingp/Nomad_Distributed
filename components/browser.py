import re
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


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


class NomadDriver(object):

    def __init__(self, service_path, start_page=None):
        self.service_path = service_path
        self.service = self.start_service()
        self.driver = self.start_driver(start_page)
        self.wait = WebDriverWait(self.driver, 60)

    def start_service(self):
        service = webdriver.chrome.service.Service(
            os.path.abspath(self.service_path))
        service.start()
        return service

    def start_driver(self, start_page):
        driver = webdriver.Chrome(os.path.abspath(self.service_path))
        if start_page:
            driver.get(start_page)
        return driver

    def go_to_page(self, url):
        self.driver.get(url)
        page_ready = self.wait.until(PageStatusReady())
        return page_ready

    def get_page_link(self):
        page_ready = self.wait.until(PageStatusReady())
        if not page_ready:
            print("Error getting")
            return None
        page_link = self.driver.execute_script(
            "return document.querySelector(\"a[data-control-name='view_profile_in_recruiter']\").href")
        return page_link

    def do_task(self, url):
        page = self.go_to_page(url)
        if not page:
            return False
        page_link = self.get_page_link()
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
