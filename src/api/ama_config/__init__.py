# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from flask import Blueprint

from .controller import config_base_threshold, config_limit_threshold

rest_ama_config = Blueprint('rest_ama_config', __name__, url_prefix='')

rest_ama_config.add_url_rule('/config/base_threshold', methods=['POST'], view_func=config_base_threshold)

rest_ama_config.add_url_rule('/config/limit_threshold', methods=['POST'], view_func=config_limit_threshold)
