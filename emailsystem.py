#!/usr/bin/env python
"""Common email system code"""
import os
import unittest
from ConfigParser import SafeConfigParser, NoSectionError

class EmailSystemError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class EmailSystem:
    def __init__(self, api_key='', send_url=''):
        """Get the email system's API key and sending URL from the config file"""
        self.api_key = api_key
        self.send_url = send_url

    def send_message(self, to_email="", to_name="", from_email="", from_name="", subject="", body=""):
        raise NotImplementedError

