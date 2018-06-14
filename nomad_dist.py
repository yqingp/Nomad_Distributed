from components import HermesConnection, UserInterface, NomadDriver


class Program(object):

    def __init__(self, browser, ui, network, debug):
        self.browser = browser
        self.ui = ui
        self.network = network
        self.debug = debug
        self.tasks = None
        if debug:
            self.init_ui("Nomad - Distributed Edition - DEBUG", print_delay=0)
        else:
            self.init_ui("Nomad - Distributed Edition", print_delay=2)

    def init_browser(self, *args, **kwargs):
        self.browser = self.browser(*args, **kwargs)

    def init_ui(self, *args, **kwargs):
        self.ui = self.ui(*args, **kwargs)

    def init_network(self, *args, **kwargs):
        self.network = self.network(*args, **kwargs)

    # Order of Operations
    # UI - Welcome - welcome()
    # UI - Auth - welcome()
    # Network - Do Auth - setup_network()
    # Browser - Open - setup_browser()
    # UI - Prompt Browser Login - explain_browser_login()
    # Network - Fetch available Queues - fetch_all_queues()
    # UI - Prompt to Select Queue - prompt_select_queue()
    # UI - Prompt # Tasks - prompt_task_count()
    # Network - Fetch Tasks - fetch_tasks()
    # Browser - Do Tasks & Network - Save Tasks
    # UI - Exit

    """
    UI
    """

    @property
    def ui_username(self):
        return self.ui.username

    @property
    def ui_password(self):
        return self.ui.password

    def welcome(self):
        self.welcome_()
        self.welcome_login()

    def welcome_(self):
        return self.ui.welcome_()

    def welcome_login(self):
        self.ui.welcome_login_()

    def explain_browser_login(self):
        # This waits until user confirms via input
        self.ui.explain_browser_login_()

    def await_login_confirmed(self):
        self.ui.await_login_confirmed()

    def prompt_select_queue(self, available_queues):
        selected_queue = self.ui.prompt_select_queue_(available_queues)
        # {'queue_id' : 1, 'friendly_id': 'something'}
        return selected_queue

    def prompt_task_count(self, selected_queue):
        n_tasks = self.ui.prompt_task_count_(selected_queue)
        return n_tasks

    def tasks_complete(self):
        self.ui.close_app()

    """
    Network
    """

    def setup_network(self, retry=False):
        if retry:
            self.ui.retry_login()
        self.init_network(username=self.ui_username, password=self.ui_password, debug=self.debug)
        login_success = self.network.get_api_token()
        if login_success:
            return True
        else:
            self.setup_network(retry=True)

    def fetch_all_queues(self):
        available_queues = self.network.get_queues()
        return available_queues

    def fetch_tasks(self, n_items):
        tasks = self.network.checkout_items(n_items, self.ui.queue_id)
        # Dict with keys ['id', 'queue_id', 'item_data']
        self.tasks = tasks
        self.ui.show_items_received(n_items, tasks)

    def checkin_task(self, task, task_data):
        item_id = task['id']
        self.network.checkin_item(item_id, task_data)


    """
    Browser
    """

    def setup_browser(self):
        print("")
        print(" CHROME LOG (Ignore This) ".center(80, "="))
        self.init_browser(start_page="https://www.linkedin.com/recruiter")
        print(" END CHROME LOG ".center(80, "="))
        print("")

    def do_task(self):
        if not self.tasks:
            return False
        new_task = self.tasks.pop()
        url = new_task['item_data']
        task_data = self.browser.do_task(url)
        self.ui.finished_one_task(url)
        return new_task, task_data


nomad_dist = Program(browser=NomadDriver, ui=UserInterface, network=HermesConnection, debug=False)
try:
    nomad_dist.welcome()
    nomad_dist.setup_network()
    available_queues = nomad_dist.fetch_all_queues()
    selected_queue = nomad_dist.prompt_select_queue(available_queues)
    n_items = nomad_dist.prompt_task_count(selected_queue)
    nomad_dist.fetch_tasks(n_items)
    nomad_dist.explain_browser_login()
    nomad_dist.setup_browser()
    nomad_dist.await_login_confirmed()
    tasking = True
    while tasking is True:
        task = nomad_dist.do_task()
        if not task:
            try:
                nomad_dist.browser.driver.quit()
            except AttributeError:
                pass
            tasking = False
            break
        nomad_dist.checkin_task(task[0], task[1])
except Exception as e:
    print(e)
finally:
    nomad_dist.tasks_complete()
    nomad_dist.browser.driver.quit()
    print("You may now close this window... Goodbye!")



