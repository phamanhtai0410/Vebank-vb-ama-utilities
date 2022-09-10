# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from lib.decorators import handle_res
from src.schemas.ama_config import BaseThresholdForm, LimitThresholdForm
from src.services.ama_config import AMAConfigService


@handle_res(login=False, req_schema=BaseThresholdForm)
def config_base_threshold(body, *args, **kwargs):
    AMAConfigService.set_base_threshold(
        pair=body.pair,
        value=body.base_threshold
    )
    return {
        "status": "done"
    }


@handle_res(login=False, req_schema=LimitThresholdForm)
def config_limit_threshold(body, *args, **kwargs):
    AMAConfigService.set_limit_threshold(
        pair=body.pair,
        value=body.limit_threshold
    )
    return {
        "status": "done"
    }
