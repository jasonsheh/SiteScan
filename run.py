#!/usr/bin/python
# __author__ = 'jasonsheh'
# -*- coding:utf-8 -*-

import sys
from web.web import app

try:
    app.run()
except KeyboardInterrupt:
    sys.exit()
