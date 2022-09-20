from src.helpers.vechain import make_transact, make_call
from src.services.ama_config import AMAConfigService
from src.exceptions.bot import BotEx
from src.config import DefaultConfig
from lib.util import dt_utcnow
from pydash import get
import src.helpers.bot.utils as utils
from src.helpers.pool import get_amount_out, get_amount_in
from src.constants import AppConstants


class RebalancePair:
    def __init__(self, env, pair_address, amount, side):
        self.amount = amount
        self.side = side
        self.token1 = None
        self.token0 = None
        self.reserve0 = None
        self.reserve1 = None
        self.env = env
        self.pair_address = pair_address

    def cache_pair_reserves(self):
        try:
            # Get reserves
            _get_reserves_resp = make_call(
                contract_address=self.pair_address,
                abi_file_name="PoolPair",
                call_function_name="getReserves",
                params=[]
            )
            if _get_reserves_resp == Exception:
                raise BotEx(f"Bot Exception: Get reserves failed with pair {self.pair_address}")
            self.reserve0 = get(_get_reserves_resp, "_reserve0")
            self.reserve1 = get(_get_reserves_resp, "_reserve1")
        except Exception as e:
            print(f"Exception in get reserves : {e}")

    def cache_tokens_address(self):
        try:
            # Get tokens address
            _get_token0_resp = make_call(
                contract_address=self.pair_address,
                abi_file_name="PoolPair",
                call_function_name="token0",
                params=[]
            )
            _get_token1_resp = make_call(
                contract_address=self.pair_address,
                abi_file_name="PoolPair",
                call_function_name="token1",
                params=[]
            )
            if type(_get_token0_resp) == Exception or type(_get_token1_resp) == Exception:
                raise BotEx(f"Bot Exception: Get token address failed with pair {self.pair_address}")
            self.token0, self.token1 = get(_get_token0_resp, "0"), get(_get_token1_resp, "0")
        except Exception as e:
            print(f"Exception in get reserves : {e}")

    def approve(self):
        try:
            if self.side == utils.BUY:
                _approve_resp = make_transact(
                    contract_address=self.token0,
                    abi_file_name="VIP180",
                    transact_function_name="approve",
                    params=[
                        AMAConfigService.get_router_address(self.env),
                        self.amount
                    ]
                )
            else:
                _approve_resp = make_transact(
                    contract_address=self.token1,
                    abi_file_name="VIP180",
                    transact_function_name="approve",
                    params=[
                        AMAConfigService.get_router_address(self.env),
                        int(get_amount_in(
                            _amount_out=self.amount,
                            _reserve_in=self.reserve1,
                            _reserve_out=self.reserve0
                        ))
                    ]
                )
            if type(_approve_resp) == Exception:
                raise BotEx(f"Bot Exception: approve failed")
        except Exception as e:
            print(f"Exception in approve : {e}")
            return None

    def swap(self):
        try:
            _router_address = AMAConfigService.get_router_address(self.env)
            """
                In defaults, we recognize that BUY is BUY quote token by swapping base tokens and get quote tokens.
                SELL: SELL quote tokens means that swaps quote tokens and get base tokens
            """
            if self.side == utils.BUY:
                _amount_in = self.amount
                _amount_out_min = int(get_amount_out(
                    _amount_in=self.amount,
                    _fee=AppConstants.SWAP_FEE,
                    _reserve_in=self.reserve0,
                    _reserve_out=self.reserve1,
                ))
                path = [
                    self.token0,
                    self.token1
                ]
            else:
                _amount_in = int(get_amount_in(
                    _amount_out=self.amount,
                    _reserve_in=self.reserve1,
                    _reserve_out=self.reserve0
                ))
                _amount_out_min = self.amount
                path = [
                    self.token1,
                    self.token0
                ]

            _swap_params = [
                _amount_in,
                _amount_out_min,
                path,
                DefaultConfig.CALLER,
                int(dt_utcnow().timestamp()) + 5 * 60
            ]
            print(f"*** Make swap with data {_swap_params} ")
            _resp_swap = make_transact(
                contract_address=_router_address,
                abi_file_name="PoolRouter",
                transact_function_name="swapExactTokensForTokens",
                params=_swap_params
            )
            if type(_resp_swap) == Exception:
                raise BotEx(f"Bot Exception: Swap failed with data {_swap_params}")
            return _resp_swap
        except Exception as e:
            print(f"Exception in swap : {e}")
            return None
