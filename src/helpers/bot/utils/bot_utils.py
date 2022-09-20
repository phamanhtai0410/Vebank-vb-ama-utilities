from src.helpers.vechain import make_call, make_transact
from src.exceptions.bot import BotEx
from pydash import get
from src.constants import BotType


class VIP180:
    def __init__(self, address):
        self.symbol = None
        self.address = address
        self.decimals = None
        self.initialized = None

    def initialize(self, rpc_url: str):
        self.decimal = 18
        self.initialized = True

    def get_balance(self, rpc_url: str, address: str):
        if not self.initialized:
            self.initialize(rpc_url)

        resp = make_call(
            contract_address=self.address,
            abi_file_name='VIP180',
            call_function_name="balanceOf",
            params=[
                address
            ]
        )

        if not resp:
            raise BotEx(message=f"Bot Exception: Get Balance of token {address} failed")

        return resp

    def get_symbol(self, rpc_url: str):
        if not self.initialized:
            self.initialize(rpc_url)

        resp = make_call(
            contract_address=self.address,
            abi_file_name='VIP180',
            call_function_name="symbol",
            params=[]
        )

        if not resp:
            raise BotEx(message=f"Bot Exception: Get Symbol of token {self.address} failed")

        _symbol = resp["0"][1:] if resp["0"] in BotType.SPECIAL_SYMBOL else resp["0"]
        self.symbol = _symbol
        return _symbol

    def get_decimals(self, rpc_url: str):
        if not self.initialized:
            self.initialize(rpc_url)

        resp = make_call(
            contract_address=self.address,
            abi_file_name='VIP180',
            call_function_name="decimals",
            params=[]
        )

        if not resp:
            raise BotEx(message=f"Bot Exception: Get Decimals of token {self.address} failed")

        _decimals = resp["0"][1:] if resp["0"] in BotType.SPECIAL_SYMBOL else resp["0"]
        self.decimals = _decimals
        return _decimals


class Pair:
    def __init__(self, pair_address):
        self.pair_address = pair_address

    def get_reserves(self):
        _resp_get_reserves = make_call(
            contract_address=self.pair_address,
            abi_file_name="PoolPair",
            call_function_name="getReserves",
            params=[]
        )
        if not _resp_get_reserves:
            return None, None
        return get(_resp_get_reserves, "_reserve0"), get(_resp_get_reserves, "_reserve1")


