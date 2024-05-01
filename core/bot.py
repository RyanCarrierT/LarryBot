from core.operation import Operation

from binance.client import Client

class Bot:
    """
    This class is intended to model a single bot.

    A bot has a low and a high bound, operating only if the currency price is comprised between those.
    Once the bot is active, it places a limit buy order, when filled, the bot places a sell order at a slightly higher price.  
    
    Class Attributes:
        ...

    Instance Attributes:
        ...

    Methods:
        ...
    """

    SELLS_BENEFITS = 0.0001 # Difference between sell and buy operations price expressed as a percentage of buy price

    def __init__(self, client: Client, currency: str,  capital: float, low_bound: float, high_bound: float, bot_id: int = 0):
        self._client = client

        self._currency = currency

        self._capital = capital

        self._low_bound = low_bound
        self._high_bound = high_bound

        self._bot_id = bot_id

        self.latest_operation = Operation(
            "",
            "",
            "",
            0,
            0
        )

    def place_order(self, price: float):
        if self.latest_operation.operation_type != Client.SIDE_BUY:
            self._place_buy_order(price)
        else:
            self._place_sell_order()

    def _place_buy_order(self, price: float):
        quantity = self._capital/price

        order = self._client.create_order(
            symbol=self._currency,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce=Client.TIME_IN_FORCE_GTC,
            quantity=f"{quantity:.2f}",
            price=price
        )

        self.latest_operation = Operation(
            order["orderId"],
            Client.SIDE_BUY,
            self._currency,
            price,
            quantity
        )

        print(f"Bot {self._bot_id} passed buy operation at price : {price} for quantity : {quantity}")

    def _place_sell_order(self):
        price = self.latest_operation.price * (1 + Bot.SELLS_BENEFITS)

        order = self._client.create_order(
            symbol=self._currency,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce=Client.TIME_IN_FORCE_GTC,
            quantity=f"{self.latest_operation.quantity:.2f}", # Quantity bought at last buy operation
            price=f"{price:.1f}"
        )

        self.latest_operation = Operation(
            order["orderId"],
            Client.SIDE_SELL,
            self._currency,
            f"{price:.1f}",
            self.latest_operation.quantity
        )
        
        self._capital = price * self.latest_operation.quantity

        print(f"Bot {self._bot_id} passed sell operation at price : {price} for quantity : {self.latest_operation.quantity}")
