from src.extensions import redis_cluster

"""
    @function: get key stored of Pool in specific environment.
    @param: `env` - environment name of pool on demand.
    @return: key of redis stored
"""


def gen_non_expirable_key(name: str, env: str) -> (str, str):
    return f"env_{env}", f"POOL_{name}"


"""
    Write non-expirable value to redis
    @params: _key: string
    @return: 0 (Failed) or 1 (Success)
"""


def save_non_expirable_to_redis(key_name: str, field_name: str, value: str):
    return redis_cluster.hsetnx(key=field_name, name=key_name, value=value)


"""
    Function check redis key
    @params: key type HASH
    @return: value of the key
"""


def get_non_expirable_redis_key(redis_key: str, redis_field: str) -> str:
    return redis_cluster.hget(
            name=redis_key,
            key=redis_field
        )


