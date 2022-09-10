# -*- coding: utf-8 -*-


# File: utils.py
# Created at 03/11/2021
"""
   Description:
        -
        -
"""
import json
import traceback

import requests
import sentry_sdk


def request_inside(url, method, body={}, params={}):
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        _data = json.dumps(body)
        # print(f"url {url}; method {method}; body {body}; params {params}; headers {headers};")
        response = requests.request(method=method,
                                    url=url,
                                    data=_data,
                                    params=params,
                                    headers=headers,
                                    timeout=6)
        # print("request inside : ", response.json())
        if response:
            return response.json()
    except Exception as e:
        sentry_sdk.capture_exception()
        print(e)
        traceback.print_exc()
    return None
