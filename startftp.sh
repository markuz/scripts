#!/bin/bash
if [ "x$1" == "xstop" ]; then
    sudo launchctl unload -w /System/Library/LaunchDaemons/ftp.plist
else
    sudo launchctl load -w /System/Library/LaunchDaemons/ftp.plist
fi
