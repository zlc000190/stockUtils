#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
发送带附件的邮件基本思路如下：
1. 构造 MIMEMultipart 对象做为根容器
2. 构造 MIMEText 对象做为邮件显示内容并附加到根容器
3. 构造 MIMEImage 对象做为图片附件并附加到根容器
4. 构造 MIMEBase 对象做为文件附件内容并附加到根容器
　　a. 读入文件内容并格式化
　　b. 设置判断MIME类型并设置附件头
5. 设置根容器属性
6. 得到格式化后的完整文本
7. 用 smtp 发送邮件

20151016
"""

import os
import mimetypes
import smtplib
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email import encoders


SMTPserver = 'smtp.163.com'
sender = '13146623011@163.com'
destination = ['1072079578@qq.com','546528535@qq.com','2717197561@qq.com']
passwd = '25698469'

login = {'smtpserver': SMTPserver,
         'username': sender,
         'password': passwd}


def send_email(login=None, mail=None, images=None, attachments=None, use_ssl=None):
    """发送常规邮件,可以有图片和其它格式的附件

    :param login: dict:登录信息,包括smtp服务器地址,帐号,密码
                        {'smtpserver': 'smtp.163.com',
                         'username': 'xxx@163.com',
                         'password': 'xxx'}
    :param mail: dict:邮件内容,包含邮件类型,发送人,收件人(多人的话要使用列表),标题,内容.
                        {'email_type': "html",    # 可以是:plain\html
                         'from': 'xxx@163.com',
                         'to': 'xxx@126.com',
                         'subject': "标题",
                         'content': "正文"}
    :param images:          # 图片附件列表(由路径组成)
    :param attachments:     # 其它附件列表(由路径组成)
    :param use_ssl:         # 否使用 ssl(暂时无用0
    :return:
    """

    smtpserver = login.get("smtpserver")
    username = login.get("username")
    password = login.get("password")

    email_type = mail.get('email_type')
    From = mail.get('from')
    To = mail.get('to')
    Subject = mail.get('subject')
    content = mail.get('content')

    if not To:
        To = username
    # To 是列表,就用分隔符合并
    if isinstance(To, list):
        To = ','.join(To)

    if not email_type or (email_type not in ("plain", "html")):
        email_type = "html"

    # 构造MIME Multipart 对象做为根容器
    main_msg = MIMEMultipart()

    # 添加公共信息
    main_msg['Subject'] = Subject
    main_msg['From'] = From
    main_msg['To'] = To
    # main_msg.preamble = content[:100]       # 序文

    # 构造MIMEText对象做为邮件显示内容并附加到根容器,统一使用 utf-8
    text_msg = MIMEText(content, email_type, 'utf-8')
    main_msg.attach(text_msg)

    if images:
        for f in images:
            fp = open(f, 'rb')
            img_msg = MIMEImage(fp.read())  # 没有 _subtype 参数,MIMEImage 会自己探测图片类型
            fp.close()

            # 设置附件头
            basename = os.path.basename(f)
            img_msg.add_header('content-disposition',
                               'image' + str(images.index(f)), filename=basename)
            main_msg.attach(img_msg)

    if attachments:
        # 构造MIMEBase对象做为文件附件内容并附加到根容器
        for f in attachments:
            basename = os.path.basename(f)
            # 判断文件 MIME
            if "." in basename:     # 带扩展名的
                content_type = mimetypes.types_map["." + basename.split(".")[-1]]
            else:                   # 无扩展名的
                content_type = 'application/octet-stream'
            maintype, subtype = content_type.split('/', 1)

            fp = open(f, 'rb')
            file_msg = MIMEBase(maintype, subtype)
            file_msg.set_payload(fp.read())
            fp.close()

            encoders.encode_base64(file_msg)

            # 设置附件头
            file_msg.add_header('Content-Disposition',
                                'attachment' + str(images.index(f)), filename=basename)
            main_msg.attach(file_msg)

    smtp = smtplib.SMTP(smtpserver)
    # 使用 ssl 的情况
    if use_ssl:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

    smtp.login(username, password)
    # smtp.set_debuglevel(1)            # 调试模式
    smtp.sendmail(From, To, main_msg.as_string())
    smtp.quit()


    # {
    #     "t": "plain",
    #     "s": "测试纯文本的 email",
    #     "c": """
    #         测试一下纯文本内容,为什么不让我过?
    #         •553 Requested action not taken: NULL sender is not allowed 不允许发件人为空，请使用真实发件人发送；
    #       　　•553 Requested action not taken: Local user only  SMTP类型的机器只允许发信人是本站用户；
    #         """,
    #     "a": None,
    #     "i": None
    # },
    # {
    #     "t": "html",
    #     "s": "测试 html 格式的 email",
    #     "c": """
    #         测试一下HTML格式的内容,为什么不让我过?<br/>
    #         •550 Requested mail action not taken: too much recipient  群发数量超过了限额；<br/>
    #         <hr/>
    #       　　•552 Requested mail action aborted: exceeded mailsize limit 发送的信件大小超过了网易邮箱允许接收的最大限制；<br/>
    #       　　•553 Requested action not taken: NULL sender is not allowed 不允许发件人为空，请使用真实发件人发送；<br/>
    #       　　•553 Requested action not taken: Local user only  SMTP类型的机器只允许发信人是本站用户；<br/>
    #       　　•553 Requested action not taken: no smtp MX only  MX类型的机器不允许发信人是本站用户；<br/>
    #         """,
    #     "a": None,
    #     "i": None
    # },
    # {
    #     "t": "html",
    #     "s": "测试 带图片的 email",
    #     "c": """
    #         测试一下带图片的内容<br/>
    #         •550 Requested mail action not taken: too much recipient  群发数量超过了限额；<br/>
    #         """,
    #     "a": ("logo.png", "logo_s.png"),
    #     "i": ("logo.png", "logo_s.png")
    # },
# ]

def sendMail(fr,toList,subject,content):
        mail = {
            'email_type': 'plain',
            'from': sender,
            'to': destination,    # 单人用字符串,多人用列表
            'subject': subject,
            'content': content,
        }
        send_email(login=login, mail=mail)
