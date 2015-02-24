#! /bin/bash
sudo killall -HUP mDNSResponder
# If we are runnign OS X
sudo discoveryutil udnsflushcaches
