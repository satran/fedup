#! /usr/bin/python

import imaplib
import email
import re
from django.core.management import setup_environ
from fedup import settings
setup_environ(settings)

#from fedup.email_settings import IMAP_HOST, IMAP_USE_SSL, IMAP_PORT, IMAP_USER_NAME, IMAP_USER_PASS
from tasks.models import Task
from django.conf import settings
from django.contrib.auth.models import User

def add_tasks():
    if settings.IMAP_USE_SSL:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
    else:
        mail = imaplib.IMAP4(host=settings.IMAP_HOST, port=settings.IMAP_PORT)

    mail.login(settings.IMAP_USER_NAME, settings.IMAP_USER_PASS)

    mail.select()
    _, ids = mail.search(None, '(UNSEEN)')

    for id in ids[0].split():
        typ, data = mail.fetch(id, '(RFC822)')
        email_mess = email.message_from_string(data[0][1])
        from_user = re.search('<(?P<email>.+)>', email_mess['From'])

        try:
            user = User.objects.get(email=from_user.groupdict()['email'])
        # It happens when the regex emails gets the value None
        # which is to say there was no match.
        except AttributeError:
            continue
        # If the email is not registered with any user just ignore.
        except User.DoesNotExist:
            continue

        task = Task()
        task.save_from_re(email_mess['Subject'])
        task.assigned_users.add(user)

        if email_mess.get_content_maintype() == 'text':
            task.notes = email_mess.get_payload()
        elif email_mess.get_content_maintype() == 'multipart': 
            for part in email_mess.get_payload():
                if part.get_content_type() == 'text/plain':
                    task.notes = part.get_payload().replace('\n> ', '\n').replace('\n *> ', '\n').replace('\n', '  \n').replace('=20', '').replace('=\r', '\r')
        task.save()
        
        print "{0} was created!".format(task.title)

if __name__ == '__main__':
    add_tasks()
