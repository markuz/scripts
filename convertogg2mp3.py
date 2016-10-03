#!/usr/bin/env python
# -*- encoding: utf8 -*-
# -*- coding: utf8 -*-
#
# This scripts helps to convert ogg files in a directory and subdirectories
# taking care of the spaces that might be in the file path.
#
# Note, for quickness this script makes use of "find" to get the ogg files,
#       "ogg123" to reproduce the oggfile and "lame" to encode to mp3
#
# Note2. This script starts the work on the current directory,

import os
import sys
import shutil
import tempfile
import subprocess

from multiprocessing import Pool, cpu_count

print "Finding files..."
process = subprocess.Popen("find . -iname '*ogg'", shell=True, 
                           stdout = subprocess.PIPE )
print "Done"

all_files = 0
processed_files = 0
STEPS = [0, "",""]

def process_song(args):
    fpath, STEPS = args
    #print "processing: %s" % fpath.strip()
    STEPS[1] = os.path.basename(fpath.strip())
    newpath = fpath.rsplit(".",1)[0] + ".mp3"
    if os.path.exists(newpath):
        #print "mp3 already exists"
        STEPS[0] += 1
        return
    # Copy to a temporary file. 
    fp, path = tempfile.mkstemp()
    with open(fpath.strip(), "rb") as oggfp:
        with open(path, "wb") as fp:
            fp.write(oggfp.read())
            fp.flush()
    encfp, encpath = tempfile.mkstemp()
    os.close(encfp)
    command = ('/opt/local/bin/ogg123 -d wav -f - "%s" | '
               '/opt/local/bin/lame -h -m s -b 192 - "%s.mp3"' % 
               (path, encpath))
    encproc = subprocess.Popen(command, stdout = subprocess.PIPE, 
                               stderr = subprocess.PIPE, shell=True)
    encproc.communicate()
    #print "%s.mp3 => %s" % (encpath, newpath)
    try:
        shutil.move(encpath+".mp3", newpath)
    except IOError:
        print "Can't move %s", newpath
    else:
        STEPS[2] = os.path.basename(fpath.stripp())
    STEPS[0] += 1
    os.unlink(path)

if len(sys.argv) >= 2:
    process_to_disppatch = int(sys.argv[1])
    if not process_to_disppatch:
        process_to_disppatch = cpu_count()
else:
    process_to_disppatch = 1

print "Process to dispatch: %d"%process_to_disppatch
po = Pool(process_to_disppatch)

all_files = process.readlines()

results = po.map(process_song, ((k, STEPS) for k in all_files))
