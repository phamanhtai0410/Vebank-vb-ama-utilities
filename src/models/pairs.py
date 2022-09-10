from pymodm import fields
from lib.model import BaseMG
from lib.enums.database import DBName


class PairsModel(BaseMG):
    class Meta:
        collection_name = 'pairs'
        connection_alias = DBName.POOL
        final = True
        ignore_unknown_fields = True

    _id = fields.ObjectIdField(primary_key=True)
    factory_address = fields.CharField(blank=True, default='')
    pair_address = fields.CharField(blank=True, default=0)
    token0_address = fields.CharField(blank=True, default='')
    token1_address = fields.CharField(blank=True, default='')
    reserve0 = fields.CharField(blank=True, default='')
    reserve1 = fields.CharField(blank=True, default='')




