#!/bin/bash

MESSAGE=$1
TITLE=$2

CMD="display notification \"$1\""
if [ "x$TITLE" != "x" ]; then
    CMD= "$CMD with title \"$title\"";
fi

echo "$CMD"

osascript -e "$CMD"

afplay /System/Library/Sounds/Glass.aiff
