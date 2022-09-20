from pymodm import fields
from lib.model import BaseMG
from lib.enums.database import DBName


class AmmOrdersModel(BaseMG):
    class Meta:
        collection_name = 'amm_orders'
        connection_alias = DBName.POOL
        final = True
        ignore_unknown_fields = True

    _id = fields.ObjectIdField(primary_key=True)
    env = fields.CharField(blank=True, default="")
    pair_address = fields.CharField(blank=True, default='')
    base_token = fields.CharField(blank=True, default='')
    quote_token = fields.CharField(blank=True, default='')
    price = fields.FloatField(blank=True, default=0)
    amount_in_base = fields.FloatField(blank=True, default=0)
    filled_amount = fields.FloatField(blank=True, default=0)
    side = fields.CharField(blank=True, default='')
    order_type = fields.CharField(blank=True, default='')
    expired_time = fields.IntegerField(blank=True, default=0)
    status = fields.CharField(blank=True, default='')
    tx_id = fields.CharField(blank=True, default='')






