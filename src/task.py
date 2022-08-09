# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from pymodm import connect
from lib.enums.database import DBName


from lib.worker import create_worker_pika
from src.config import DefaultConfig

connect(DefaultConfig.DB_APP, connect=False)
worker = create_worker_pika(DefaultConfig)
