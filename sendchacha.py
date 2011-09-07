#!/usr/bin/env python
import time
import thread
import getpass
import smtplib
import threading
import multiprocessing
from multiprocessing import Process, Pool, Value
import email
import email.utils
import email.message
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
parser.add_option('-M','--multiprocessing',dest='multiprocessing',
        action='store_true')
parser.add_option('-f', '--file', dest='file', type='string', action='store',
        help='File to be used as email -overwrite headers defined by sender and recipient')
parser.add_option('-U','--unescape', dest='unescape',action='store_true',default=True, 
        help='Unescape the from/to headers in the case you want to use non-ascii values')
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
        from_domain = fromaddr.split("@")[-1]
        msgfrom = message['from'].split('@')[0]
        if options.unescape:
            from_domain = from_domain.decode('string_escape')
            msgfrom = msgfrom.decode('string_escape')
        fromaddr = msgfrom + "@" + from_domain
    else:
        counter.value += 1
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = "%d - %s"%(counter.value, toaddrs)
        msgRoot['From'] = fromaddr
        msgRoot['Reply-To'] = fromaddr
        msgRoot['Sender'] = fromaddr
        msgRoot['To'] = toaddrs
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        if options.message:
            message = options.message
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
    c.ehlo(fromaddr.split("@")[-1])
    if username and password:
        c.login(username,password)
    c.sendmail(fromaddr,toaddrs,msg)
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
    for to in toaddrs:
        time.sleep(0.001)
        create_process(fromaddr, to, msg, counter, username, password, host, port,
                    options.ssl)


while thread_list:
    for index, tr in enumerate(thread_list):
        if not getattr(tr,'is_alive', False):
            thread_list.pop(index)
            continue
        if not tr.is_alive():
            thread_list.pop(index)
