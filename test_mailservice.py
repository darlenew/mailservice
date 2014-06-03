#!/usr/bin/env python
"""Tests for the mailservice module.  Assumes that the service is already up and running"""
import os
import unittest
import requests
import json

from mailservice import is_valid

HTTP_MAIL_SERVICE_URL = "http://127.0.0.1:5000/email"

# reusable, customizable fields for testing
TO = os.environ['TESTMAILSERVICE_TO']
TO_NAME = os.environ['TESTMAILSERVICE_TO_NAME']
FROM = os.environ['TESTMAILSERVICE_FROM']
FROM_NAME = os.environ['TESTMAILSERVICE_FROM_NAME']

class TestEmailService(unittest.TestCase):
    """Test the email service.  Assumes that the email service is up and running"""

    def setUp(self):
        self.payload = { "to": TO,
                         "to_name": TO_NAME,
                         "from": FROM,
                         "from_name": FROM_NAME, 
                         "subject": "A Message from Uber", 
                         "body": "<h1>Client Message</h1><p>$10</p>" }

    def test_send_email(self):
        # test the general case
        r = requests.post(HTTP_MAIL_SERVICE_URL,
                          data=self.payload)
        self.assertEqual(r.status_code, 200)
        
    def test_missing_to(self):
        # make sure you get an error message if a field is missing
        self.payload.pop("to")
        r = requests.post(HTTP_MAIL_SERVICE_URL,
                          data=self.payload)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(json.loads(r.text), {"message": "Required fields missing: to"}) 


class TestValidRequest(unittest.TestCase):
    """Test the server-side validation of incoming requests"""
    
    def setUp(self):
        class FakeRequest:
            form = {}

        self.r = FakeRequest()
        self.r.form['to'] = TO
        self.r.form['to_name'] = TO_NAME
        self.r.form['from'] = FROM
        self.r.form['from_name'] = FROM_NAME
        self.r.form['subject'] = 'Test Valid Request'
        self.r.form['body'] = 'Just seeing\n\n\nYeah'

    def test_valid(self):
        self.assertEqual(is_valid(self.r), (True, ''))

    def test_missing_from(self):
        self.r.form.pop('from')
        self.r.form.pop('from_name')
        self.assertEqual(is_valid(self.r), (False, 'Required fields missing: from, from_name'))

    def test_bad_to_email(self):
        self.r.form['to'] = 'invalid_email.com'
        self.assertEqual(is_valid(self.r), (False, 'Invalid email addresses: invalid_email.com'))

    def test_empty_field(self):
        self.r.form['body'] = ''
        self.assertEqual(is_valid(self.r), (False, 'Required fields are empty: body'))
    
if __name__=='__main__':
    unittest.main()
