#!/usr/bin/env python
#-*- coding: utf8 -*-
import cgi
import time
import os
import boto3
import sender

def regular_page(userId):
        print "Content-type:text/html\r\n\r\n"
        print '<html>'
        print '<head>'
        print '<meta charset="UTF-8">'
        print '<title>加工中...</title>'
        print '</head>'
        print '<body>'
        print '<h1>请至少等待半小时，再点击以下链接查看结果</h1>'
        print "<h1><a href='http://13.229.82.76/"+str(userId)+".html'><u>打开新世界大门的钥匙</u></a></h1>"
        print '</body>'
        print '</html>'
def error_page():
        print "Content-type:text/html\r\n\r\n"
        print '<html>'
        print '<head>'
        print '<meta charset="UTF-8">'
        print '<title>错误！</title>'
        print '</head>'
        print '<body>'
        print '<h1>请检查ID是否正确。请勿捣乱: )</h1>'
        print "<a href='http://13.229.82.76'><u>点击返回<ּ/u></a>"
        print '</body>'
        print '</html>'

form = cgi.FieldStorage() 
rawInput = str(form.getvalue('id')).replace(' ','')
if (rawInput.isdigit()):
        os.system("cp ../html/donate.html ../html/"+str(rawInput)+".html")
        regular_page(rawInput)
        sender.send(rawInput)
else:
        error_page()
