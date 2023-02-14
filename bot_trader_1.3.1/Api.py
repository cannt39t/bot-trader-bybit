import time

import requests
from pybit import inverse_perpetual
from pybit import usdt_perpetual

endpoint = "https://api.bybit.com"
# https://api-testnet.bybit.com
# https://api.bybit.com


class Api:

    def __init__(self, apikey, apisecret):
        self.api_key = apikey

        self.api_secret = apisecret

        self.session_unauth = inverse_perpetual.HTTP(
            endpoint=endpoint
        )

        self.session_auth_inverse = inverse_perpetual.HTTP(
            endpoint=endpoint,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

        self.session_auth_perp = usdt_perpetual.HTTP(
            endpoint=endpoint,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

    def get_balance(self, name):
        return (self.session_auth_inverse.get_wallet_balance(coin=name))["result"][name]["available_balance"]

    def get_equity(self, name):
        return (self.session_auth_inverse.get_wallet_balance(coin=name))["result"][name]["equity"]

    def get_price(self, name):
        return (self.session_unauth.latest_information_for_symbol(
            symbol=name
        )['result'][0]['last_price'])

    def get_position(self, name):
        return self.session_auth_perp.my_position(symbol=name)

    def get_position_qty(self, name, long_0_short_1):
        return self.get_position(name)["result"][long_0_short_1]["size"]

    def place_order(self, name, position, leverage):
        v = "{:.3f}".format(round(self.get_balance("USDT") / 5 * leverage) / float(self.get_price(name + "USDT")))
        return (self.session_auth_perp.place_active_order(
            symbol=name + "USDT",
            side=position,
            order_type="Market",
            qty=v,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        ))

    def place_order_tp_sl(self, name, position, leverage, tp, sl):
        v = "{:.3f}".format(round(self.get_balance("USDT") / 5 * leverage) / float(self.get_price(name + "USDT")))
        return (self.session_auth_perp.place_active_order(
            symbol=name + "USDT",
            side=position,
            order_type="Market",
            qty=v,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False,
            take_profit=tp,
            stop_loss=sl,
        ))

    def close_position(self, name, side, long_0_short_1):
        return (self.session_auth_perp.place_active_order(
            symbol=name + "USDT",
            side=side,
            order_type="Market",
            qty=self.get_position_qty(name + "USDT", long_0_short_1),
            time_in_force="GoodTillCancel",
            reduce_only=True,
            close_on_trigger=False
        ))

    def set_leverage(self, name, long, short):
        while True:
            try:
                return (self.session_auth_perp.set_leverage(
                    symbol=name + "USDT",
                    buy_leverage=long,
                    sell_leverage=short
                ))
            except requests.exceptions.ReadTimeout:
                print("Got problems on server")
                time.sleep(5)

    def have_no_orders(self, symbol):
        json = self.get_position(symbol + "USDT")
        size_long = json["result"][0]['size']
        size_short = json["result"][1]['size']
        if (size_short == 0) and (size_long == 0):
            return True
        return False

    def have_order_long(self, symbol):
        json = self.get_position(symbol + "USDT")
        size_long = json["result"][0]['size']
        if size_long != 0:
            return True
        return False

    def have_order_short(self, symbol):
        json = self.get_position(symbol + "USDT")
        size_short = json["result"][1]['size']
        if size_short != 0:
            return True
        return False

    def get_unrealised_pnl(self, symbol):
        if self.have_order_short(symbol):
            return self.get_position(symbol + "USDT")["result"][1]["unrealised_pnl"]
        if self.have_order_long(symbol):
            return self.get_position(symbol + "USDT")["result"][0]["unrealised_pnl"]
        return 0

    def set_tp_qty(self, symbol, side, price, qty):
        return (self.session_auth_perp.set_trading_stop(
            symbol=symbol + "USDT",
            side=side,
            take_profit=price,
            tp_size=qty
        ))