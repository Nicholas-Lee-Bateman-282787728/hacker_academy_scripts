# This script is intended to be the email-sending system for HA.
# All emails and email templates should able to be be added and maintained
# through this script, and all sending operations should be as well.

# Usage: For now, hard-code the correct input email template and a list of
# speakers in the correct format. A speaker is only accepted as a valid
# recipient if the type is defined.

# builtin imports
import os
import sys
import re
from string import Template
import argparse

# Other libraries
from getpass import getpass

# Custom modules
import Email
# Puts .. in python path.
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import helper

# Types of email reminders.
    # invite: invite people to join an event at HA.
    # pizza: remind EngSoc about pizza order from HA.
    # reminder: remind speaker to attend NETtalk.
    # book: make room booking.
EMAIL_TYPES = ['invite', 'pizza', 'remind', 'book']

HA_INFO_EMAIL = "info@hackeracademy.org"
HA_INFO_EMAIL_SENDER = "info@webdev.skule.ca"
EXEC_EMAILS = ["mailwen.li@mail.utoronto.ca", "alan.daniels@mail.utoronto.ca"]
DEFAULT_TEST_EMAIL = "tony.wenbo.li@gmail.com"

# Root path for email files.
EMAIL_FILES_PATH = "email_files"

# For sending invitation emails.
INVITEE_LIST = os.path.join(
    EMAIL_FILES_PATH, "invitation_test.csv")

# name of the dict which stores information of NETtalks and events so that
# automatic emails can get information from it by loading this dictionary from
# a specified info file.
INFO_DICT_NAME = "info"

RHONDA_EMAIL = "rhonda@g.skule.ca"

# INPUT: email body with variable names to be replaced, list of identifiers for
# the variable names, and a list of data.
# The data must be the same length as the identifier list, the dict keys must
# match the identifier_list, and the values of the dict must strings of length
# 1.
# OUTPUT: list of data replacing the identifiers.
# Function to replace variable names, or identifiers in a
def substitute_email(email_body, identifier_list, data_dict):
    # Input validity check:
    keys = data_dict.keys()
    if len(identifier_list) != len(keys):
        raise Exception("there must be as much data as identifiers to replace.")
    for id in identifier_list:
        v = data_dict.get(id)
        if not v:
            raise Exception("The data for " + id + " does not exist.")
        if not type(v) is str:
            raise Exception("The value type for " + id + " is not of type str.")
    # input validity check passed.

    for id in identifier_list:
        email_body = email_body.replace('[' + id + ']', data_dict[id])

    if re.search('\[', email_body) or re.search('\]', email_body):
        print "[ or ] detected in email body after identifier replacement."

    return email_body

def search_last_name(string):
    #print string # debug
    # TO IMPROVE: Of course this doesn't catch corner cases.
    search = re.search("[a-z,A-Z, ,\-,\.]+ ([a-z,A-Z,\-,']+)", string)
    if search:
        return search.group(1) # Return the matched string.

# INPUT: raw contact data from csv file from online google doc.
# OUTPUT: recipient data in a dict, with the name as the key and the address
# and the email as the value in a list.
# format: name: [address, email]
def get_recipient_data(contact_data):
    recipient_data = dict()

    name_col = helper.get_array_col(contact_data, 0)
    type_col = helper.get_array_col(contact_data, 1)
    email_col = helper.get_array_col(contact_data, 3)
    for i in xrange(0, max(len(name_col), len(email_col))):
        address = ''
        contact_type = type_col[i].strip().upper()
        if contact_type == 'P':
            last_name = search_last_name(name_col[i])
            address = "Professor " + last_name
        elif contact_type == 'G':
            address = name_col[i]
        else:
            continue
            # raise Exception("Type of contact %s not currently handled." % contact_type)
        #print email_col[i]
        email = re.search("([\w\.]+@[\w\.]+)", email_col[i]).group(1)
        recipient_data[name_col[i]] = [address, email]

    return recipient_data

