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
#         send-email-ntlm =  send-email --smtp-server /usr/bin/sendmail-htmlv2.py
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
toaddrs = sys.argv[2]  # git sendmail call this with arugments -i xxx@who.com

msgs = sys.stdin.readlines()
msg = ''.join(msgs)
#msg = 'hello world!'

#EXCHANGE_PASSWORD = 'ThisIsReallyMyPassword!'
EXCHANGE_PASSWORD = getpass('Password for ' + USER + ': ')

print("To: " + toaddrs)
print("Message length is", len(msg))

conn = SMTP(SMTPSVR_ADDR)
conn.set_debuglevel(0)
conn.starttls()
conn.ehlo()
ntlm_authenticate(conn, DOMAIN, USER, EXCHANGE_PASSWORD)
conn.sendmail(FROMADDR, toaddrs, msg)
conn.quit()

