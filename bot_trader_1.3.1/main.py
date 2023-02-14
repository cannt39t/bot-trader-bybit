from flask import *

from Api import Api

import telebot
from telebot.types import Message

app = Flask(__name__)

bot_u: telebot.TeleBot = None
message_u: Message = None
api_u: Api = None
name_coin_u = ""

api_key_u = ""
api_secret_u = ""

count_ex = 0

@app.route('/position', methods=['GET', 'POST'])
async def signals():
    print("got position")
    json_data = request.json
    buy_or_sell = str(json_data["comment"])
    close = float(json_data["close"])
    if buy_or_sell == "open_long":
        await bot_open_long(message_u, api_u, close)
    if buy_or_sell == "open_short":
        await bot_open_short(message_u, api_u, close)
    bot_u.send_message(message_u.chat.id, buy_or_sell)
    return "order"

# async
async def bot_open_long(message, api, close):
    try:
        if api.have_order_short(name_coin_u):
            api.close_position(name_coin_u, "Buy", 1)
            bot_u.send_message(message.chat.id, "#Close SHORT ✅")
        bot_u.send_message(message.chat.id, str(api.place_order(name_coin_u, "Buy", 10)))
        bot_u.send_message(message.chat.id, "#Open LONG 📈")
        bot_u.send_message(message.chat.id, str(api.get_equity("USDT")))

        qty_long = api.get_position_qty(name_coin_u + "USDT", 0)
        part1 = round(qty_long * 0.1, 4)
        price1 = round(close * 1.05, 4)
        price2 = round(close * 1.1, 4)
        price3 = round(close * 1.15, 4)
        price4 = round(close * 1.2, 4)
        price5 = round(close * 1.25, 4)
        price6 = round(close * 1.3, 4)
        price7 = round(close * 1.35, 4)
        api.set_tp_qty(name_coin_u, "Buy", price1, part1)
        api.set_tp_qty(name_coin_u, "Buy", price2, part1)
        api.set_tp_qty(name_coin_u, "Buy", price3, part1)
        api.set_tp_qty(name_coin_u, "Buy", price4, part1)
        api.set_tp_qty(name_coin_u, "Buy", price5, part1)
        api.set_tp_qty(name_coin_u, "Buy", price6, part1)
        api.set_tp_qty(name_coin_u, "Buy", price7, part1)
        bot_u.send_message(message.chat.id, "Set TakeProfits ✅")

    except Exception as e:
        global count_ex, api_key_u, api_secret_u, api_u
        if count_ex == 1:
            global api_u
            api_u = None
            bot_u.send_message(message.chat.id, "❗️BOT STOPPED❗️ \n" +
                               "SOMETHING SERIOUS HAPPENED")
            bot_u.send_message(message.chat.id, "🚫")
        else:
            bot_u.send_message(message.chat.id, e.__str__())
            api_u = Api(api_key_u, api_secret_u)
            bot_u.send_message(message.chat.id, "Recreate API")
            count_ex = count_ex + 1
            # await
            await bot_open_long(message, api_u, close)

    count_ex = 0

# async
async def bot_open_short(message, api, close):
    try:
        if api.have_order_long(name_coin_u):
            api.close_position(name_coin_u, "Sell", 0)
            bot_u.send_message(message.chat.id, "#Close LONG ✅")
        bot_u.send_message(message.chat.id, str(api.place_order(name_coin_u, "Sell", 10)))
        bot_u.send_message(message.chat.id, "#Open SHORT 📉")
        bot_u.send_message(message.chat.id, str(api.get_equity("USDT")))

        qty_short = api.get_position_qty(name_coin_u + "USDT", 1)
        part1 = round(qty_short * 0.1, 4)
        price1 = round(close * 0.95, 4)
        price2 = round(close * 0.9, 4)
        price3 = round(close * 0.85, 4)
        price4 = round(close * 0.8, 4)
        price5 = round(close * 0.75, 4)
        price6 = round(close * 0.7, 4)
        price7 = round(close * 0.65, 4)
        api.set_tp_qty(name_coin_u, "Sell", price1, part1)
        api.set_tp_qty(name_coin_u, "Sell", price2, part1)
        api.set_tp_qty(name_coin_u, "Sell", price3, part1)
        api.set_tp_qty(name_coin_u, "Sell", price4, part1)
        api.set_tp_qty(name_coin_u, "Sell", price5, part1)
        api.set_tp_qty(name_coin_u, "Sell", price6, part1)
        api.set_tp_qty(name_coin_u, "Sell", price7, part1)
        bot_u.send_message(message.chat.id, "Set TakeProfits ✅")

    except Exception as e:
        global count_ex, api_key_u, api_secret_u, api_u
        if count_ex == 1:
            global api_u
            api_u = None
            bot_u.send_message(message.chat.id, "❗️BOT STOPPED❗️ \n" +
                               "SOMETHING SERIOUS HAPPENED")
            bot_u.send_message(message.chat.id, "🚫")
        else:
            bot_u.send_message(message.chat.id, e.__str__())
            api_u = Api(api_key_u, api_secret_u)
            bot_u.send_message(message.chat.id, "Recreate API")
            count_ex = count_ex + 1
            # await
            await bot_open_short(message, api_u, close)

    count_ex = 0


def set_the_globals_and_trade(bot, message, api, name_symbol, api_key, api_secret):
    global bot_u, message_u, api_u, name_coin_u, api_key_u, api_secret_u
    name_coin_u = name_symbol
    bot_u = bot
    message_u = message
    api_u = api
    api_key_u = api_key
    api_secret_u = api_secret


    app.run()
