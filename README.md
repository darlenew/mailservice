mailservice
===========

An HTTP email sending service that allows you to configure multiple transactional email services to use, in case one of them goes down.  This service accepts POST requests containing JSON data representing a single email message.  The email message is delivered, text-only, via one of the configured transactional email services.  If the message is not successfully sent, it is retried with another configured transactional email service.

setup
=====

Install the requests module

```
# Download the module
$ curl -OL https://github.com/kennethreitz/requests/tarball/master

# Extract the contents of the tarball
$ tar xvf master

# Install requests
$ cd kennethreitz-requests-7022830/
$ python setup.py install
```

Install Flask

```
# Download the module
$ curl -OL http://pypi.python.org/packages/source/F/Flask/Flask-0.10.1.tar.gz

# Extract the contents
$ tar xvzf Flask-0.10.1.tar.gz

# Install
$ cd Flask-0.10.1
$ python setup.py install
```

Configure

```
# Copy the sample-settings.cfg to settings.cfg
$ cp sample-settings.cfg settings.cfg
```

Edit the settings.cfg file.  Supply your API keys and sandbox URL in the appropriate sections.


running
=======

Run the Flask server:
```
$ ./mailservice.py
```

By default, the server is now running at http://127.0.0.1:5000

You can now send POST requests containing JSON data to the server at: http://127.0.0.1:5000/email

Your requests should be formatted as follows:

    {
        "to": "fake@example.com",
        "to_name”: “Ms. Fake",
        "from": "noreply@uber.com",
        "from_name": "Uber",
        "subject": "A Message from Uber",
        "body": "<h1>Your Bill</h1><p>$10</p>"
    }

Each of the fields must be in the payload, and none of the fields can
be empty.  The email addresses must be valid.  You can include HTML
tags in the body section, but the HTML will be stripped off by the
mail service, resulting in a text-only message.


testing
=======

Discover and run the unit tests.

    $ python -m unittest discover -v -p '*.py'

NOTE: Some of the tests in test_mailservice.py expect that the Flask
app is already up and running.  If it is not running, it is expected
that 2 of the tests will fail.

NOTE2: The test_mailservice.py needs some email addresses to test the
actual service.  These need to be set in your environent variables:

    $ export TESTMAILSERVICE_TO=<your email address>
    $ export TESTMAILSERVICE_TO_NAME=<your name>
    $ export TESTMAILSERVICE_FROM=<your other email address>
    $ export TESTMAILSERVICE_FROM_NAME=<your name>


how to add a new email service
==============================

Create a new Python module for your email service.  It is
anticipated that the new module will have an all-lowercase name.

In the new module, create a subclass of EmailSystem for your new
email service.  The subclass is expected to match the module name, but
start with a capital letter.  Implement the send_message() method as
appropriate for the new service.

Create a section in the settings.cfg configuration file for the new
email service.  The name of the section must exactly match the name of
the corresponding subclass.

