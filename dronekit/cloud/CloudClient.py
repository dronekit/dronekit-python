import requests

class CloudError(Exception):
    def __init__(self, type, message, response):
        self.type = type
        self.message = message
        self.response = response

    def __str__(self):
        return "%s [%s] (%s)" % (self.type, self.response.url, self.message)

    def __repr__(self):
        return "%s(type=%s)" % (self.__class__.__name__, self.type)

class CloudClient(object):
    BASE_URL = 'http://api.droneshare.com/api/v1/'
    REST_CALLS = {
        'staticMap': 'staticMap',
        'analysis': 'analysis.json',
        'geo': 'messages.geo.json',
        'messages': 'messages.json',
        'parameters': 'parameters.json'
    }

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'Authorization': "DroneApi apikey=\"%s\"" % self.apikey}

    def __getattr__(self, name):
        def method(*args):
            find_action = name.split('_')
            find_args = args
            action_url = find_action[0]
            if (len(find_action) > 1):
                if (find_action[1] in self.REST_CALLS):
                    if (len(args) > 0):
                        action_url += "/%s/%s" % (str(args[0]), self.REST_CALLS[find_action[1]])
                    else:
                        action_url += "/%s" % find_action[1]
                else:
                    action_url += "/%s/%s" % (str(args[0]), find_action[1])
            return self._request(action_url, args[1:])
        return method

    def _request(self, url, data):
        self.response = requests.get("%s%s" % (self.BASE_URL, url), headers=self.headers)
        if self.response.status_code == 404:
            raise CloudError(self.response.status_code, 'Unkown Endpoint', self.response)
        return self.response
