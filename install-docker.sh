#!/bin/sh
scriptdir="$(dirname "$(realpath "$0")")"
if [ -z "$COORDSYSDEF" ]; then
    echo "Need COORDSYSDEF environment"
    exit 1
fi
tgtdir="$(dirname "$COORDSYSDEF")"
if ! rm -rf "$tgtdir" || ! mkdir -p "$(dirname "$tgtdir")" ; then
    echo "Cannot make coordsys directory $tgtdir"
    exit 1
fi
if ! cp -rP "$scriptdir/files" "$tgtdir"; then
    echo "Error copying liblinz-web-perl LINZ directory to $PERL5LIB"
    exit 1
fi