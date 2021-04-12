import re

def email_regex(email):
    return re.match('[^@]+@[^@]+\.[^@]+', email)

def ip_regex(ip):
    return re.match('^(([1-9]?\d|1\d\d|2[0-5][0-5]|2[0-4]\d)\.){3}([1-9]?\d|1\d\d|2[0-5][0-5]|2[0-4]\d)$', ip)

def check_if_upload_is_image(attachment):
    ''' check the type of upload '''
    return re.search("(?i)\.(jpg|png|gif|svg|jpeg)$", attachment)