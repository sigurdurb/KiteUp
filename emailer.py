#!/usr/bin/python3
import smtplib
import traceback

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import gmtime, strftime
import getpass

fromaddr = ""

def send_mail(message, toaddr):
    curr_time = strftime("%d/%m/%Y %H:%M:%S", gmtime())
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ', '.join(toaddr)
    msg['Subject'] = "KiteUp v.0.1.0 Alert System, Time:{}".format(curr_time)
    pw = "";
    
    body = """
{}

{}""".format(message, "disclaimer: this is a noreply address, if important contact some other way, this email is never checked")

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()

    server.login(fromaddr, pw)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()



