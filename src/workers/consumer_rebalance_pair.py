import json
import sys
import getopt
sys.path.append(".")
from lib.utils import amqp
from lib.logger import LoggerTask
from lib.util import dt_utcnow
from src.task import worker
from src.helpers.vechain import get_token_symbol, get_pair_reserves
from src.constants import AppConstants
from src.config import DefaultConfig
from pydash import get
from src.helpers.request import request_inside
from src.helpers.ama import gen_non_expirable_key, get_non_expirable_redis_key
from src.helpers.pool import calculate_amount_to_rebalance, get_amount_out
from src.constants import AppConstants
from src.helpers.vechain import make_transact, make_call
from lib.decorators.exception import handle_exception
from lib.util import dt_utcnow
from src.models.amm_logs import AmmHistoryLogsModel
from pymodm import connect
from lib.enums.database import DBName
from src.services.ama_config import AMAConfigService


@handle_exception()
def on_message_rebalance_pair(channel, method, properties, body):
    msg = body.decode("utf8")
    msg = json.loads(msg)
    _data_msg = msg

    # Log received message
    LoggerTask.debug(_data_msg)

    # parse message
    _pair_address = get(_data_msg, "pair_address").lower()
    _factory_address = get(_data_msg, 'factory_address').lower()
    _router_address = get(_data_msg, 'router_address').lower()
    _reserve0 = get(_data_msg, "reserve0")
    _reserve1 = get(_data_msg, 'reserve1')
    _token0_address = get(_data_msg, 'token0_address')
    _token1_address = get(_data_msg, 'token1_address')

    """
        Checking status of Pool is need to rebalance or not
    """
    # Check tokens 's decimals
    _token0_decimals = make_call(
        contract_address=_token0_address,
        abi_file_name="Token",
        call_function_name="decimals"
    )["0"]
    _token1_decimals = make_call(
        contract_address=_token1_address,
        abi_file_name="Token",
        call_function_name="decimals"
    )["0"]
    # Check price of token in Oracle
    _token0_symbol = get_token_symbol(_token0_address)
    _token1_symbol = get_token_symbol(_token1_address)

    """
        Modify symbol for oracle call
    """
    if _token1_symbol == "WVET":
        _token1_symbol = "VET"

    if _token0_symbol == "WVET":
        _token0_symbol = "VET"

    if _token0_symbol[0] == "v":
        _token0_symbol = _token0_symbol[1:]

    if _token1_symbol[0] == "v":
        _token1_symbol = _token1_symbol[1:]

    """
        Call to Oracle API to get latest price of assets
    """
    print(f"** Rebalance for pair {_token0_symbol}{_token1_symbol}")
    _token0_oracle_price = float(request_inside(
        method="GET",
        url=f"{DefaultConfig.API_URL}/v1/oracle/price/{_token0_symbol}USD/latest",
    )["data"]["price"] or 0)

    if _token0_oracle_price == 0:
        _token0_oracle_price = float(request_inside(
            method="GET",
            url=f"{DefaultConfig.API_URL}/v1/oracle/price/{_token0_symbol}BUSD/latest",
        )["data"]["price"] or 0)

    _token1_oracle_price = float(request_inside(
        method="GET",
        url=f"{DefaultConfig.API_URL}/v1/oracle/price/{_token1_symbol}USD/latest",
    )["data"]["price"] or 0)

    if _token1_oracle_price == 0:
        _token1_oracle_price = float(request_inside(
            method="GET",
            url=f"{DefaultConfig.API_URL}/v1/oracle/price/{_token1_symbol}BUSD/latest",
        )["data"]["price"] or 0)

    """
        Check current reserve token in Pool
    """
    _reserve0_from_chain, _reserve1_from_chain = get_pair_reserves(_pair_address, _token0_decimals, _token1_decimals)

    """
        Get pair AMM configuration
    """
    #       1. Base Threshold
    _base_threshold_key, _base_threshold_field = gen_non_expirable_key(
        f"base_threshold_{_token0_symbol}{_token1_symbol}",
        DefaultConfig.ENV
    )
    _base_threshold = float(get_non_expirable_redis_key(
        redis_key=_base_threshold_key,
        redis_field=_base_threshold_field
    ) or 0)

    #       2. Limit threshold
    _limit_threshold_key, _limit_threshold_field = gen_non_expirable_key(
        f"limit_threshold_{_token0_symbol}{_token1_symbol}",
        DefaultConfig.ENV
    )
    _limit_threshold = float(get_non_expirable_redis_key(
        redis_key=_limit_threshold_key,
        redis_field=_limit_threshold_field
    ) or 0)

    """
        Handler for rebalance    
    """
    if _limit_threshold == 0:
        AMAConfigService.set_limit_threshold(
            pair=f"{_token0_symbol}{_token1_symbol}",
            value=1000
        )

    # Choose threshold
    _range_threshold = _limit_threshold / 10000
    _base_threshold /= 10000
    # Proportion
    _from_chain_ratio = _reserve0_from_chain / _reserve1_from_chain
    _oracle_ratio = _token0_oracle_price / _token1_oracle_price

    _need_to_rebalance = True \
        if abs(_from_chain_ratio - _oracle_ratio) / _oracle_ratio > _range_threshold \
        else False

    if _need_to_rebalance:
        _swap, _amount_in = calculate_amount_to_rebalance(
            _reserve0=_reserve0_from_chain,
            _reserve1=_reserve1_from_chain,
            _fee=AppConstants.SWAP_FEE,
            _oracle_ratio=_oracle_ratio
        )
        print("_amount_in = ", _amount_in)

        if _amount_in:
            _in_decimal = _token0_decimals if _swap else _token1_decimals
            _amount_out = get_amount_out(
                _amount_in=int(_amount_in * 10 ** _in_decimal),
                _reserve_in=int(_reserve0_from_chain * 10 ** _token0_decimals),
                _reserve_out=int(_reserve1_from_chain * 10 ** _token1_decimals),
                _fee=AppConstants.SWAP_FEE
            )

            _amount_out_min = _amount_out * (1 - AppConstants.SWAP_SLIPPAGE / 1000)
            # Approve Router to use token
            make_transact(
                contract_address=_token1_address if _swap else _token0_address,
                abi_file_name="Token",
                transact_function_name="approve",
                params=[
                    _router_address,
                    int(_amount_in * 10 ** _in_decimal)
                ]
            )
            # Swap
            _resp = make_transact(
                contract_address=_router_address,
                abi_file_name="PoolRouter",
                transact_function_name="swapExactTokensForTokens",
                params=[
                    int(_amount_in * 10 ** _in_decimal),
                    int(_amount_out_min),
                    [
                        _token1_address if _swap else _token0_address,
                        _token0_address if _swap else _token1_address
                    ],
                    DefaultConfig.CALLER,
                    int(dt_utcnow().timestamp() + AppConstants.SWAP_DEADLINE)
                ]
            )
            print("_swap_transact_resp: ", _resp, type(_resp))
            AmmHistoryLogsModel.insert(
                {
                    "env": DefaultConfig.ENV,
                    "swap_info": {
                        "amount_in": str(_amount_in * 10 ** _in_decimal),
                        "amount_out_min": str(_amount_out_min),
                        "path": [
                            {
                                "address": _token1_address if _swap else _token0_address,
                                "symbol": _token1_symbol if _swap else _token0_symbol
                            },
                            {
                                "address": _token0_address if _swap else _token1_address,
                                "symbol": _token0_symbol if _swap else _token1_symbol
                            }

                        ],
                        "deadline": int(dt_utcnow().timestamp() + AppConstants.SWAP_DEADLINE)
                    },
                    "tx_id": _resp["id"] if isinstance(_resp, dict) else None,
                    "tx_info": str(_resp),
                    "status": "Done" if isinstance(_resp, dict) else "Reverted"
                }
            )

    """
        ACK Rabbit Message
    """
    channel.basic_ack(delivery_tag=method.delivery_tag)


