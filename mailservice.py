#!/usr/bin/env python
"""An HTTP service that accepts POST requests containing email data, processes, and sends the email"""
import os, re, sys, importlib

from flask import Flask, Markup, jsonify, request
from ConfigParser import SafeConfigParser

app = Flask(__name__)

#################
# configuration #
#################
CONFIG_FILE = 'settings.cfg'
if not os.path.exists(CONFIG_FILE):
    sys.stdout.write('Missing %s config file.\n' % CONFIG_FILE)
    sys.exit(1)

###########
# logging #
###########
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('logs/mailservice.log', 'a', 1 * 1024 * 1024 * 10, 30)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.info('mailservice starting')
    

##################
# error handling #
##################
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle invalid usage errors"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response

#############
# utilities #
#############
def is_valid(request):
    """Returns a 2-tuple, a boolean indicating whether or not the request was valid, 
    and an error message if the request was not valid."""

    email_fields = ('to', 'from')
    name_fields = ('to_name', 'from_name')
    subject_fields = ('subject',)
    body_fields = ('body',)

    required_fields = email_fields + name_fields + subject_fields + body_fields
    missing_fields = []
    empty_fields = []
    for field in required_fields:
        # make sure required fields are there
        if field not in request.form:
            missing_fields.append(field)
            continue
        # make sure required fields are non-empty
        if not request.form[field]:
            empty_fields.append(field)
    if missing_fields:
        app.logger.debug('Required fields missing: ' + ', '.join(missing_fields))
        return (False, 'Required fields missing: ' + ', '.join(missing_fields))
    if empty_fields:
        app.logger.debug('Required fields are empty: ' + ', '.join(empty_fields))
        return (False, 'Required fields are empty: ' + ', '.join(empty_fields))

    # valid email addresses
    email_re = re.compile('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$')
    invalid_emails = []
    for field in email_fields:
        email = request.form[field]
        m = email_re.match(email)
        if not m:
            invalid_emails.append(email)
    if invalid_emails:
        return False, 'Invalid email addresses: ' + ', '.join(invalid_emails)

    return True, ""

def send_email(request):
    """Send the email via the appropriate email service"""

    # convert the body to text-only
    body_text = Markup(request.form['body']).striptags()

    # See what email systems are configured.  Try them one at a time until succeeding,
    # or running out of systems to try.  Each section of the config file is expected to be 
    # setup for a different email system.
    parser = SafeConfigParser()
    parser.read(CONFIG_FILE)
    for section in parser.sections():
        api_key = parser.get(section, 'API_KEY')
        send_url = parser.get(section, 'SEND_URL')
        module = importlib.import_module(section.lower())
        service_class_ = getattr(module, section)
        service = service_class_(api_key, send_url)

        app.logger.info('sending message to %s via %s' % (request.form['to'], section))
        response = service.send_message(to_email = request.form['to'],
                                        to_name = request.form['to_name'],
                                        from_email = request.form['from'],
                                        from_name = request.form['from_name'],
                                        subject = request.form['subject'],
                                        body = body_text,
                                        )
        if response.status_code != 200:
            app.logger.debug('send failed, trying another service')
            continue # try the next service

        app.logger.info('message sent successfully')
        return (response.text, response.status_code)

    return ('failed to send email', 500)

#########
# views #
#########
@app.route('/email', methods=['POST'])
def email():
    """Handle POST requests containing email data"""

    app.logger.debug('received POST request')

    if request.method != 'POST':
        raise InvalidUsage('/email endpoint requires POST method', 400)
    
    valid, msg = is_valid(request)
    if not valid:
        raise InvalidUsage(msg, 400)
    
    return send_email(request)


if __name__ == '__main__':
    app.run(debug=True)
    #app.run()
