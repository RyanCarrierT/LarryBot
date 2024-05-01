import time
import datetime

import numpy as np

from binance.client import Client

from scipy.stats import norm

from core.bot import Bot

class Orchestator:
    """
    This class is intended to manage agents activity.

    Class Attributes :
        ...
    
    Instance Attributes:
        ...
    
    Methods:
        ...
    """

    def __init__(self, public_key: str = "", secret_key: str = "", currency: str = "", capital: float = 0, low_bound: float = 0, high_bound: float = 0, price_std_dev: float = 5, bots_number: int = 1):
        
        self._currency = currency

        self._capital = capital

        self._low_bound = low_bound
        self._high_bound = high_bound

        self._price_std_dev = price_std_dev

        self._client = Client(public_key, secret_key, testnet=True)

        self._bots_number = bots_number

        self._bots = []


    def create_bots(self):
        current_price = next(
            (ticker['price'] for ticker in self._client.get_all_tickers() 
             if ticker['symbol'] == self._currency),
            None
        )
        
        if current_price is None:
            raise ValueError("Currency not found in tickers.")
        
        current_price = float(current_price)

        start_points = np.linspace(self._low_bound, self._high_bound, self._bots_number + 1)

        probabilities = [norm.pdf((start_points[i] + start_points[i + 1]) / 2, loc=current_price, scale=self._price_std_dev) for i in range(self._bots_number)]
        probabilities = probabilities/np.sum(probabilities) 

        capitals = [self._capital * prob for prob in probabilities]

        with open("capitals.txt", "a") as file:
            for i in range(len(capitals)):
                print("Bot : " + str(i) + " capital : " + str(capitals[i]))

        for i in range(self._bots_number):
            low_bound = start_points[i]
            high_bound = start_points[i + 1]
            capital_allocation = capitals[i]
            
            bot = Bot(self._client, self._currency, capital_allocation, low_bound, high_bound, i)

            self._bots.append({
                'bounds': (low_bound, high_bound),
                'bot': bot,
            })

            print(f"Created bot : {i} Capital : {capital_allocation} Bounds : {(low_bound, high_bound)}",)

    def run(self):
        while True:
            price = next(
                (
                    ticker['price'] for ticker in self._client.get_all_tickers() 
                    if ticker['symbol'] == self._currency
                ),
                None
            )

            price = float(price)

            bot = next(
                iter(
                    [
                        bot_dict["bot"] for bot_dict in self._bots
                        if bot_dict["bounds"][1] >= price
                    ]
                ), None
            )

            place_order = False

            bot_latest_operation_id = bot.latest_operation.operation_id

            if bot_latest_operation_id:
                bot_latest_operation_status = self._client.get_order(
                    symbol=self._currency,
                    orderId=bot_latest_operation_id
                )
                
                if bot_latest_operation_status["status"] == "FILLED":
                    place_order = True
            else:
                place_order = True

            if place_order:
                bot.place_order(price)

                usdt_balance = [k for k in self._client.get_account()["balances"] if k["asset"] == "USDT"][0]["free"]
                bnb_balance = [k for k in self._client.get_account()["balances"] if k["asset"] == "BNB"][0]["free"]
                
                usdt_locked = [k for k in self._client.get_account()["balances"] if k["asset"] == "USDT"][0]["locked"]
                bnb_locked = [k for k in self._client.get_account()["balances"] if k["asset"] == "BNB"][0]["locked"]

                now = datetime.datetime.now()
                formatted_timestamp = now.strftime("%d/%m/%y %H:%M:%S")

                print(formatted_timestamp + " : USDT Balance : ", usdt_balance, end=" ")
                print("BNB Balance : ", bnb_balance, end=" ")

                print("Locked USDT : ", usdt_locked, end=" ")
                print("Locked BNB : ", bnb_locked, end="")
                
                with open("balances_history.txt", "a") as file:
                    print(formatted_timestamp + " : USDT Balance : ", usdt_balance, file=file)
                    print(formatted_timestamp + " : BNB Balance : ", bnb_balance, file=file)

                with open("locked_history.txt", "a") as file:
                    print(formatted_timestamp + " : Locked USDT : ", usdt_locked, file=file)
                    print(formatted_timestamp + " : Locked BNB : ", bnb_locked, file=file)
                
                with open("orders_history.txt", "a") as file:
                    print(formatted_timestamp + " : USDT orders : ", self._client.get_all_orders(symbol=self._currency), file=file)
                    print(formatted_timestamp + " : BNB orders : ", self._client.get_all_orders(symbol=self._currency), file=file)

            time.sleep(1)