#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# This file is part of my scripts project
#
# Copyright (c) 2013 Marco Antonio Islas Cruz
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
import sys
import imaplib
import email
from optparse import OptionParser



parser = OptionParser()
parser.add_option("-e", "--email", dest="email", action="store",
        type="string", 
        help=("Username for the IMAP login. "
            "This will be used on both servers if --new-email is "
            "not defined"
            ))
parser.add_option("-n", "--new-email", dest="newemail", action="store",
        type="string",
        help="Username to connect to the new host")
parser.add_option("","--old-host", dest="oldhost",action="store",
        type="string",
        help="Old host. must be HOST:PORT")
parser.add_option("","--new-host", dest="newhost",action="store",
        type="string",
        help="New host, must be HOST:PORT")
parser.add_option("","--old-password", dest="oldpassword",action="store",
        type="string",
        help="old password")
parser.add_option("","--new-password", dest="newpassword",action="store",
        type="string",
        help="New password")
parser.add_option("","--prefix", dest="prefix",action="store",
        type="string",
        help="mailbox prefix")
options, args = parser.parse_args()

if not options.newemail:
    options.newemail = options.email

OLDHOST= options.oldhost.split(":")[0]
OLDPORT= int(options.oldhost.split(":")[1])
NEWHOST=options.newhost.split(":")[0]
NEWPORT=int(options.newhost.split(":")[1])


def move_folder_messages(d, oldhost, newhost):
    print "Entrando al directorio ", d
    typ, dat = oldhost.select(d)
    if typ != 'OK':
        print "Cannot select %r"%d
    #Seleccionar el directorio en el nuevo host.
    typ, dat = newhost.select(d)
    a,b = newhost.list()
    print typ, dat, d,a,b
    if typ != "OK":
        print "Can't select folder: '%r'"%d
        raise ValueError
    typ, data = oldhost.search(None, "ALL")
    for c, num in enumerate(data[0].split()):
        typ, data = oldhost.fetch(num, "(RFC822)")
        text = data[0][1]
        msg = email.message_from_string(text)
        subject = msg["Subject"]
        message_id = msg["Message-ID"]
########try:
########    searchpattern = '(HEADER Message-ID "%s")'%message_id
########    result, data = newhost.uid('search',None, 
########            searchpattern)
########except Exception, e:
########    print "No data: %s"%e
########    data = None
########print result, data
########if data and data[0]:
########    print ("Omitiendo el mensaje %s, ya se encuentra en el mailbox"
########            " destino (%r)" )%(subject, d)
########    continue
        print "moviendo el mensaje %s/%s"%(d,subject)
        newhost.append(d, None, None, msg.as_string())



#Conectar al host anterior
print "Connecting to %s:%d"%(OLDHOST, OLDPORT)
oldhost = imaplib.IMAP4(OLDHOST, OLDPORT)
print "Auth: %s,%s"%(options.email, options.oldpassword)
oldhost.login(options.email, options.oldpassword)

#Conectar al nuevo host
newhost = imaplib.IMAP4(NEWHOST, NEWPORT)
newhost.login(options.newemail, options.newpassword)

#Obtener la lista de directorios
result, dirs = oldhost.list()
print "Directorios encontrados"

dirs = map(lambda x: x.rsplit('"."', 1)[1].strip(), dirs)
newhdirs = map(lambda x: x.rsplit('"."', 1)[1].strip(), newhost.list()[1])
for directorio in dirs:
    if directorio not in newhdirs:
        print newhost.create(directorio)

for directorio in dirs:
    move_folder_messages(directorio, oldhost, newhost)
####try:
####    move_folder_messages(directorio, oldhost, newhost)
####except Exception, e:
####    print "Error, mailbox: %s, error %r"%(directorio, e)



