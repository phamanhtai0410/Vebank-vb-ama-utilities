# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from lib.decorators import handle_res


@handle_res(login=False)
def debug():
    return {}

@handle_res(login=False)
def health_check(*args, **kwargs):
    return {}
