class StdOrder:
    def __init__(
            self,
            _id,
            status,
            amount,
            price,
            available_amount,
            filled_amount,
            side
    ):
        self._id = _id
        self.status = status
        self.amount = amount
        self.price = price
        self.available_amount = available_amount
        self.filled_amount = filled_amount
        self.side = side



