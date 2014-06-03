mailservice
===========

An HTTP service that accepts POST requests containing JSON data representing a single email message.  The email message is delivered, text-only, via one of the configured transactional email services.  If the message is not successfully sent, it is retried with another transactional email service.
