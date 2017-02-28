# -*- coding: utf-8 -*-
"""
    Site specific configuration details for an implementation.
    Used to store server info, authentication keys, base urls, etc
    Update with your relevant information before running CLI scripts OR using the xxxd_library.py modules
"""

__author__ = 'hapresto'

# UCS Director Access Info  -  Update for your install
ucsdserver = "10.72.86.243"
ucsd_key = "EF5A6F2BE93046E0936838BA3BC99D96"

# ICF Director Access Info  -  Update for your Install
icfdserver = "icfd.local.intra"
icfd_key = "XXXXXXXX"

# This information should stay the same for all users
url = "http://%s/app/api/rest?"
getstring = "formatType=json&opName=%s"
parameter_lead = "&opData="
headers = {"X-Cloupia-Request-Key": "EF5A6F2BE93046E0936838BA3BC99D96"}


#catalog_type_list = [ '표준','고급','서비스 컨테이너','Standard', 'Advanced', 'Service Container']
catalog_type_list = [ 'Standard']

catalog_type_mapper = { u'표준':'Standard', u'고급':'Advanced', u'서비스 컨테이너':'Service Container'}