def handle_msg(_cfg):
    cfg_rabbit = {
        "hostname": DefaultConfig.RABBIT_HOST, "port": DefaultConfig.RABBIT_PORT,
        "username": DefaultConfig.RABBIT_USER, "password": DefaultConfig.RABBIT_PASSWORD,
        "vhost": DefaultConfig.RABBIT_VHOST, "exchange_type": "topic"
    }
    cfg_rabbit.update(_cfg)
    event_name = cfg_rabbit["queue"].split("-")[-1]
    print("cfg_rabbit: ", cfg_rabbit)
    mq = amqp.AmqpConnection(**cfg_rabbit)
    mq.connect()
    mq.setup_queues(durable=True)

    # Connect mongoDB
    connect(DefaultConfig.DB_APP, connect=False, alias=DBName.POOL)

    if event_name == "amm_utils_rebalance":
        mq.consume(on_message_rebalance_pair)
    else:
        print("Event not found")
        sys.exit(2)


if __name__ == "__main__":
    _cfg = {}
    _exchange = ""
    _routing_key = ""
    _queue = ""
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "k:e:q:", ["routing_key=", "exchange=", "queue="])
    except getopt.GetoptError:
        print("python3 workers/consumer_rebalance_pair.py -e <exchange> -k <routing_key> -q <queue>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("python3 workers/consumer_rebalance_pair.py -e <exchange> -k <routing_key> -q <queue>")
            sys.exit()
        elif opt in ("-e", "--exchange"):
            _exchange = arg
        elif opt in ("-k", "--routing_key"):
            _routing_key = arg
            print("_routing_key: ", _routing_key)
        elif opt in ("-q", "--queue"):
            _queue = arg

    _cfg["exchange"] = _exchange
    _cfg["routing_key"] = _routing_key
    _cfg["queue"] = _queue
    handle_msg(_cfg)

