#!/bin/bash

trap "exit" INT

OPTIONS="--similarity-links -d 3 -w 0.3"

for file in data/duc/*.original
do
    name=$(basename $file)
    name=${name%.original}
    echo $name >&2
    gold=${file%.original}.gold

    morewords=$(wc -w $file | awk '{print $1}')
    words=$(wc -w $gold | awk '{print $1}')

    echo -n "$name $morewords $words "
    ./summary.py $file $gold -q --baseline --hits $OPTIONS -n $words | tr '\n' ' '
    timeout 3m ./summary.py $file $gold -q --clustering $OPTIONS -n $words
    echo ""
done
