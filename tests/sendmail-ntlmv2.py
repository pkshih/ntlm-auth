#!/bin/python3

# Copy this from:
# https://stackoverflow.com/questions/41686957/error-535-whilst-trying-to-send-email-from-python-and-ntlm-library
#
# Modify for git sendmail.
# Usage:
#   1. with arguments
#      git send-email --smtp-server /PATH-TO/THIS_PROGRAM
#
#   2. use alias
#      edit ~/.gitconfig
#      add below to section [alias]
#         send-email-ntlm =  send-email --smtp-server /usr/bin/sendmail-ntlmv2.py
#      Then, use below command like git send-email
#      git send-email-ntlm
#
# Install component to support his
#   python setup.py install

from smtplib import SMTP
from ntlm_auth.ntlm import Ntlm
import socket
from smtplib import SMTPException, SMTPAuthenticationError
import sys
from getpass import getpass
from email.mime.text import MIMEText

workstation = socket.gethostname().upper()

def ntlm_authenticate(smtp, domain, username, password):
    code, response = smtp.docmd("AUTH", "NTLM")
    ntlm_context = Ntlm(ntlm_compatibility=3)
    if code != 334:
        raise SMTPException("Server did not respond as expected to NTLM negotiate message")

    code, response = smtp.docmd(ntlm_context.create_negotiate_message(domain, workstation).decode())

    if code != 334:
        raise SMTPException("Server did not respond as expected to NTLM challenge message")

    ntlm_context.parse_challenge_message(response)

    code, response = smtp.docmd(ntlm_context.create_authenticate_message(username, password,
                                                                         domain, workstation).decode())
    if code != 235:
        raise SMTPAuthenticationError(code, response)

# fill all of fields in upper case
USER = 'your_name'
DOMAIN = 'NT_domain'
FROMADDR = 'your_name@your_company.com'
SMTPSVR_ADDR = 'smtp_server.your_company.com'

# git sendmail call this with arugments -i xxx@who.com yyy.who2.com ...
# (the list includes To: and Cc:)
toaddrs = sys.argv[2:]

msgs = sys.stdin.readlines()

# split inputs into hdr and msg parts
hdr_region = 1
hdr = ''
msg = ''

for m in msgs:
    if hdr_region == 1 and m == "\n":
        hdr_region = 0
    elif hdr_region == 1:
        hdr = hdr + m
    else:
        msg = msg + m

#msg = ''.join(msgs)
#msg = 'hello world!'

msg_utf8 = MIMEText(msg, "plain", "utf-8").as_string()
msg = "\n" + msg  # only plain text need to re-add missing blank line

#print("hdr:\n" + hdr)
#print("msg:\n" + msg)
#print("msg_utf8:\n" + msg_utf8)
#print("hdr + msg:\n" + hdr + msg)
#print("hdr + msg_utf8:\n" + hdr + msg_utf8)

#EXCHANGE_PASSWORD = 'ThisIsReallyMyPassword!'
EXCHANGE_PASSWORD = getpass('Password for ' + USER + ': ')

print("To: " + ' '.join(toaddrs))

conn = SMTP(SMTPSVR_ADDR)
conn.set_debuglevel(0)
conn.starttls()
conn.ehlo()
ntlm_authenticate(conn, DOMAIN, USER, EXCHANGE_PASSWORD)
try:
    print("Send message in plain text with length", len(msg), end='')
    conn.sendmail(FROMADDR, toaddrs, hdr + msg)
    print("")
except UnicodeEncodeError:
    print(" ... ascii coding failed")
    print("Send message in utf8 text with length", len(msg_utf8))
    conn.sendmail(FROMADDR, toaddrs, hdr + msg_utf8)
conn.quit()

