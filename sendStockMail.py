#!/usr/bin/python
# -*- coding: utf-8 -*-
#author:蔡董
#date:2017.11.26

# import smtplib

SMTPserver = 'smtp.163.com'
sender = '13146623011@163.com'
destination = '1171851914@qq.com'
passwd = '25698469'

# message = 'I send a message by Python. 你好'
# msg = MIMEText(message)
#
# msg['Subject'] = 'Test Email by Python'
# msg['From'] = sender
# msg['To'] = destination
#
# mailserver = smtplib.SMTP(SMTPserver, 25)
# mailserver.login(sender, password)
# mailserver.sendmail(sender, [sender], msg.as_string())
# mailserver.quit()
# print 'send email success'

from marrow.mailer import Mailer, Message
mailer = Mailer(dict(
        transport = dict(
                use = 'smtp',
                host = SMTPserver,
                password=passwd)))

mailer.start()
message = Message(author=sender, to=destination)
message.subject = "Testing Marrow Mailer"
message.plain = "This is a test."
mailer.send(message)

mailer.stop()