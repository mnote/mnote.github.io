#!/usr/bin/env bash

# Resolve the location of installation.
# This includes resolving any symlinks.
PRG=$0
while [ -h "$PRG" ]; do
    ls=`ls -ld "$PRG"`
    link=`expr "$ls" : '^.*-> \(.*\)$' 2>/dev/null`
    if expr "$link" : '^/' 2> /dev/null >/dev/null; then
        PRG="$link"
    else
        PRG="`dirname "$PRG"`/$link"
    fi
done

BINDIR=`dirname "$PRG"`

# absolutize dir
oldpwd=`pwd`
cd "${BINDIR}"
BINDIR=`pwd`
cd "${BINDIR}/.."
BASEDIR=`pwd`
cd "${oldpwd}"
unset oldpwd

echo $BINDIR

cd "$BINDIR"

bundle exec jekyll serve