import re

def email_regex(email):
    return re.match('[^@]+@[^@]+\.[^@]+', email)

def check_if_upload_is_image(attachment):
    ''' check the type of upload '''
    return re.search("(?i)\.(jpg|png|gif|svg|jpeg)$", attachment)