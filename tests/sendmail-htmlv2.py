# Copy this from:
# https://stackoverflow.com/questions/41686957/error-535-whilst-trying-to-send-email-from-python-and-ntlm-library

from smtplib import SMTP
from ntlm_auth.ntlm import Ntlm
import socket
from smtplib import SMTPException, SMTPAuthenticationError

workstation = socket.gethostname().upper()

def ntlm_authenticate(smtp, domain, username, password):
    code, response = smtp.docmd("AUTH", "NTLM")
    ntlm_context = Ntlm(ntlm_compatibility=2)
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

EXCHANGE_PASSWORD = 'ThisIsReallyMyPassword!'

fromaddr = 'anthony.shaw@ourcompany.com'
toaddrs = 'my.colleague@ourcompany.com'
msg= 'hello world!'

print("Message length is", len(msg))

conn = SMTP('webmail.ourcompany.com')
conn.set_debuglevel(1)
conn.starttls()
conn.ehlo()
ntlm_authenticate(conn, 'DOMAINXXX', 'anthony.shaw', EXCHANGE_PASSWORD)
conn.sendmail(fromaddr, toaddrs, msg)
conn.quit()

