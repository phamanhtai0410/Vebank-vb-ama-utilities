# -*- coding: utf-8 -*-

""""
    Copyright (C) 2022 ESOL LABS - All Rights Reserved.

    You may use, distribute and modify this code under the
    terms of the XYZ license, which unfortunately won't be
    written for another century.

    You should have received a copy of the XYZ license with
    this file. If not, please write to: , or visit :
"""

# File: consumer_liquidation_checking.py
# Created at May 17th, 2022
# Author: taipa


from src.helpers.ama import gen_non_expirable_key, get_non_expirable_redis_key, save_non_expirable_to_redis
from src.config import DefaultConfig
from src.extensions import redis_cluster


class AMAConfigService(object):
    @staticmethod
    def get_factory_address(env=DefaultConfig.ENV):
        _factory_key, _factory_field = gen_non_expirable_key(
            "factory_address",
            env
        )
        _factory_address = get_non_expirable_redis_key(
            redis_key=_factory_key,
            redis_field=_factory_field
        )
        return _factory_address

    @staticmethod
    def get_router_address(env=DefaultConfig.ENV):
        _router_key, _router_field = gen_non_expirable_key(
            "router_address",
            env
        )
        _router_address = get_non_expirable_redis_key(
            redis_key=_router_key,
            redis_field=_router_field
        )
        return _router_address

    @classmethod
    def set_base_threshold(cls, pair, value, env=DefaultConfig.ENV):
        _base_threshold_key, _base_threshold_field = gen_non_expirable_key(
            f"base_threshold_{pair}",
            env
        )
        _store_base_threshold = save_non_expirable_to_redis(
            key_name=_base_threshold_key,
            field_name=_base_threshold_field,
            value=value
        )
        print(f"Set base threshold {env} for pair {pair} with value {value} : {_store_base_threshold}")
        pass

    @classmethod
    def set_limit_threshold(cls, pair, value, env=DefaultConfig.ENV):
        _limit_threshold_key, _limit_threshold_field = gen_non_expirable_key(
            f"limit_threshold_{pair}",
            env
        )
        _store_limit_threshold = save_non_expirable_to_redis(
            key_name=_limit_threshold_key,
            field_name=_limit_threshold_field,
            value=value
        )
        print(f"Set limit threshold {env} for pair {pair} with value {value} : {_store_limit_threshold}")
        pass