def send_NETtalk_invitation_emails(template_file, recipient_file):
    email_info = open(template_file, 'r').read()
    #print email_info
    email_title = re.search('[Tt][Ii][Tt][Ll][Ee]: *(.*)', email_info).group(1)
    email_template = re.search('[Ee][Mm][Aa][Ii][Ll]:\s*(.*)', email_info, 16).group(1)

    sender_email = raw_input("sender email: ")
    pwd = getpass()

    contact_data = helper.read_csv(recipient_file)

    recipient_data = get_recipient_data(contact_data)

    if not recipient_data:
        raise Exception("Recipient data is empty after reading and parsing!")

    skip = False
    failed_list = list()
    for name, info in recipient_data.iteritems():
        email_body = substitute_email(email_template, ['professor_name'], {'professor_name': info[0]})
        email_address = info[1]
        #email_address = "mailwen.li@mail.utoronto.ca" #debug
        cc_address = [HA_INFO_EMAIL]
        #   cc_address = "" #debug
        bcc_address = ""
        if not skip:
            print "\nRecipient email address: ", email_address
            print "Recipient email title: ", email_title
            print "Recipient email body: \n" + email_body
            while True:
                prompt = raw_input('Press ENTER for the next recipient, or "skip" to skip all future prompt: ')
                if prompt == '':
                    break
                elif prompt == "skip":
                    skip = True
                    break

        ret = Email.send_email(sender_email, pwd, email_address, email_title,
        email_body, cc_address, bcc_address, not args.send)

        if ret != 0:
            failed_list.append(email_address)
        #exit() # debug

    print "%d emails successfully sent, %d failures" % (len(recipient_data) - len(failed_list), len(failed_list))

    failed_file = open("failed_recipients.txt", 'w')
    print "list of failures:"
    for failed_recipient in failed_list:
        print failed_recipient
        failed_file.write(failed_recipient)

    failed_file.close()

def send_pizza_notification_email(template_file):
    # TODO: make date validity checking more robust.
    while True:
        month = int(raw_input("month of event (1-12): "))
        if month >= 1 and month <= 12:
            break
    while True:
        day = int(raw_input("day of event (1-31): "))
        if day >= 1 and day <= 31:
            break

    event_date = "%s %s" % (helper.month[month], day)

    default_order = {
        "cheese"    : 1,
        "pepperoni" : 1,
        "pineapple" : 1,
        "ham"       : 1,
        "green olives"  : 1
    }

    toppings = default_order.keys()
    order_printout = str(default_order[toppings[0]]) + " " + toppings[0]
    for i in xrange(1, len(toppings)):
        order_printout += "\n" + str(default_order[toppings[i]]) + " " + toppings[i]

    default_info = {
        "person_name"   : "Wen Bo Li",
        "event_date"    : event_date,
        "event_time"    : "8-9PM",
        "pizza_order_table" : order_printout,
        "phone_number"  : "647-786-9812"
    }

    email_body = open(template_file, 'r').read()
    for tag_name, info in default_info.iteritems():
        tag = "[%s]" % tag_name
        email_body = email_body.replace(tag, default_info[tag_name])

    sender_email = HA_INFO_EMAIL_SENDER
    pwd = getpass()
    email_address = "vpstudentlife@g.skule.ca"
    cc_address = EXEC_EMAILS
    email_title = "Pizza Nova Order: Hacker Academy %s" % event_date

    ret = Email.send_email(sender_email, pwd, email_address, email_title, email_body,
    cc=cc_address, test=not args.send)

def send_email(args, recipient_email, subject, body, cc="", bcc=""):
    pwd = getpass()
    if args.send:
        raw_input("Watch out! Email about to be sent!")
        Email.send_email(args.sender, pwd, recipient_email, subject, body, cc,
        bcc, test=False)
    else:
        Email.send_email(args.sender, pwd, recipient_email, subject, body, test=True)

