import requests  
import datetime
import logging

class BotHandler:
    def __init__(self, token, defaultChatId):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.defaultChatId = defaultChatId

    def getUpdates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.api_url + method, params)
        json = None
        if (response.status_code == 200):
            json = response.json()['result']
        else:
            logging.warning('Not successs request in botHandler.get_updates(), Reason: {0}, Code: {1}'.format(response.reason, response.status_code))
        return json

    def sendMessage(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def getLastUpdate(self, offset=None):
        get_result = self.getUpdates(offset)

        if get_result is not None and len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update

    def getAllChatIds(self):	
        return [defaultChatId]

