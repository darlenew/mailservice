#!/usr/bin/env python
"""Mandrill transactional email system"""

import json
import requests
import sys
from StringIO import StringIO
import unittest

from emailsystem import EmailSystem, EmailSystemError

class Mandrill(EmailSystem):

    def send_message(self, to_email="", to_name="", from_email="", from_name="", subject="", body=""):
        data= {"key": self.api_key,
               "message": {"html": "", 
                           "text": body,
                           "subject": subject,
                           "from_email": from_email,
                           "from_name": from_name,
                           "to": [{"email": to_email,
                                   "name": to_name,
                                   "type": "to"}] 
                           } 
               }

        io = StringIO()
        json.dump(data, io)
        data = io.getvalue()

        response = requests.post(
            self.send_url,
            data=data
            )

        return response
        

class TestMandrill(unittest.TestCase):

    def setUp(self):
        # get the api key and url from config
        import os, string
        from ConfigParser import SafeConfigParser

        CONFIG_FILE = 'settings.cfg'        
        parser = SafeConfigParser()
        parser.read(CONFIG_FILE)
        section = string.capwords(os.path.splitext(os.path.basename(__file__))[0])
        if section in parser.sections():
            api_key = parser.get(section, 'API_KEY')
            send_url = parser.get(section, 'SEND_URL')
        else:
            self.fail('config file misconfigured: %s' % (CONFIG_FILE))

        self.service = globals()[section](api_key, send_url)

    def test_send_message(self):
        response = self.service.send_message(to_email="darlene.py@gmail.com", to_name="DW", from_email="darlene.wong@gmail.com", subject="hello from python requests", body="test from __main__")
        self.assertEqual(response.status_code, 200)

if __name__=="__main__":
    unittest.main()

    
    
