#!/bin/ksh
#
# This is an example on how to run generate all on MacOSX. This should produce xcode projects for you!
#
#

GENALL=`dirname $0`/../GenerateAll.py
echo $GENALL
python $GENALL -s
