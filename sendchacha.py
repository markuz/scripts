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
import os
import time
import datetime
import getpass
import smtplib
import multiprocessing
from multiprocessing import Process, Value
import email
import email.utils
import email.message
#from email.Header import Header
from email import Encoders
from email.MIMEBase import MIMEBase
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
parser.add_option('','--cc', dest="cc", type='string',action="store", default=None)
parser.add_option('','--bcc', dest="bcc", type='string',action="store", default=None)
parser.add_option('','--subject',dest='subject',type='string', action='store',
        help='Custom subject for email', default=None)
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
parser.add_option('','--set-sender-encoding',dest='set_sender_encoding',
        action = 'store', type='string',
        help='Set the sender encoding to be used in the envelope header, note, this is not the FROM: header')
parser.add_option('','--set-recipient-encoding',dest='set_recipient_encoding',
        action = 'store', type='string',
        help='Set the recipient encoding to be used in the envelope header, note, this is not the TO: header')
parser.add_option('','--use-sendmail', dest='use_sendmail',action='store_true',
        help='Use the smtplib.SMTP[_SSL].sendmail method')
parser.add_option("","--set-helo-encoding", dest="helo_encoding",
        action="store",type="string",
        help="Set the encoding to be used by the HELO/EHLO string")
parser.add_option("","--set-subject-encoding", dest="subject_encoding",
        action="store",type="string",
        help="Set the encoding to be used by the string")
parser.add_option("","--one-message-per-recipient", dest="one_message_per_recipient", action="store_true",
        help="Useful when we want to pass thru all SMTP steps before sending a message to another recipient")
parser.add_option("","--python-values", dest="python_values", action="store_true",
        default=False,
        help=("When set, the values will be interpreted as python values, "
            "for example 'user@example.com' is a string, "
            "but u'user@example.com is unicode. "
            "This allows you to use nonprintable characters"))
parser.add_option("","--set-header", dest="set_header",
        action="append", 
        help=("Add the header to the headers in the mail, "
            "header must be a couple of KEY=VALUE items, "
            "this argument may be set multiple times to add "
            "more that one header"),
        default = [])
parser.add_option("","--attachment", dest="attachment",
        action="append",
        help=("Add the file to the message, you can define several "
            "files to be attached. with several --attach options"))
options, args = parser.parse_args()


if not options.email_per_connection:
    options.email_per_connection = 1

gmail = options.host.find("gmail") > -1

def debug(msg, *args):
    if not options.debug: 
        return
    if args:
        if not isinstance(msg, basestring):
            print msg
            return
        print msg % args
        return
    print msg

def error(msg, *args):
    if args:
        if not isinstance(msg, basestring):
            print msg
            return
        print msg % args
        return
    print msg

debug("cpucount = %s", multiprocessing.cpu_count())

if options.python_values:
    import codecs
    for key in [k for k in dir (options) if not k.startswith("_")]:
        value = options.__dict__.get(key, None)
        if not value:
            continue
        if not isinstance(value,basestring):
            continue
        options.__dict__[key] = codecs.escape_decode(value)[0]



