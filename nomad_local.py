from components import LocalHermesConnection, NomadDriver
import time
import easygui

DEBUG = False
SLEEP_TIME = 10

items_list = easygui.codebox(msg="Paste in items to get").splitlines()

# Login to Hermes
username = input("Enter Hermes Username ")
password = input("Enter Hermes Password ")

network = LocalHermesConnection(username=username, password=password, items=items_list, debug=DEBUG)

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



