import requests
import base64


class HermesConnection(object):

    url = "https://estasney1.pythonanywhere.com{}"
    url_debug = "http://127.0.0.1:5000{}"

    def __init__(self, username, password, debug=False):
        self.s = requests.session()
        self.username = username
        self.password = password
        if debug:
            self.base_url = self.url_debug
        else:
            self.base_url = self.url
        self.api_token = None

    def get_api_token(self):
        auth_header_val = "{}:{}".format(self.username, self.password)
        auth_header_val_enc = base64.b64encode(auth_header_val.encode()).decode()
        self.s.headers.update({'Authorization': "Basic " + auth_header_val_enc})
        token_url = self.base_url.format("/api/v1/token")
        response = self.s.post(token_url)
        if response.status_code == 401 or response.status_code == 500:
            return False
        token = response.json()['token']
        self.api_token = token
        self.s.headers.pop('Authorization')
        self.s.headers.update({'Api-Key': token})
        return True


class LocalHermesConnection(HermesConnection):

    def __init__(self, username, password, items, debug=False):
        super().__init__(username, password, debug)
        self.items = items
        self.get_api_token()

    def checkin_item(self, profile_data):
        self.s.post(self.base_url.format("/api/v1/profiles"), json=profile_data)


class DistributedHermesConnection(HermesConnection):

    def __init__(self, username, password, debug=False):
        super().__init__(username, password, debug)
        self.available_queues = []
        self.active_queue = None

    def get_queues(self):
        available_queues = self.s.get(self.base_url.format("/api/v2/queue/list")).json()['queues']
        return available_queues

    def set_active_queue(self, queue_id):
        for q in self.available_queues:
            if q['queue_id'] == queue_id:
                self.active_queue = q

    def checkout_items(self, n_items, queue_id):
        data = {'queue_id': queue_id, 'n_items': int(n_items)}
        response = self.s.post(self.base_url.format("/api/v2/queue/fetch"), json=data)
        items = response.json()['items']
        return items

    def checkin_item(self, item_id, profile_data):
        data = {'item_id': item_id, 'data': profile_data}
        self.s.post(self.base_url.format("/api/v2/queue/complete"), json=data)

    def checkin_item_failure(self, item, n_attempts):
        data = {'item_id': item['id'], 'attempts': n_attempts}
        self.s.post(self.base_url.format("/api/v2/queue/invalid"), json=data)
