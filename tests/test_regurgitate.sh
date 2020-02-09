#!/bin/sh

python3 ../samparser.py regurgitate conditioned_rows.sam > conditioned_rows.dump

diff conditioned_rows.sam conditioned_rows.dump > /dev/null 2>&1

error=$?
if [ $error -eq 0  ]; then
   echo "Successfully parsed and regurgitated input"
elif [ $error -eq 1 ]; then
   echo "Regurgitated output does not match input"
else
   echo "Diff command failed"
fi

