# hacker_academy_scripts

Written for python 2.7.

#TODO: Upgrade to python 3.

helper.py contains helper scripts

wui.py grabs all users from hackeracademy.org, puts them in an excel file, which can be directly used in MailChimp for uploading any new users (MailChimp ignores users who are already existing).

website_user_importer_test contains unit test files for wui.py

email_automation contains scripts having to do with email automation.
- Email.py contains basic email-sending functions.
- ha_email.py allows common emails to be sent (invitations, reminders, room booking for events)
- NETtalk_reminder.py is obsolete.

For each script, read the usage descriptions using python's --help to know how to use them.
