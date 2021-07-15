#!/bin/bash -e

while true
do
	files=`ls ../data/ | grep '^20'` || true #don't fail if there are no files
	sleep 10 #to ensure files are done writing
	for file in $files
	do
		aws s3 cp ../data/$file s3://trailer-monitor-rpi/
		mv ../data/$file ../data-past/
	done
done

