import os

#EMAIL_HOST = 'smtp.sendgrid.net'
#EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME', '')
#EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD', '')
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'thaictu@gmail.com'
EMAIL_HOST_PASSWORD = 'vbdtvtkgghsalkxl'
DEFAULT_FROM_EMAIL = 'default from email'