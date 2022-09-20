import time
from src.config import DefaultConfig
from src.helpers.bot.orders_handler.bot_orders_handler import BotOrdersHandler
import src.helpers.bot.utils as utils
from .const_product import generate_constant_product_ladders, ConstantProductLadder
from src.exceptions.bot import BotEx


def new_constant_product_bot(
    orders_handler: BotOrdersHandler,
    price_gap: float,
    rpc_url: str
):
    base_token, quote_token = orders_handler.get_trading_tokens()
    if not base_token or not quote_token:
        raise BotEx(message="Bot Exceptions: Trading pair not found")

    base_oracle_price, quote_oracle_price = orders_handler.get_oracle_prices()
    if not base_oracle_price or not quote_oracle_price:
        raise BotEx(message="Bot Exceptions: Trading pair's price from oracle not found")

    print("Oracle Prices : ", base_oracle_price, quote_oracle_price)
    # Exactly price = quote_amount / base_amount = base_oracle_price / quote_oracle_price
    exactly_price = base_oracle_price / quote_oracle_price

    # Range of rebalanced price between a deviation set in bot configurations
    min_price = exactly_price * (1 - DefaultConfig.BOT_DEVIATION / 2)
    max_price = exactly_price * (1 + DefaultConfig.BOT_DEVIATION / 2)

    print("Min Price = ", min_price)
    print("Max Price = ", max_price)

    bot = ConstantProductBot(
        orders_handler,
        base_token,
        quote_token,
        {},
        min_price,
        max_price,
        price_gap,
        rpc_url
    )
    return bot


class ConstantProductBot:
    def __init__(
            self,
            orders_handler: BotOrdersHandler,
            base_token: utils.VIP180,
            quote_token: utils.VIP180,
            ladder_map: dict,
            min_price: float,
            max_price: float,
            price_gap: float,
            rpc_url: str
    ):
        self.orders_handler = orders_handler
        self.base_token = base_token
        self.quote_token = quote_token
        self.ladder_map = ladder_map
        self.min_price = min_price
        self.max_price = max_price
        self.price_gap = price_gap
        self.rpc_url = rpc_url

    def run(self):
        self.initialize()
        # print("*** Ladder Map = ", self.ladder_map)
        for _key, _val in self.ladder_map.items():
            # print(f"**** + {_key} : {_val.__dict__}")
            self.implement_order(_key)

    def initialize(self):
        self.orders_handler.cancel_all_pending_orders()

        bot_current_base_balance = self.base_token.get_balance(self.rpc_url, self.orders_handler.address)
        if not bot_current_base_balance:
            raise BotEx(message="Bot Exception: Could not get balance of token base")

        bot_current_quote_balance = self.quote_token.get_balance(self.rpc_url, self.orders_handler.address)
        if not bot_current_quote_balance:
            raise BotEx(message="Bot Exception: Could not get balance of token quote")

        base_token_amount, quote_token_amount = self.orders_handler.pair.get_reserves()
        print("Current Reserves : ", base_token_amount, quote_token_amount)

        if not base_token_amount or not quote_token_amount:
            raise BotEx(
                f"Bot Exception: Cannot get current reserves in pool pair {self.orders_handler.pair.pair_address}"
            )

        ladders = generate_constant_product_ladders(
            base_token_amount,
            quote_token_amount,
            self.min_price,
            self.max_price,
            self.price_gap
        )

        center_price = quote_token_amount / base_token_amount
        for ladder in ladders:
            if ladder.up_price <= center_price:
                self.create_order(ladder, utils.BUY)
            else:
                self.create_order(ladder, utils.SELL)

    def create_order(self, ladder: ConstantProductLadder, side: str):
        if side == utils.SELL:
            price = ladder.up_price
        else:
            price = ladder.down_price

        order_id = self.orders_handler.create_order(
            price,
            ladder.amount,
            side,
            utils.ORDER_OPEN,
            0
        )

        if not order_id:
            raise BotEx("Bot Exception: Create order failed")
        else:
            self.ladder_map[str(order_id)] = ladder

    def implement_order(self, order_id):
        self.orders_handler.implement_order(order_id)

    def elegant_exit(self):
        self.orders_handler.cancel_all_pending_orders()









