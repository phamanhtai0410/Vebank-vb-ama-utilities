from pymodm import fields
from lib.model import BaseMG
from lib.enums.database import DBName


class AmmHistoryLogsModel(BaseMG):
    class Meta:
        collection_name = 'amm_history_logs'
        connection_alias = DBName.POOL
        final = True
        ignore_unknown_fields = True

    _id = fields.ObjectIdField(primary_key=True)
    env = fields.CharField(blank=True, default="")
    swap_info = fields.DictField(blank=True, default={})
    tx_id = fields.CharField(blank=True, default='')
    status = fields.CharField(blank=True, default='')





