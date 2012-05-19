#! /usr/bin/python

import imaplib
import email
import re
from django.core.management import setup_environ
from fedup import settings
setup_environ(settings)

from tasks.models import Task
from django.conf import settings
from django.contrib.auth.models import User


def create_task(task_title, user):
    """
    Creates the task with the `task_title` and assigns the `user` to
    `assigned_users` if `assigned_users` is empty.
    """
    task = Task()
    task.save_from_re(task_title)

    # If user was not yet assigned use the email user.
    if len(task.assigned_users.all()) == 0:
        task.assigned_users.add(user)

    return task


def get_text_payload(email_mess):
    '''
    Returns the text version of the passed mail.
    '''
    if email_mess.get_content_maintype() == 'text':
        return email_mess.get_payload()
    elif email_mess.get_content_maintype() == 'multipart':
        for part in email_mess.get_payload():
            if part.get_content_type() == 'text/plain':
                return part.get_payload()


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

        # Creating multiple tasks.
        if not email_mess['Subject']:
            content = get_text_payload(email_mess)
            for line in content.splitlines():
                if line.startswith('-'):
                    task_title = line.lstrip('-').strip()
                    task = create_task(task_title, user)
                    task.save()
            print content

        else:
            task = create_task(email_mess['Subject'], user)
            notes = get_text_payload(email_mess)
            task.notes = notes.replace('\n> ', '\n').replace('\n *> ', '\n').replace('\n', '  \n').replace('=20', '').replace('=\r', '\r')
            task.save()

            print "{0} was created!".format(task.title)


if __name__ == '__main__':
    add_tasks()
