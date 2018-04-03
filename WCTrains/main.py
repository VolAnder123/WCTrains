import datetime
from botHandler import BotHandler
from trainFinder import TrainFinder

bot = BotHandler('588416451:AAHeNyVIy_ARN9kmPhM62ARjNE1cwFFf5JE') 
trainFinder = TrainFinder("https://tickets.transport2018.com/free-train/results?event_id=9", datetime.datetime(2018, 6, 15), datetime.datetime(2018, 6, 17, 22))

def messageHandler():
    new_offset = None

    while True:
        last_update = bot.get_last_update(new_offset)

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']

        if last_chat_text.lower() == "ты спортсмен?":
            bot.send_message(last_chat_id, 'иди нахуй')

        new_offset = last_update_id + 1

def findFreeTrains():
	trains = trainFinder.findFreeTrains()
	count = len(trains)
	if(count > 0):
		chatIds = bot.getAllChatIds()
		for chatId in chatIds:
			bot.send_message(chatId, 'Э, ебанько, там свободные места есть!')

def main(): 
	findFreeTrains()
	#messageHandler()


if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()