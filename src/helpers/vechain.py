import json
from thor_requests.connect import Connect
from thor_requests.contract import Contract
from thor_requests.wallet import Wallet
from src.config import DefaultConfig
from pydash import get


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


"""
    @functions: Make call to vechain
    @params: 
        + `contract_address`: address of interaction contract
        + `abi_file_name`: ABI json file name that stored in directory "src/abis" 
        + `call_function_name`: interaction function
        + `params`: an array of parameters for this call
    @return: Decoded data on demand.
"""


def make_call(contract_address, abi_file_name, call_function_name, params=[]):
    # Establish connect to contracts
    connector = Connect(DefaultConfig.VECHAIN_RPC)
    # Contract instance
    _contract_instance = Contract.fromFile(f'src/abis/{abi_file_name}.json')
    # Call function
    _res = connector.call(
        DefaultConfig.CALLER,
        _contract_instance,
        call_function_name,
        params,
        contract_address
    )
    if not _res:
        return {}

    return get(_res, 'decoded')


"""
    @function: Make transact to vechain
    @params:
        + `contract_address`: address of interaction contract
        + `abi_file_name`: ABI json file name that stored in directory "src/abis" 
        + `transact_function_name`: interaction function
        + `params`: an array of parameters for this transact
"""


def make_transact(contract_address, abi_file_name, transact_function_name, params=[]):
    # Establish connect to contracts
    connector = Connect(DefaultConfig.VECHAIN_RPC)
    # Wallet
    with open("src/keystore", "r") as _f:
        _keystore = json.load(_f)
    _wallet = Wallet.fromKeyStore(
        ks=_keystore,
        password=DefaultConfig.KEYSTORE_PASSWORD
    )
    # Contract instance
    _contract_instance = Contract.fromFile(f'src/abis/{abi_file_name}.json')
    # Call function
    _res = connector.transact(
        wallet=_wallet,
        contract=_contract_instance,
        func_name=transact_function_name,
        func_params=params,
        to=contract_address
    )
    if not _res:
        return {}

    return get(_res, 'decoded')


"""

"""


def get_health_factor(_user):
    # Establish connect to contracts
    connector = Connect(DefaultConfig.VECHAIN_RPC)

    # Contract iDelegateSeer
    _contract_address = DefaultConfig.CONTRACT_LENDING_POOL
    _contract_instance = Contract.fromFile('src/abis/PoolABI.json')

    # Call update
    _res = connector.call(
        DefaultConfig.CALLER,
        _contract_instance,
        "getUserAccountData",
        [_user],
        _contract_address
    )
    if not _res or get(_res, 'decoded')['healthFactor'] == 2**256 - 1:
        return 0

    return truncate(get(_res, 'decoded')['healthFactor'] / (10 ** 18), 3)


def get_user_account_data(_user_address):
    # Establish connect to contracts
    connector = Connect(DefaultConfig.VECHAIN_RPC)

    # Contract iDelegateSeer
    _contract_address = DefaultConfig.CONTRACT_LENDING_POOL
    _contract_instance = Contract.fromFile('src/abis/PoolABI.json')

    # Call update
    _res = connector.call(
        DefaultConfig.CALLER,
        _contract_instance,
        "getUserAccountData",
        [_user_address],
        _contract_address
    )
    if not _res:
        return {}

    return get(_res, "decoded")


"""
    @function: Get token symbol
    @params: 'token_address' - token address in lowercase
    @return     
"""


def get_token_symbol(token_address):
    # Establish connect to contracts
    connector = Connect(DefaultConfig.VECHAIN_RPC)

    # Contract
    _contract_instance = Contract.fromFile('src/abis/Token.json')

    # Call update
    _res = connector.call(
        DefaultConfig.CALLER,
        _contract_instance,
        "symbol",
        [],
        token_address
    )

    return get(_res, 'decoded')['0']


"""
    @function: POOL : Get pair reserve 
    @params: 'token_address' - token address in lowercase
    @return     
"""


def get_pair_reserves(pair_address):
    # Establish connect to contracts
    connector = Connect(DefaultConfig.VECHAIN_RPC)

    # Contract
    _contract_instance = Contract.fromFile('src/abis/PoolPair.json')

    # Call update
    _res = connector.call(
        DefaultConfig.CALLER,
        _contract_instance,
        "getReserves",
        [],
        pair_address
    )

    return divide_unit(get(_res, "decoded")["_reserve0"]), divide_unit(get(_res, "decoded")["_reserve1"])


def divide_unit(value):
    return float(value / (10 ** 18))



