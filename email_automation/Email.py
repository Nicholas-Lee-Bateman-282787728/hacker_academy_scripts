# Usage: use send_email(), but add the domain-to-host mapping in the dict before doing so.

# INPUT: user and recipients are email addresses, the rest are self-explanatory.
# OUTPUT: specific return codes have different meanings:
# 0: success
# 1: smtp sending failed.
# 2: domain-to-host mapping not defined.
import sys

TEST_EMAIL = "tony.wenbo.li@gmail.com"

def send_email(user, pwd, recipients, subject, body, cc="", bcc="", test=False):
    """Sends email to recipients, cc, and bcc.

    user: email of sender as string.
    pwd: password of sender email as string.
    recipients: single email as string, or list of strings.
    cc, bcc: same as above
    test: sends a email, but only to the test email hardcoded in this function.
    """
    host_map = {
        "gmail.com"         : "smtp.gmail.com",
        "webdev.skule.ca"   : "smtp.gmail.com",
        "hotmail.com"       : "smtp.live.com",
        "mail.utoronto.ca"  : "outlook.office365.com"
    }

    if test:
        recipients = TEST_EMAIL
        cc = ""
        bcc = ""

    user_name, at, domain_name = user.rpartition('@')

    host = host_map.get(domain_name)

    if host:
        return send_email_aux(user, host, pwd, recipients, cc, bcc, subject, body)
    else:
        print "host not determined for domain name. Add the mapping in Email.py"
        return 2

def send_email_aux(user, host, pwd, recipients, cc, bcc, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipients if type(recipients) is list else [recipients]
    CC = cc if type(cc) is list else [cc]
    BCC = bcc if type(bcc) is list else [bcc]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nCC: %s\nBCC: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), ",".join(CC), ",".join(BCC), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP(host, 587) # 587 is the TLS port, and is the usual default. 465 is deprecated.
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO + CC + BCC, message)
        server.close()
        print 'successfully sent the mail'
        return 0
    except Exception as exc:
        print "failed to send mail:", exc
        return 1
