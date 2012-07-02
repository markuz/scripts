#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# This file is part of my scripts project
#
# Copyright (c) 2011 Marco Antonio Islas Cruz
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2011 Marco Antonio Islas Cruz
# @license   http://www.gnu.org/licenses/gpl.txt
import time
import datetime
import thread
import getpass
import smtplib
import threading
import multiprocessing
from multiprocessing import Process, Pool, Value
import email
import email.utils
import email.message
from email.Header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-e','--email',dest='email',action='store',type='string')
parser.add_option('-u','--username',dest='username',action='store',type='string')
parser.add_option('-s','--sender',dest='sender',action='store',type='string')
parser.add_option('-p','--password',dest='password',action='store',type='string')
parser.add_option('-H','--host',dest='host',action='store',type='string')
parser.add_option('-c','--count',dest='count',action='store',type='string')
parser.add_option('-S','--ssl',dest='ssl',action='store_true')
parser.add_option('-d','--debug',dest='debug',type='int', action='store')
parser.add_option('-m','--message',dest='message',type='string', action='store')
parser.add_option('','--subject',dest='subject',type='string', action='store',
        help='Custom subject for email')
parser.add_option('-M','--multiprocessing',dest='multiprocessing',
        action='store_true')
parser.add_option('-C', '--content_file', dest='content_file', type='string', action='store',
        help='File to be read as content, it should be simple text')
parser.add_option('-f', '--file', dest='file', type='string', action='store',
        help='File to be used as email -overwrite headers defined by sender and recipient')
parser.add_option('-U','--unescape', dest='unescape',action='store_true',default=True, 
        help='Unescape the from/to headers in the case you want to use non-ascii values')
parser.add_option('-T','--use-smtp-domain', dest='use_smtp_domain', action='store_true',
        help='Use the smtp domain in the from address, this only works with -f')
parser.add_option('-E','--helo',dest='helo',action='store',type='string',
        help='Custom HELO/EHLO string')
parser.add_option('-N','--no-auth', dest='no_auth',action='store_true',
        help='Do not use SMTP_AUTH')
parser.add_option('','--email-per-connection',dest='email_per_connection',
        action = 'store', type='string',
        help='Says how many messages should be sent on every connection.')
options, args = parser.parse_args()

print "cpucount = ", multiprocessing.cpu_count()

debug = options.debug
if not debug:
    debug = 0

gmail = options.host.find("gmail") > -1

def send_mail(fromaddr, toaddrs, message, counter, username, password, host, 
        port, usessl):
    if options.file:
        f = open(options.file)
        msg = f.read()
        f.close()
        message = email.message_from_string(msg)
        # Update date, some spam filters will not receive email that is 
        # long in the past or far in the future.
        now  = datetime.datetime.utcnow()
        del message['date']
        message['date'] = time.ctime(time.mktime(now.timetuple()))
        print "Date>>>>>>>>>>>>>>" ,message['date']
        msg = message.as_string()
        from_domain = fromaddr.split("@")[-1]
        msgfrom = message['from'].split('@')[0]
        if options.unescape:
            from_domain = from_domain.decode('string_escape')
            msgfrom = msgfrom.decode('string_escape')
        if options.use_smtp_domain:
            from_domain = options.username.split("@")[1]
        fromaddr = msgfrom + "@" + from_domain
    else:
        counter.value += 1
        msgRoot = MIMEMultipart('related')
        if options.subject:
            msgRoot['Subject'] = options.subject
        else:
            msgRoot['Subject'] = "%d - %s"%(counter.value, toaddrs)
        msgRoot['From'] = Header(fromaddr,'latin1')
        msgRoot['Reply-To'] = Header(fromaddr,'latin1')
        msgRoot['Sender'] = fromaddr
        msgRoot['To'] = ",".join(map(lambda x: "<%s>"%x, toaddrs))
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        if options.message:
            message = options.message
        if options.content_file:
            f = open(options.content_file)
            message = f.read()
            f.close()
        msgText = MIMEText(message, 'html')
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgAlternative.attach(msgText)
        msg = msgRoot.as_string()
    if usessl:
        c = smtplib.SMTP_SSL()
    else:
        c = smtplib.SMTP()
        
    c.set_debuglevel(debug)
    c.connect(host,port)
    if gmail:
        c.ehlo()
        c.starttls()
        c.ehlo()
    if options.helo:
        c.ehlo(options.helo)
    else:
        c.ehlo(fromaddr.split("@")[-1])
    if not options.no_auth:
        if username and password:
            c.login(username,password)
    smtplib.quoteaddr = lambda x: "<%s>"%x
    for i in xrange(int(options.email_per_connection)):
        c.sendmail(fromaddr,toaddrs,msg)
    #c.sendmail(fromaddr,toaddrs,msg)
    c.quit()
    print counter.value

def create_process(fromaddr, toaddrs, msg, counter, username, password, host, 
        port, usessl):
    if not options.multiprocessing:
        return send_mail(fromaddr, toaddrs, msg, counter, username, password, host, 
              port, usessl)
    else:
        p = Process(target= send_mail, 
           args = (fromaddr, toaddrs, msg, counter, username, password, host, 
               port, usessl))
        p.start()
        return p


counter = Value('d',0)
if options.sender:
    fromaddr= options.sender
else:
    fromaddr = 'nobody@example.com'

if options.username:
    username = options.username
else:
    username = fromaddr

port = None
if options.host:
    host = options.host
    if len(host.split(":")) == 2:
        host, port = host.split(":")
else:
    local, remote = fromaddr.split("@")
    host = 'mail.%s'%remote


if options.password:
    password = options.password
else:
    password = getpass.getpass('Sender password: ')

if not options.email:
    t = raw_input('to: ')
    if t:
        toaddrs = t
    toaddrs = toaddrs.split(',')
else:
    toaddrs = options.email.split(",")
msg = time.ctime()
thread_list = []
if options.count:
    numbers = options.count
else:
    numbers = raw_input("How many mails do you need to be sent?")
thrn = range(int(numbers))
ncounter =0
ntime = None
#========== resume =============
print "Sending %s mails"%numbers
print "from '%s' to '%s'"%(fromaddr, repr(toaddrs))
print "using the server",host,
if port:
    print "and port",port
else:
    print "default port"
print "using ssl: ",['no','yes'][bool(options.ssl)]
print "authenticated with '%s' and "%username
if password:
    print "password not None"
else:
    print "no password"

#=========================
while thrn:
    ncounter +=1
    if len(thread_list) >= 50:
        time.sleep(0.01)
    if ncounter >= 100:
        if not ntime:
            ntime = time.time() + 30
        diff = ntime - time.time()
        print diff
        if diff > 0:
            time.sleep(1)
        else:
            ncounter = 0
            ntime = None
        continue
    i = thrn.pop(0)
    print "Creating thread #",i
    #print (to.decode('utf8').encode('GBK'),)
    create_process(fromaddr, toaddrs, msg, counter, username, password, host, port,
                options.ssl)


while thread_list:
    for index, tr in enumerate(thread_list):
        if not getattr(tr,'is_alive', False):
            thread_list.pop(index)
            continue
        if not tr.is_alive():
            thread_list.pop(index)
