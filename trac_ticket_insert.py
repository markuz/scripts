#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the Markuz Scripts project
#
# Copyright (c) 2006-2009 Marco Antonio Islas Cruz
#
# Markuz Scripts is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Markuz Scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @package   Markuz Scripts
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2011 Markuz Scripts Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

import sys
import trac.ticket.model as model
from trac.ticket.notification import TicketNotifyEmail
from trac.env import open_environment
from optparse import OptionParser

parser = OptionParser(version='1.0')
parser.add_option('-s', '--status',dest='status',default='new',type='string')
parser.add_option('-t', '--type',dest='type',default='task',type='string')
parser.add_option('-u', '--summary',dest='summary',type='string',
        help='Short description of the ticket')
parser.add_option('-d', '--description',dest='description',type='string',
        help='Full description of the ticket')
parser.add_option('-r', '--reporter',dest='reporter',type='string')
parser.add_option('-o', '--owner',dest='owner',,type='string')
parser.add_option('-c', '--component',dest='component',type='string')
parser.add_option('-p', '--project',dest='project',type='string',
        help='Path to the project')
options, args = parser.parse_args()

if None in (options.summary, options.description, options.reporter,
        options.owner, options.component, options.project):
    sys.stderr.write("Please make sure that summary, description, reporter,"
            " owner, componnet and project are defined")
    sys.stderr.flush()
    sys.exit(1)


env = open_environment(options.project)

t = model.Ticket(env)
t['status'] = options.status
t['summary'] = options.summary
t['description'] = options.description
t['reporter'] = options.reporter
t['owner'] = options.owner
t['type'] = options.type
t['component'] = options.component
t.insert()

try:
    tn = TicketNotifyEmail(env)
    tn.notify(t, newticket=True)
except Exception, e:
    sys.stderr.writer("Failure sending notification on creation of ticket #%s: %s" % (t.id, e))
    sys.stderr.flush()
