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
process = subprocess.Popen("find . -iname '*m4a'", shell=True, 
                           stdout = subprocess.PIPE,
                           stderr = subprocess.PIPE)
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
    try:
        with open(fpath.strip(), "rb") as oggfp:
            with open(path, "wb") as fp:
                fp.write(oggfp.read())
                fp.flush()
    except:
        print "Can't copy the file %r to a temporary location" % fpath
        sys.exit(-1)
    encfp, encpath = tempfile.mkstemp()
    os.close(encfp)
    command = ('ffmpeg -i %s -acodec libmp3lame -ab 128k %s' % (path,
               encpath))
    print command
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

try:
    all_files = process.stdout.readlines()
except AttributeError:
    print process.stderr.read()
    sys.stdout.write("Can't find a m4a file..")
    sys.stdout.flush()
    sys.exit(-1)


results = po.map(process_song, ((k, STEPS) for k in all_files))
