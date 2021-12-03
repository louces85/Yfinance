#!/bin/bash

path=$(dirname "$0")
if [[ "$path" == "." ]]; then
    path=$(pwd)
fi

cd $path

if [ ! -s files/history_6mo_results_net_income ]
	then
		echo "This history file is empty, please run it to continue." > index.html
		exit 0
	fi

python_version=`python -c 'import sys; print(".".join(map(str, sys.version_info[:1])))'`
if [ $python_version -eq 2 ]
	then
		cat css/stylesheet.css > index.html 
		python3 src/main.py >> index.html
else
		cat css/stylesheet.css > index.html 
		python src/main.py >> index.html
fi

for k in $(cat index.html | grep "padding-left: 1em; padding-right: 1em; text-align: left; vertical-align: top" | awk -F ">" '{print $2}' | awk -F "</" '{print $1}')
do
	sed -i "s|$k|<a href="https://www.google.com/finance/quote/$k:BVMF?window=6M" target="_blank">$k</a>|g" "index.html"
done