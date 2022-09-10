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
     Creation
"""


class Form(Schema):
    class Meta:
        unknown = INCLUDE
        ordered = True
    
    name = fields.Str(required=True)
    image_uri = fields.Str(required=True)
    supply = fields.Int(required=True)
    price = fields.Float(allow_none=True)
    type = fields.Str(required=True)
    percent = fields.Float(allow_none=True)
    description = fields.Str(allow_none=True)
