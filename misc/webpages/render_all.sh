#!/bin/bash

url_list=$1

image_min_width=1024
image_min_heigth=768


while read line
do
	params=($line)
	out_file=${params[0]}
	url=${params[1]}
	if [[ "$out_file" =~ ^#.*$ ]]
	then
		return
	fi
	echo "rendering $url to $out_file"
	chromium-headless-shell --virtual-time-budget=10000 --timeout=15000 --screenshot=$out_file --window-size=$image_min_width,$image_min_heigth $url	
done < $url_list

