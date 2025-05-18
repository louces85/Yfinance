#!/bin/bash

#cmd to run the script every hour on terminal
#for (( ; ; )) ; do ./run.sh ; mv  index.html /var/www/html/index.html ;  sleep 3600 ; done;

path=$(dirname "$0")
if [[ "$path" == "." ]]; then
    path=$(pwd)
fi

cd $path

unameOUT=`uname -s`
docker_exec_output=""
case "${unameOUT}" in
    Linux*)     docker_exec_output="docker exec -it yfinance-postgres psql -U postgres yfinance -c";;
    MINGW64*)   docker_exec_output="winpty -Xallow-non-tty docker exec -it yfinance-postgres psql -U postgres yfinance -c";;
    *)          exit 0
esac

$docker_exec_output "select count(*) from history where net_income = true;" > /dev/null 2>&1

if [ ! $? -eq 0 ]
	then
		echo "Restoring the database..."
		cat db/* | docker exec -i yfinance-postgres psql -U postgres
	fi


#curl -s --location -g --request GET 'https://statusinvest.com.br/category/advancedsearchresult?search=%7B%22Sector%22%3A%22%22%2C%22SubSector%22%3A%22%22%2C%22Segment%22%3A%22%22%2C%22my_range%22%3A%220%3B25%22%2C%22dy%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_L%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22peg_Ratio%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_VP%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemBruta%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22margemLiquida%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22eV_Ebit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaLiquidaEbit%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividaliquidaPatrimonioLiquido%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_SR%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_CapitalGiro%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_AtivoCirculante%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roe%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roic%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22roa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezCorrente%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22pl_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22passivo_Ativo%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22giroAtivos%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22receitas_Cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lucros_Cagr5%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezMediaDiaria%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22vpa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lpa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22valorMercado%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull}}&CategoryType=1' --header 'Content-Type: application/json' --header 'Cookie: _adasys=2f748b19-046e-4367-b285-ab79b67b53ba' --data-raw '' > files/all_indicators.json
echo '<html><head><meta http-equiv="refresh" content="30"></head>' > index.html
date +"%m-%d-%Y %T" >> index.html
cat css/stylesheet.css >> index.html 
python_version=`python -c 'import sys; print(".".join(map(str, sys.version_info[:1])))'`
if [ $python_version -eq 2 ]
	then
		python3 src/main.py >> index.html
else
		python src/main.py >> index.html
fi

for k in $(cat index.html | grep "padding-left: 1em; padding-right: 1em; text-align: left; vertical-align: top" | awk -F ">" '{print $2}' | awk -F "</" '{print $1}')
do
	sed -i "s|$k|<a href="https://www.google.com/finance/quote/$k:BVMF?window=1Y" target="_blank">$k</a>|g" "index.html"
done

#sed -i 's|<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">|<meta http-equiv="refresh" content="30">|g' "index.html"
echo '</html>' >> index.html