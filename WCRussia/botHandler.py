import requests  
import datetime
import logging

class BotHandler:
    def __init__(self, token, defaultChatIds):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.defaultChatIds = defaultChatIds

    def getUpdates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.api_url + method, params)
        json = None
        if (response.status_code == 200):
            json = response.json()['result']
        else:
            logging.warning('Not success request in botHandler.get_updates(), Reason: {0}, Code: {1}'.format(response.reason, response.status_code))
        return json

    def sendMessage(self, chatId, message):
        method = 'sendMessage'
        params = {'chat_id': chatId, 'text': message}
        requests.post(self.api_url + method, params)

    def sendMessageToAll(self, message):
        chatIds = self.getAllChatIds()
        for chatId in chatIds:
            self.sendMessage(chatId, message)

    def getLastUpdate(self, offset=None):
        get_result = self.getUpdates(offset)

        if get_result is not None and len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update

    def getAllChatIds(self):	
        return self.defaultChatIds