def send_talk_reminder(args):
    DEFAULT_TEMPLATE_FILE = "NETtalk_reminder_template.txt"
    if args.template_file:
        body_template = Template(open(args.template_file).read())
    else:
        body_template = Template(open(DEFAULT_TEMPLATE_FILE).read())

    for info_file in args.info_files:
        nothing_prepared = ("We can conveniently provide a projector, but let us "
        "know if you happen to need anything else, and we'll see what we can do.")

        projector_prepared = ("We have already prepared a projector, but let us "
        "know if you happen to need anything else, and we'll see what we can do.")

        subject_template = Template("Hacker Academy NETtalk Reminder $date $time "
        "$location_short")

        exec("from " + os.path.splitext(info_file)[0] + " import %s" %
             INFO_DICT_NAME)
        if info["projector"]:
            info["materials_msg"] = projector_prepared
        else:
            info["materials_msg"] = nothing_prepared

        body = body_template.substitute(info)
        subject = subject_template.substitute(info)

        send_email(
            args, info["email"], subject, body, cc=[HA_INFO_EMAIL] + EXEC_EMAILS)

def send_room_bookings(args):
    subject = "Hacker Academy Room Booking"
    DEFAULT_TEMPLATE_FILE = "room_booking_template.txt"
    if args.template_file:
        body_template = Template(open(args.template_file).read())
    else:
        body_template = Template(open(DEFAULT_TEMPLATE_FILE).read())
    summary_template = Template("$date - $title")
    details_template = Template("$time $date - $location_short $projector_msg")
    summaries = list()
    details = list()

    # Gather the talks' info strings from the info files.
    for info_file in args.info_files:
        exec("from " + os.path.splitext(info_file)[0] + " import %s" %
             INFO_DICT_NAME)

        projector_requested = "Projector Requested"

        info["projector_msg"] = (projector_requested if info["projector"] else
                                 "")
        summaries.append(summary_template.substitute(info))
        details.append(details_template.substitute(info))

    # Substitute each of the talks' info into the email body.
    summary_combined = "\n".join(summaries)
    info["summaries"] = summary_combined
    details_combined = "\n".join(details)
    info["details"] = details_combined
    body = body_template.substitute(info)

    send_email(args, RHONDA_EMAIL, subject, body, cc=EXEC_EMAILS)

def main(args):
    # TODO: Store a list of email template paths from which to retrieve the email templates/emails,
    # and set up a system to add, maintain, and delete emails, just like cqe.
    # data_file = "HA_email_list.txt"

    args.sender = args.sender if args.sender else HA_INFO_EMAIL_SENDER
    args.tester = args.tester if args.tester else DEFAULT_TEST_EMAIL

    if args.type == "invite":
        template_file = os.path.join(
            EMAIL_FILES_PATH, "NETtalk_invitation_template_academia.txt")
        template_file = args.template_file if args.template_file else template_file

        send_NETtalk_invitation_emails(template_file, INVITEE_LIST)
    elif args.type == "pizza":
        template_file = os.path.join(
            EMAIL_FILES_PATH, "engsoc_pizza_notification_template.txt")
        template_file = args.template_file if args.template_file else template_file

        send_pizza_notification_email(template_file)
    elif args.type == "remind":
        send_talk_reminder(args)
    elif args.type == "book":
        send_room_bookings(args)

if __name__ == "__main__":
    print (
    """
Usage:
python ha_email.py invite
python ha_email.py remind <info_file.py> (give it a try with arkady.py)
python ha_email.py book <info_file.py> (give it a try with arkady.py)
there is no reason to use pizza because NETtalks are not held when
they're in office.
    """)
    parser = argparse.ArgumentParser(description=
    """Automatically send emails for HA for a variety of purposes. By default,
    all emails are sent as test emails.""")
    parser.add_argument('type', choices=EMAIL_TYPES, help="type of email.")
    parser.add_argument("info_files", nargs="*", help="information to fill the template"
    "file.")
    parser.add_argument('--template_file', help="email template to be used (if"
    "required).")
    parser.add_argument("--sender", help="sender email if different from "
    "{}.".format(HA_INFO_EMAIL_SENDER))
    parser.add_argument("-t", "--tester", help="test email to send to"
    "(default: {})".format(DEFAULT_TEST_EMAIL))
    parser.add_argument("--cc", nargs="*", help="cc")
    parser.add_argument("--bcc", nargs="*", help="bcc")
    parser.add_argument("--send", action="store_true", help="Actually send "
    "the email instead of testing.")
    args = parser.parse_args()

    main(args)
