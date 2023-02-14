import time

import pybit
import telebot

from Api import Api
from main import set_the_globals_and_trade

api_key_user = ""
api_secret_user = ""
api: Api = None

token = ""

bot_mine = telebot.TeleBot(token)

name_of_coin = ""


def check_api():
    print(api_key_user)


def check_api_secret():
    print(api_secret_user)


def telegram_bot():
    global bot_mine
    bot = bot_mine

    @bot.message_handler(commands=["start_u"])
    def start_message(message):
        bot.send_message(message.chat.id, "Hello friend! Write the '/api_key' to enter your api_key")

    @bot.message_handler(commands=["api_key"])
    def api_key(message):
        msg = bot.send_message(message.chat.id, "Your 'api_key' is: ")
        bot.register_next_step_handler(msg, api_key_continue)

    def api_key_continue(message):
        global api_key_user
        api_key_user = message.text
        check_api()
        bot.send_message(message.chat.id, "Enter '/api_secret' to enter your api_secret")

    @bot.message_handler(commands=["api_secret"])
    def api_secret(message):
        msg = bot.send_message(message.chat.id, "Your 'api_secret' is: ")
        bot.register_next_step_handler(msg, api_secret_continue)

    def api_secret_continue(message):
        global api_secret_user
        api_secret_user = message.text
        check_api_secret()
        bot.send_message(message.chat.id, "Enter '/name_of_coin' to set the coin")

    @bot.message_handler(commands=["name_of_coin"])
    def name_of_coin_u(message):
        msg = bot.send_message(message.chat.id, "Your 'name_of_coin' is: ")
        bot.register_next_step_handler(msg, name_of_coin_continue)

    def name_of_coin_continue(message):
        global name_of_coin
        name_of_coin = message.text
        print(name_of_coin)
        bot.send_message(message.chat.id, "Enter '/trade' to start")

    @bot.message_handler(commands=["info"])
    def check(message):
        if api is not None:
            bot.send_message(message.chat.id,
                             "Info: \n\n"
                             + name_of_coin + ": " + str(api.get_price(name_of_coin + "USDT")) + '\n\n'
                             + "Unrealised PNL: " + str(api.get_unrealised_pnl(name_of_coin))
                             )

    @bot.message_handler(commands=["balance"])
    def balance(message):
        if api is not None:
            bot.send_message(message.chat.id, "Your balance: " + str(api.get_equity("USDT")) + str(" 💲"))

    @bot.message_handler(commands=["trade"])
    def api_secret(message):
        bot.send_message(message.chat.id, "Let's go")
        trade(message)

    def trade(message):

        bot.send_message(message.chat.id, "Checking for correct API...")

        global api
        api = Api(api_key_user, api_secret_user)

        try:
            bot.send_message(message.chat.id, "Your balance on futures " + str(api.get_balance("USDT")))

            bot.send_message(message.chat.id,
                             "Last price for " + name_of_coin + "\n" + str(api.get_price(name_of_coin + "USDT")))

        except pybit.exceptions.InvalidRequestError:

            bot.send_message(message.chat.id, "You give me wrong api_key or api_secret")
            bot.send_message(message.chat.id, "Try again by using '/start'")

        set_the_globals_and_trade(bot, message, api, name_of_coin, api_key_user, api_secret_user)

    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5)
            continue


if __name__ == '__main__':
    telegram_bot()
