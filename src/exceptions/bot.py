# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from lib.decorators.http import make_response
from lib.enums.http import StatusInt
from src.enums.http import ErrorCode


class BotEx(Exception):
    def __init__(self, message='bot_error', *args: object) -> None:
        super().__init__(*args)
        self.response = make_response(
            error_code=ErrorCode.BotError,
            msg=message
        ), StatusInt.Bad
    pass
