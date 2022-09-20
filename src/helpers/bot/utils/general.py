from .const import *


def toggle_side(side: str):
    if side == SELL:
        return BUY
    else:
        return SELL
