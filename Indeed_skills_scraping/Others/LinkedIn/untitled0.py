# -*- coding: utf-8 -*-
"""
Created on Wed Mar 01 16:47:16 2017

@author: MINH PHAN
"""

from __future__ import print_function, division

from linkedin import linkedin
from oauthlib import *

CONSUMER_KEY = 'XXXXX'
CONSUMER_SECRET = 'XXXXX'
USER_TOKEN = 'XXXXX'
USER_SECRET = 'XXXXX'
RETURN_URL = 'http://localhost:8000'

authentication = linkedin.LinkedInDeveloperAuthentication(CONSUMER_KEY, CONSUMER_SECRET, 
                                                          USER_TOKEN, USER_SECRET, 
                                                          RETURN_URL, linkedin.PERMISSIONS.enums.values())

application = linkedin.LinkedInApplication(authentication)

g = application.get_profile()
print(g)