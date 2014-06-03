#!/usr/bin/env python
"""Mailgun transactional email system"""
import requests
import unittest

from emailsystem import EmailSystem, EmailSystemError

class Mailgun(EmailSystem):

    def send_message(self, to_email="", to_name="", from_email="", from_name="", subject="", body=""):
        if not to_email:
            raise EmailSystemError("no recipient specified!")

        if to_email and to_name:
            to_list = ["%s <%s>" % (to_name, to_email)]
        else:
            to_list = ["%s" % (to_email)]

        if from_email and from_name:
            from_string = "%s <%s>" % (from_name, from_email)
        else:
            from_string = from_email
        
        data={"from": from_string,
              "to": to_list,
              "subject": subject,
              "text": body}

        response = requests.post(
            self.send_url,
            auth=("api", self.api_key),
            data=data
            )
        
        return response


class TestMailgun(unittest.TestCase):

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

    def test_missing_to_email(self):
        with self.assertRaises(EmailSystemError):
            self.service.send_message(to_name="DW", from_email="darlene.wong@gmail.com", subject="hello from python requests", body="test from __main__")
            
        
if __name__=="__main__":
    unittest.main()
