#!/bin/bash

LOCAL_FILE=rules.yaml
REMOTE_URL=https://raw.githubusercontent.com/UniNuvola/promflux/refs/heads/main/rules.yaml

checkrules()
{
	# compute local MD5
	LOCAL_MD5=$(md5sum "$LOCAL_FILE" | awk '{ print $1 }')

	# compute remote MD5
	REMOTE_MD5=$(curl -sL "$REMOTE_URL" | md5sum | awk '{ print $1 }')

	# compare hashes
	if [[ "$LOCAL_MD5" == "$REMOTE_MD5" ]]; then
    	echo "Files are the same."
	else
    	echo "Files are different."
    	echo "Downloading new rules ..."
    	curl -o rules.yaml $REMOTE_URL 
	fi
}

while true
do
	sleep 10
	checkrules	
	python3 promflux.py
done
