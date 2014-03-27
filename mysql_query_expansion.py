#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
#
# This file is part of my scripts project
#
# Copyright (c) 2014 Marco Antonio Islas Cruz
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

# This is a simple script to convert a MySQL query and their arguments to a
# valid MySQL query (to be used with the terminal client).

import MySQLdb
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", dest="query", action="store",
        help="The query with all its expansion symbols")
parser.add_argument("-a","--args", dest="args", action="store",
        help=("The args to be used in the query, if this is not defined the "
            "values from the sys.argv will be used"))
parser.add_argument("-i","--aditional_imports", dest="imports", 
        help="Use this place to import modules required to evaluate the arguments",
        action="append")
args = parser.parse_args()

if args.imports:
    for i in args.imports:
        a = __import__(i, globals=globals(), locals=locals())
        globals()[i] = a
        locals()[i] = a


if not args.args:
    args.args = args

args.args = eval(args.args)

scapped_args = []
if args.args:
    for arg in args.args:
        if not isinstance(arg, basestring):
            arg = str(arg)
        scapped_args.append(repr(MySQLdb.escape_string(arg)))
scapped_args = tuple(scapped_args)

print 
print args.query % scapped_args

