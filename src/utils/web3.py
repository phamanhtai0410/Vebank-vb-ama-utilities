from pydash import get


def keystore_to_address(_keystore):
    return get(_keystore, "address")

