import json
import sys
import getopt
sys.path.append(".")
import src.helpers.bot.utils as utils
from lib.utils import amqp
from lib.logger import LoggerTask
from src.config import DefaultConfig
from pydash import get
from lib.decorators.exception import handle_exception
from bson import ObjectId
from src.models.amm_orders import AmmOrdersModel
from pymodm import connect
from lib.enums.database import DBName
from src.helpers.rebalance_tool import RebalancePair


@handle_exception()
def on_message_rebalance_pair(channel, method, properties, body):
    msg = body.decode("utf8")
    msg = json.loads(msg)
    _data_msg = msg

    # Log received message
    LoggerTask.debug(_data_msg)

    # parse message
    _id = str(get(_data_msg, "_id"))
    _order_info = AmmOrdersModel.find_one(
        with_cache=False,
        filter={
            "_id": ObjectId(_id)
        }
    )
    """
        Handle swap action by RebalancePair class
    """
    _rebalanced = RebalancePair(
        env=get(_order_info, "env"),
        pair_address=get(_order_info, "pair_address"),
        amount=int(get(_order_info, "amount_in_base")),
        side=get(_order_info, "side")
    )
    _rebalanced.cache_pair_reserves()
    _rebalanced.cache_tokens_address()
    _rebalanced.approve()
    _swap_resp = _rebalanced.swap()

    """
        Update status to db records
    """
    AmmOrdersModel.update_one(
        filter={
            "_id": ObjectId(_id)
        },
        obj={
            "order_type": utils.ORDER_CLOSE,
            "status": utils.STATUS_DONE,
            "tx_id": get(_swap_resp, "id")
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
