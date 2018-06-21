import time


class UserInterface(object):

    def __init__(self, name, print_delay=2):
        self.name = name
        self.print_delay = print_delay
        self.username = None
        self.password = None
        self.n_tasks = None
        self.queue_id = None
        self.queue_name = None

    def console_print(self, messages):
        for m in messages:
            if isinstance(m, str):
                print(m)
                time.sleep(self.print_delay)
                print("")
            else:
                m()

    """
    
    Welcome messages
    
    """

    @property
    def _welcome_(self):

        messages = ['Welcome to {}!'.format(self.name),
                    'This program will visit a list of profiles which will be saved to Hermes']
        return messages

    def welcome_(self):
        self.console_print(self._welcome_)

    @property
    def _welcome_login_(self):

        def prompt_username():
            username_prompt = input("What is your Hermes username?")
            self.username = username_prompt

        def prompt_password():
            password_prompt = input("What is your Hermes password?")
            self.password = password_prompt

        messages = ["Let's get started...", prompt_username, prompt_password]
        return messages

    def welcome_login_(self):
        self.console_print(self._welcome_login_)
        return {'username': self.username, 'password': self.password}


    """
    
    Logging In
    
    """

    @property
    def _retry_login(self):

        messages = ["",
                    "Invalid login",
                    "Please try again"]
        return messages

    def retry_login(self):
        self.console_print(self._retry_login)

    @property
    def login_web_(self):

        messages = ["",
                    "A new Chrome browser will open momentarily",
                    "Please log in to LinkedIn Recruiter",
                    "Return to this console once you have logged in",
                    ""
                    ]

        return messages

    def explain_browser_login_(self):
        self.console_print(self.login_web_)

    @property
    def await_login_confirmed_(self):

        def wait_for_login():
            confirm_logged_in = input("Are you logged in to LinkedIn Recruiter? Enter (y/n)")
            if confirm_logged_in.lower() == "n":
                return False
            else:
                return True

        messages = [wait_for_login]
        return messages

    def await_login_confirmed(self):
        self.console_print(self.await_login_confirmed_)

    @property
    def _prompt_task_count_(self):

        def task_count():
            n_tasks = input("How many tasks would you like to complete?")
            self.n_tasks = int(n_tasks)

        messages = ["",
                    task_count]
        return messages

    def prompt_task_count_(self, selected_queue):
        print("You selected {}".format(selected_queue['friendly_id']))
        self.console_print(self._prompt_task_count_)
        return self.n_tasks

    def show_items_received(self, n_items, tasks):

        messages = ["",
                    "Requested {} new tasks".format(n_items),
                    "Received {} tasks from Hermes".format(len(tasks)),
                    "This number may vary depending on:",
                    "1: Your daily profiles views remaining",
                    "2: Items you have checked out but not completed",
                    "3: Remaining items in queue"]

        self.console_print(messages)

    def prompt_select_queue_(self, available_queues):

        print("Here are your available queues:")
        print("")
        time.sleep(self.print_delay)
        break_line = "".join(["=" for _ in range(81)])
        for q in available_queues:
            print(break_line)
            print("Queue ID : {}, Queue Name : {}".format(q['queue_id'], q['friendly_id']).center(80))
            print("Enter {} To Select".format(q['queue_id']).center(80))
            print("Items in Queue : {}".format(q['n_items']))
            print("Items Completed in Queue : {}".format(q['n_completed']))
            print("Items You Have Currently Checked Out : {}".format(q['user_checkouts']))
            print("Items You Have Completed : {}".format(q['user_completes']))
            print(break_line)
            print("")
            time.sleep(self.print_delay)

        queue_prompt = int(input("Which queue do you want to work on?"))

        selected_queue = list(filter(lambda x: x['queue_id'] == int(queue_prompt), available_queues))[0]
        self.queue_id = selected_queue['queue_id']
        self.queue_name = selected_queue['friendly_id']
        return selected_queue

    @staticmethod
    def finished_one_task(task):
        print("Finished {}".format(task))

    @property
    def close_app_(self):

        messages = ["{} exiting in {}".format(self.name, i) for i in range(1, 4)]
        return list(reversed(messages))  # Count down, not up

    def close_app(self):
        self.console_print(self.close_app_)
