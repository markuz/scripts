#!/bin/bash
# This file is part of the Christine project
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
# @license   http://www.gnu.org/licenses/gpl.tx

EXCLUDE=""
EXCLUDEDIR=""
DEBUG=""
#By default, look on python scripts
STRINGS=""
EXT=""
#args=`getopt de:E: "$@"`
#set $args

function usage(){
    echo "busca_print.sh [eEdxh] query"
    echo ""
    echo "-e <files>\t\tFiles to be excluded"
    echo "-E <dirs>\t\tDirectories to be excluded"
    echo "-d \t\tDebug"
    echo "-x \t\tLook only for this extension(s)"
    echo "-h \t\tShow this help"
}


while getopts "de:E:x:h" OPTION
do
    case $OPTION in
        e) EXCLUDE="$EXCLUDE $OPTARG";;
        E) EXCLUDEDIR="$EXCLUDEDIR $OPTARG";;
        d) DEBUG="yes";;
        x) EXT="$EXT *$OPTARG";;
        h) HELP="yes";;
        *) STRINGS="$STRINGS $OPTARG";;
    esac
done
shift `expr $OPTIND - 1`

if [ "x$HELP" != "x" ]; then 
    usage;
    exit 0
fi

if [ "x$EXT" == "x" ]; then
    EXT='*py';
fi

if [ "x$EXT" == "x *none" ]; then
    EXT='*';
fi


function debug
{
    if [ "x$DEBUG" != "x" ]; then
        echo $*;
    fi
}

debug "Exclude: $EXCLUDE" ;
debug "Excludedir: $EXCLUDEDIR" ;
debug "Debug: $DEBUG";
debug "STRINGS : $@";
debug "EXT: $EXT";

for e in "$EXT"; do 
    newname=${e//[[:space:]]};
    debug "New name : $newname"
    for i in `find -L . -iname "$newname" 2> /dev/null`; do 
        E=`grep "$1" $i 2> /dev/null`; 
        for item in $EXCLUDE; do
            if [ "x$i" == "x$item" ]; then
                debug "Excluding $i";
                continue
            fi
        done
        for item in $EXCLUDEDIR; do
            result=`echo $i |grep -e "\./$item"`
            if [ "x$result" != "x" ]; then
                debug "Excluding $i";
                exclude=yes
            fi
        done
        if [ "x$exclude" != "x" ]; then
            continue
        fi
        if [ "x$E" == "x" ]; then 
            continue
        fi
        ISSVN=`echo $i |grep -e ".*.svn*"`
        if [ "x$ISSVN" != "x" ]; then
            continue
        fi
        for query in "$@"; do
            MATCH=`grep -n -w "$query" $i`
            if [ "x$MATCH" == "x" ]; then 
                continue
            fi
            echo ====$i:$query====; 
            python -c "import sys; map(lambda x: sys.stdout.write(x), sys.argv[1])" "$MATCH"
            python -c print ""
        done
    done
done
