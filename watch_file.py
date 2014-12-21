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

#
# Watch a file and execute the command
# with the specified path
#


import os 
import time
import logging
#from watchdog.observers import Observer
#from watchdog.observers.fsevents import FSEventsObserver as Observer
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-f','--file',dest='wfile',action='store',type='string',
        help='The file being watched')
parser.add_option('-c','--command',dest='command',action='store',type='string',
        help='Command to execute, you can use {file} to put the file path in the command.')
options, args = parser.parse_args()

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

class MyHandler(FileSystemEventHandler):
    #def __init__(self, *args, **kwargs):
    #    FileSystemEventHandler.__init__(self, *args,**kwargs)

    def execute_command(self, event):
        logger = logging.getLogger()
        command = options.command
        if command.find("{file}")>-1:
            command = command.replace("{file}","%(file)s")
            command = command % {"file":options.wfile}
        logger.info(command)
        os.system(command)
        logger.info("Done!")

    def on_created(self, event):
        self.execute_command(event)

    def on_modified(self, event):
        self.execute_command(event)

    def on_moved(self, event):
        self.execute_command(event)


if __name__ == "__main__":
    observer = Observer()
    logging.info("watching %r"%options.wfile)
    event_handler = MyHandler()
    observer.schedule(event_handler, options.wfile, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
