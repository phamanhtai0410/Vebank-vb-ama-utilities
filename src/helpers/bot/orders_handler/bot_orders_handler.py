from src.utils import *
from src.helpers.bot.utils import VIP180, Pair
import src.helpers.bot.utils as utils
from src.exceptions.bot import BotEx
from src.helpers.request import request_inside
from src.config import DefaultConfig
from pydash import get
from src.models.amm_orders import AmmOrdersModel
from bson import ObjectId
from lib.utils import amqp


class BotOrdersHandler:
    def __init__(
            self,
            base_token: VIP180,
            quote_token: VIP180,
            pair: Pair,
            rpc_url: str,
            keystore: dict,
            mq: amqp.AmqpConnection
    ):
        self.base_token = base_token
        self.quote_token = quote_token
        self.pair = pair
        self.rpc_url = rpc_url
        self.keystore = keystore
        self.mq = mq

        # Get address from keystore
        self.address = keystore_to_address(keystore)

        # Store order_id
        self.order_id = 0

    def implement_order(
            self,
            order_id
    ):
        order_info = self.get_order(order_id)
        if not order_info:
            raise BotEx(f"Get order with id #{order_id} failed")
        else:
            print("*** Order infors : ", order_info)
            self.mq.publish(
                payload={
                    "_id": str(get(order_info, "_id"))
                }
            )
            pass

    def create_order(
            self,
            price,
            amount,
            side,
            order_type,
            expired_time
    ):
        resp = AmmOrdersModel.insert({
            "env": DefaultConfig.ENV,
            "pair_address": self.pair.pair_address,
            "base_token": self.base_token.address,
            "quote_token": self.quote_token.address,
            "price": price,
            "amount_in_base": amount,
            "side": side,
            "order_type": order_type,
            "expired_time": expired_time,
            "status": utils.STATUS_PENDING
        })
        return str(get(resp, "_id"))

    @staticmethod
    def cancel_order(order_id):
        AmmOrdersModel.update_one(
            filter={
                "_id": ObjectId(order_id)
            },
            obj={
                "order_type": utils.ORDER_CLOSE,
                "status": utils.STATUS_DONE
            }
        )

    def cancel_all_pending_orders(self):
        _orders = self.get_all_pending_orders()
        for _order in _orders:
            self.cancel_order(get(_order, "_id"))
        pass

    def get_all_pending_orders(self):
        return AmmOrdersModel.find(
            filter={
                "env": DefaultConfig.ENV,
                "pair_address": self.pair.pair_address
            },
            with_cache=False
        )

    def get_trading_tokens(self):
        return self.base_token, self.quote_token

    @staticmethod
    def get_order(order_id):
        return AmmOrdersModel.find_one(
            filter={
                "_id": ObjectId(order_id)
            },
            with_cache=False
        )

    def get_oracle_prices(self):
        try:
            _base_symbol = self.base_token.get_symbol(self.rpc_url)
            _quote_symbol = self.quote_token.get_symbol(self.rpc_url)
            print("Symbol = ", _base_symbol, _quote_symbol)

            _base_decimals = self.base_token.get_decimals(self.rpc_url)
            _quote_decimals = self.quote_token.get_decimals(self.rpc_url)
            print("Decimals = ", _base_decimals, _quote_decimals)

            _base_oracle_res = request_inside(
                url=f"{DefaultConfig.API_URL}/v1/oracle/price/symbol/{_base_symbol}",
                method="GET",
                params=[],
                body={}
            )
            _quote_oracle_res = request_inside(
                url=f"{DefaultConfig.API_URL}/v1/oracle/price/symbol/{_quote_symbol}",
                method="GET",
                params=[],
                body={}
            )
            if len(get(_base_oracle_res['data'], "list_price")) == 0 or len(get(_base_oracle_res['data'], "list_price")) == 0:
                raise BotEx(f"Bot Exception: Invalid price from oracle for pair {self.pair.pair_address} 2")

            _base_oracle_price, _quote_oracle_price = None, None
            for _item in get(_base_oracle_res['data'], "list_price"):
                for _key, _val in _item.items():
                    if _val:
                        _base_oracle_price = float(_val)
                        break

            for _item in get(_quote_oracle_res['data'], "list_price"):
                for _key, _val in _item.items():
                    if _val:
                        _quote_oracle_price = float(_val)
                        break
            return _base_oracle_price * 10 ** _base_decimals, _quote_oracle_price * 10 ** _quote_decimals
        except Exception as e:
            print(e)
            raise BotEx(f"Bot Exception: error when get price from oracle for pair {self.pair.pair_address} 3")







