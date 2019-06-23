#!/bin/bash

for sol in ./sol/prob-*.sol.*; do
    dir=${sol%/*/*}
    base=${sol##*/}
    cur_res=${sol##*.}
    best_sol=${dir}/best-sol/${base%.sol.*}.sol.*
    #echo ""
    #echo "Current: $base"
    best_file=`find $best_sol`
    if [ -z "$best_file" ]
    then
	echo "No best solution for ${base} using this."
	cp "$sol" ./best-sol
    else
	#echo "Previous: ${best_file}"
	best_res=${best_file##*.}
	if [ "$cur_res" -lt "$best_res" ]
	then
	    echo "${base} is better then ${best_file}."
	    rm -f "$best_file"
	    cp "$sol" ./best-sol
	#else
	    #echo "!!! Old result is better."
	fi
    fi
done
