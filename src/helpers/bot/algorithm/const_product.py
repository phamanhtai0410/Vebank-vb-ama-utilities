import math
import src.helpers.bot.utils as utils


class ConstantProductLadder:
    def __init__(self, up_price, down_price, amount):
        self.up_price = up_price
        self.down_price = down_price
        self.amount = amount


def generate_constant_product_ladders(
        base_token_amount,
        quote_token_amount,
        min_price,
        max_price,
        price_gap,
):
    ladders = []

    product = base_token_amount * quote_token_amount

    center_price = quote_token_amount / base_token_amount

    execute_price_gap = price_gap * center_price
    """
        Ask Orders
    """
    down_price = center_price
    last_base_amount = base_token_amount
    while len(ladders) <= utils.LADDERS_MAX_ALLOWED:
        up_price = down_price + execute_price_gap

        if up_price > max_price:
            break
        f = product / up_price
        new_base_amount = math.sqrt(f)
        ladders.append(
            ConstantProductLadder(
                up_price,
                down_price,
                abs(new_base_amount - last_base_amount)
            )
        )
        print("+ ladder ask : ", up_price, down_price, abs(new_base_amount - last_base_amount))
        down_price = up_price
        last_base_amount = new_base_amount
    """
        Bid Orders
    """
    up_price = center_price
    last_base_amount = base_token_amount
    while len(ladders) <= utils.LADDERS_MAX_ALLOWED:
        down_price = up_price - execute_price_gap
        if down_price < min_price:
            break
        f = product / down_price
        new_base_amount = math.sqrt(f)
        ladders.append(
            ConstantProductLadder(
                up_price,
                down_price,
                abs(new_base_amount - last_base_amount)
            )
        )
        print("+ ladder bid : ", up_price, down_price, abs(new_base_amount - last_base_amount))
        up_price = down_price
        last_base_amount = new_base_amount

    return ladders



