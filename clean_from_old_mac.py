#! /usr/bin/env python
# -*- coding: utf-8 -*-
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


#TODO: print something about sockets

import os
import sys
import shutil
import subprocess
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-v','--verbose',dest = 'verbose', action='store_true',
        help='Print extra information')
options, args = parser.parse_args()

entries = []
process_info = os.popen("locate 'from old Mac'")
tmpentries = process_info.read().split("\n")
   
print "Calculating size..."

totsize = 0
totfiles = 0
totdirs = 0
totlinks = 0
totunknown = 0

for item in tmpentries:
    if not os.path.exists(item):
        continue
    entries.append(item)
    if os.path.isfile(item):
        stat = os.stat(item)
        size = stat.st_size
        totsize += size
        totfiles += 1
    elif os.path.isdir(item):
        totdirs += 1
    elif os.path.islink(item):
        totlinks += 1
    else:
        print item
        totunknown +=  1
#Resume
print "Number of files: ", totfiles
print "Number of directories: ", totdirs
print "Number of links: ", totlinks
print "Number of unknown files: ", totunknown
print "Total space saved: ", (totsize/1024)/1024, "MB"


cont = raw_input("Continue [y/N]")

if cont.lower() != "y":
    sys.exit()

while entries:
    entry = entries.pop()
    if "(from old Mac)" in entry:
        if os.path.isfile( entry ) or os.path.islink( entry ):
            if options.debug:
                print "delete file", entry
            func = os.remove
        elif os.path.isdir( entry ):
            if options.debug:
                print "rm dir", entry
            func = shutil.rmtree
        else:
            print "Unknown type for '%s' didn't touch it."%entry
        try:
            func(entry)
        except Exception, e:
            sys.stderr.write(e)
            sys.stderr.flush()

