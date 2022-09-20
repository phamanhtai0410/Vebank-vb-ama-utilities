import getopt
import sys
import shutil
import time
import traceback
import sentry_sdk
sys.path.append(".")
from lib.utils import amqp
from src.config import DefaultConfig
from src.services.ama_config import AMAConfigService
from src.models.pairs import PairsModel
from pydash import get
from pymodm import connect
from lib.enums.database import DBName
from src.helpers.bot.execute_bot import BotExecutedCommands


"""
    JOB DESCRIPTION: Scheduled Jobs for passive rebalance
"""


def main(_cfg):
    cfg_rabbit = {
        "hostname": DefaultConfig.RABBIT_HOST, "port": DefaultConfig.RABBIT_PORT,
        "username": DefaultConfig.RABBIT_USER, "password": DefaultConfig.RABBIT_PASSWORD,
        "vhost": DefaultConfig.RABBIT_VHOST, "exchange_type": "topic"
    }

    # Connect RabbitMQ
    cfg_rabbit.update(_cfg)
    mq = amqp.AmqpConnection(**cfg_rabbit)
    mq.connect()
    # Connect MongoDB
    connect(DefaultConfig.DB_APP, connect=False, alias=DBName.POOL)

    while True:
        """
            Concepts:
            
        """
        try:
            _env = DefaultConfig.ENV
            _factory_address = AMAConfigService.get_factory_address(_env)
            _router_address = AMAConfigService.get_router_address(_env)
            _list = PairsModel.get_list(
                filter={
                    "factory_address": _factory_address
                }
            )

            for _pair in _list:
                terminal_size = shutil.get_terminal_size(fallback=(120, 50))
                print("=" * terminal_size.columns)
                print(f'Gen new BOT instant for pair {get(_pair, "pair_address")}')
                _gen_new_bot = BotExecutedCommands(
                    base_token_address=get(_pair, "token0_address"),
                    quote_token_address=get(_pair, "token1_address"),
                    pair_address=get(_pair, "pair_address"),
                    mq=mq
                )
                _gen_new_bot.main_bot_running()

        except Exception as e:
            print(e)
            sentry_sdk.capture_exception()
            traceback.print_exc()

        time.sleep(DefaultConfig.SCHEDULED_INTERVAL)


if __name__ == "__main__":
    _cfg = {}
    _exchange = ""
    _routing_key = ""
    _queue = ""
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "k:e:q:", ["routing_key=", "exchange=", "queue="])
    except getopt.GetoptError:
        print("python3 src/schedule_jobs/rebalance_strategy.py -e <exchange> -k <routing_key> -q <queue>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("python3 src/schedule_jobs/rebalance_strategy.py -e <exchange> -k <routing_key> -q <queue>")
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
    main(_cfg)
