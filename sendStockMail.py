#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.11.26

import smtplib
from email.mime.text import MIMEText

SMTPserver = 'smtp.163.com'
sender = '13146623011@163.com'
destination = '1171851914@qq.com'
password = '25698469'

message = 'I send a message by Python. 你好'
msg = MIMEText(message)

msg['Subject'] = 'Test Email by Python'
msg['From'] = sender
msg['To'] = destination

mailserver = smtplib.SMTP(SMTPserver, 25)
mailserver.login(sender, password)
mailserver.sendmail(sender, [sender], msg.as_string())
mailserver.quit()
print 'send email success'