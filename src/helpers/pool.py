import cmath


def get_amount_in(_amount_out, _fee, _reserve_in, _reserve_out):
    return (_reserve_in * _amount_out) / ((_reserve_out - _amount_out) * (1 - _fee / 1000)) + 1


def get_amount_out(_amount_in, _fee, _reserve_in, _reserve_out):
    return ((_reserve_out * _amount_in) * (1 - _fee / 1000)) / (_reserve_in + _amount_in * (1 - _fee / 1000))


def calculate_amount_to_rebalance(_reserve0: float, _reserve1: float, _fee: int, _oracle_ratio: float) -> (int, float):
    print(f"calculate_amount_to_rebalance for reserves : {_reserve0} {_reserve1}")
    _swap_token = 1 if (_reserve0 / _reserve1) > _oracle_ratio else 0
    if (_reserve0 / _reserve1) > _oracle_ratio:
        """
            @TODO: Calculate _amount_in should be swap:
             a*(_amount)**2 + b * _amount +c =0
        """
        c = (_oracle_ratio * _reserve0 * _reserve1 - _reserve0 ** 2) * (1 - _fee / 1000)
        b = (_oracle_ratio * (_reserve0 - _reserve1) + (_reserve0 + _reserve1)) * (1 - _fee / 1000)
        a = -_oracle_ratio * (1 - _fee / 1000)

        # calculate the discriminant
        d = (b ** 2) - (4 * a * c)

        # find two solutions
        sol1 = (-b - cmath.sqrt(d)) / (2 * a)
        sol2 = (-b + cmath.sqrt(d)) / (2 * a)
    else:
        """
            @TODO: Calculate _amount_in should be swap:
             a*(_amount)**2 + b * _amount +c =0
        """
        c = _reserve0 * _reserve1 * (1 - _fee / 1000) - _oracle_ratio * (_reserve1 ** 2) * (1 - _fee / 1000)
        b = ((1 - _oracle_ratio) * _reserve1 - _reserve0) * (1 - _fee / 1000) - _reserve0
        a = - (1 - _fee / 1000)

        # calculate the discriminant
        d = (b ** 2) - (4 * a * c)

        # find two solutions
        sol1 = (-b - cmath.sqrt(d)) / (2 * a)
        sol2 = (-b + cmath.sqrt(d)) / (2 * a)

    print('The solution are {0} and {1}'.format(sol1, sol2))
    print('sol1.image : ', sol1.imag == 0)
    print('sol2.image : ', sol2.imag == 0)
    _valid = []

    if get_amount_out(
        _amount_in=sol2.real,
        _fee=_fee,
        _reserve_in=_reserve1 if _swap_token else _reserve0,
        _reserve_out=_reserve0 if _swap_token else _reserve1
    ) > 0 and sol2.real > 0:
        _valid.append(sol2.real)

    if get_amount_out(
        _amount_in=sol1.real,
        _fee=_fee,
        _reserve_in=_reserve1 if _swap_token else _reserve0,
        _reserve_out=_reserve0 if _swap_token else _reserve1
    ) > 0 and sol1.real > 0:
        _valid.append(sol1.real)

    if len(_valid) == 0:
        return _swap_token, None
    else:
        return _swap_token, min(_valid)



