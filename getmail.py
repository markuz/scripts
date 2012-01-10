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

import imaplib
import email
imaplib.IMAP4.debug = imaplib.IMAP4_SSL.debug = 1

username,passwd = ('usuario','password')

print 'Connecting via ssl IMAP...'
con = imaplib.IMAP4_SSL('host',993)
print 'Conected!!'
print 'Trying to login via ssl'
con.login(username, passwd)
print 'logged in!!'
print 'Selecting INBOX'
con.select()
print 'Searching data...'
typ, data = con.search(None, '(UNSEEN)')
c = 0
for num in data[0].split():
    typ, data = con.fetch(num, '(RFC822)')
    c +=1
    print "Found 1 message!"
    text = data[0][1]
    msg = email.message_from_string(text)
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        data = part.get_payload(decode=True)
        if not data:
            print 'No attachments...'
            continue
        f  = open(os.join(os.environ['HOME'],filename), 'w')
        f.write(data)
        f.close()
        
con.close()
con.logout()

