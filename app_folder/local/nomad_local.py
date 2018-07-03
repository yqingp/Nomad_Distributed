import os
import re
import sys
import time

import easygui

from components.browser import NomadDriver
from components.network import LocalHermesConnection

DEBUG = False
SLEEP_TIME = 10


def get_chromedriver_path():
    # Get CWD and pass chromedriver to PATH env variable
    return os.path.realpath('chromedriver.exe')


def do_exit(n_seconds=5, **kwargs):
    countdown = list(reversed([i for i in range(n_seconds)]))
    for i in countdown:
        print("Exiting in {}".format(i))
        time.sleep(1)
    if 'driver' in kwargs:
        kwargs['driver'].shutdown()
    print("Goodbye".center(80, "="))
    time.sleep(SLEEP_TIME)
    sys.exit()


url_search = re.compile(r"(https?:\/\/www\.?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*)",
                        flags=re.IGNORECASE)

items_input = easygui.codebox(msg="Paste (Ctrl + V) in the CSV list of sites to extract below")

if not items_input:
    items_list = None
else:
    items_list = url_search.findall(items_input)

if not items_list:
    print("No Valid URLs found")
    do_exit()


# Login to Hermes
username = input("Enter Hermes Username : ")
password = input("Enter Hermes Password : ")

print("Logging In".center(80, "="))
network = LocalHermesConnection(username=username, password=password, items=items_list, debug=DEBUG)
if not network.api_token:
    print("Error Logging In ...")
    do_exit()

# Explaining browser open procedures
for message in ["A new chrome window will open momentarily\n",
                "Please login to LinkedIn Recruiter\n",
                "Return to this screen when complete\n"]:

    print(message)
    time.sleep(1)

# Start Selenium

print(" CHROME LOG (Ignore This) ".center(80, "="))
print("")
driver = NomadDriver(service_path=get_chromedriver_path(), start_page="https://www.linkedin.com/recruiter")
print(" END CHROME LOG ".center(80, "="))
print("")

# Confirm logged in, pause thread
input("Have you logged into LinkedIn Recruiter? [y/n] ")

print("Fetching {} Links".format(len(items_list)))

for task in items_list:
    success, data = driver.do_task(task)
    if not success:
        print("{} Returned an error".format(task))
        time.sleep(SLEEP_TIME)
        continue
    network.checkin_item(data)
    time.sleep(SLEEP_TIME)
    print("{} Success".format(task))

print("ALL DONE!".center(80, "*"))
do_exit(5, driver=driver)