def send_mail(fromaddr, toaddrs, message, counter, username, password, host, 
        port, usessl):
    now  = datetime.datetime.utcnow()
    if options.file:
        msg = None
        with open(options.file) as f:
            msg = f.read()
            msgRoot = email.message_from_string(msg)
            # Update date, some spam filters will not receive email that is 
            # long in the past or far in the future.
            del msgRoot['date']
            msgRoot['date'] = time.ctime(time.mktime(now.timetuple()))
    else:
        counter.value += 1
        msgRoot = email.message.Message()

    if options.subject != None:
        subject = options.subject
    else:
        subject  = "%d - %s"%(counter.value, toaddrs)
    if options.subject_encoding:
        subject = subject.decode("utf8").encode(options.subject_encoding)
    msgRoot.add_header('From', fromaddr)
    #msgRoot.add_header('Reply-To', fromaddr)
    #msgRoot.add_header('Sender', fromaddr)
    msgRoot.add_header('To', ",".join(map(lambda x: "<%s>"%x, toaddrs)))
    msgRoot.add_header('Subject', subject)
    if options.cc:
        msgRoot.add_header('cc', options.cc)
    if options.bcc:
        msgRoot.add_header('bcc', options.bcc)
    #msgRoot.add_header('date',  time.ctime(time.mktime(now.timetuple())))
    for raw_header in options.set_header:
        key, value = raw_header.split("=")
        msgRoot[key] = value
    if options.message:
        message = options.message
    if options.content_file:
        f = open(options.content_file)
        message = f.read()
        f.close()
    msgRoot.set_payload(message)
    for item in options.attachment:
        try:
            dat = open(item, "rb").read()
        except IOError:
            continue
        part = MIMEBase("appliation", "octect-stream")
        part.set_payload(dat)
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
               % os.path.basename(item))
        msgRoot.attach(part)
    msg = msgRoot.as_string()
    if usessl:
        c = smtplib.SMTP_SSL()
    else:
        c = smtplib.SMTP()
    c.set_debuglevel(options.debug)
    c.connect(host,port)
    if gmail:
        c.ehlo()
        c.starttls()
        c.ehlo()
    if options.helo:
        ehlo = options.helo
    else:
        ehlo = fromaddr.split("@")[-1]
    if options.helo_encoding:
        ehlo = ehlo.decode("utf8").encode(options.helo_encoding)
    c.ehlo(ehlo)
    if not (options.no_auth) and (username and password):
        c.login(username,password)
    else:
        if options.debug:
            debug("no-auth is being used")
    smtplib.quoteaddr = lambda x: "<%s>"%x
    if options.set_sender_encoding:
        fromaddr = fromaddr.decode('utf8').encode(options.set_sender_encoding)
    if options.set_recipient_encoding:
        if isinstance(toaddrs, basestring):
            toaddrs = toaddrs.decode("utf8").encode(options.set_recipient_encoding)
        else:
            encoding = options.set_recipient_encoding
            toaddrs = [k.decode("utf8").encode(encoding) for k in toaddrs]
    for i in xrange(int(options.email_per_connection)):
        if options.use_sendmail:
            if options.one_message_per_recipient:
                for recipient in toaddrs:
                    try:
                        print c.sendmail(fromaddr, recipient, msg)
                    except Exception, e:
                        error(e)
            else:
                try:
                    c.sendmail(fromaddr,toaddrs,msg)
                except Exception, e:
                    error(e)
        else:
            def csend(fromr, tor, msrgr):
                try:
                    debug("fromaddr: %s",repr(fromaddr))
                    c.mail(fromr)
                    if isinstance(tor, basestring):
                        tor = [tor]
                    debug("toaddrs: %s",tor)
                    for i in tor:
                        result = c.rcpt(i)
                        if result[0] != 250:
                            debug(" MSG ".center(80,"="))
                            print "reply: ", "".join(result[1:])
                            debug("".center(80,"="))
                            return
                    print c.data(msg)
                except Exception, e:
                    error(" ERROR ".center(80,"="))
                    error(e)
                    error( "".center(80,"="))
            if options.one_message_per_recipient:
                for recipient in toaddrs:
                    csend(fromaddr, recipient, msg)
            else:
                csend(fromaddr, toaddrs, msg)
    try:
        c.quit()
    except: 
        pass
    debug( counter.value)

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


if options.no_auth:
    password = ""
else:
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
        debug(diff)
        if diff > 0:
            time.sleep(1)
        else:
            ncounter = 0
            ntime = None
        continue
    i = thrn.pop(0)
    debug("Creating thread #%s",i)
    create_process(fromaddr, toaddrs, msg, counter, username, password, host, port,
                options.ssl)


while thread_list:
    for index, tr in enumerate(thread_list):
        if not getattr(tr,'is_alive', False):
            thread_list.pop(index)
            continue
        if not tr.is_alive():
            thread_list.pop(index)
