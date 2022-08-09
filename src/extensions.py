# -*- coding: utf-8 -*-
from flask_redis import Redis
from pymodm import connect
from rediscluster import RedisCluster

from .config import DefaultConfig

# Redis cache
redis_cache = Redis()
# Redis user info, will be initialized in app
redis_cluster = RedisCluster(
    startup_nodes=DefaultConfig.REDIS_CLUSTER,
    decode_responses=True,
    skip_full_coverage_check=True
)
# print('Init Redis user info successfully')
