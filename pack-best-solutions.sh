#!/bin/bash
ts=`date '+%Y_%m_%d_%H_%M_%S'`
zipfile="TheWildLobsters_${ts}.zip"
for sol in ./best-sol/prob-*.sol.*; do
    dir=${sol%/*}
    base=${sol##*/}
    t=${dir}/${base%.sol*}.sol
    cp "$sol" "$t"
done
cd ./best-sol
echo "$zipfile"
zip $zipfile *.sol
cd ..
