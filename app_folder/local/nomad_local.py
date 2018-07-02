import time
import easygui
import sys
import re
from components.browser import NomadDriver
from components.network import LocalHermesConnection


DEBUG = False
SLEEP_TIME = 10


def do_exit(n_seconds=5, **kwargs):
    countdown = list(reversed([i for i in range(n_seconds)]))
    for i in countdown:
        print("Exiting in {}".format(i))
    if 'driver' in kwargs:
        kwargs['driver'].shutdown()
    print("Goodbye".center(80, "="))
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

print("A new chrome window will open momentarily")
print("Please login to LinkedIn Recruiter in this window")
print("Return to this screen when complete")
time.sleep(2)

# Start Selenium
driver = NomadDriver()

# Confirm logged in
input("Enter any key to continue after logging in ")

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



