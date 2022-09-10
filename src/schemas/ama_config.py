# -*- coding: utf-8 -*-

""""
    Copyright (C) 2022 ESOL LABS - All Rights Reserved.

    You may use, distribute and modify this code under the
    terms of the XYZ license, which unfortunately won't be
    written for another century.

    You should have received a copy of the XYZ license with
    this file. If not, please write to: , or visit :
"""

# File: __init__.py
# Created at May 17th, 2022
# Author: taipa

"""
   Description:
        -
        -
"""

from marshmallow import EXCLUDE, INCLUDE, fields, Schema, validate
from lib.schema.req import ResDatetimeField, ObjectIdField


"""
     Base Threshold
"""


class BaseThresholdForm(Schema):
    class Meta:
        unknown = INCLUDE
        ordered = True

    pair = fields.Str(required=True)
    base_threshold = fields.Float(required=True)


"""
     Limit Threshold
"""


class LimitThresholdForm(Schema):
    class Meta:
        unknown = INCLUDE
        ordered = True

    pair = fields.Str(required=True)
    limit_threshold = fields.Float(required=True)


