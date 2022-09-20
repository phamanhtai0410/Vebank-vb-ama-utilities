from src.config import DefaultConfig
from src.constants import BotType
import json
from src.helpers.bot.orders_handler.bot_orders_handler import BotOrdersHandler
from src.helpers.bot.algorithm import new_constant_product_bot
from src.config import DefaultConfig
from src.helpers.bot.utils import VIP180, Pair
from src.config import DefaultConfig
from lib.enums.database import DBName
from pymodm import connect


class BotExecutedCommands:
    def __init__(self, base_token_address, quote_token_address, pair_address, mq):
        self.base_token_address = base_token_address
        self.quote_token_address = quote_token_address
        self.pair_address = pair_address
        self.mq = mq

    def main_bot_running(self):
        botType = DefaultConfig.BOT_TYPE
        if botType == BotType.CONSTANT_PRODUCT:
            self.start_constant_product_bot(
                self.base_token_address,
                self.quote_token_address,
                self.pair_address,
                self.mq
            )

    @staticmethod
    def start_constant_product_bot(base_token, quote_token, pair_address, mq):
        connect(DefaultConfig.DB_APP, connect=False, alias=DBName.POOL)

        with open("src/keystore", "r") as _f:
            _keystore = json.load(_f)

        maker_orders_handler = BotOrdersHandler(
            VIP180(base_token),
            VIP180(quote_token),
            Pair(pair_address),
            DefaultConfig.RPC_URI,
            _keystore,
            mq
        )

        bot = new_constant_product_bot(
            maker_orders_handler,
            DefaultConfig.PRICE_GAP,
            DefaultConfig.RPC_URI
        )

        bot.run()




