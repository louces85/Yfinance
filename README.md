# YFinance
[![NPM](https://img.shields.io/npm/l/react)](https://github.com/louces85/Yfinance/blob/master/LICENSE) 

# Sobre o projeto

YFinance é uma aplicação que auxilia na analise de ativos cadastrados na Bolsa Brasil Balcão (B3). O que motivou o desenvolvimento desta aplicação, foi em buscar por bons ativos que estão em tendencia de baixa nos ultimos 6 meses. 

A aplicação consiste em uma pesquisa de uma lista prévia de ativos cadastrados em arquivos de configuração, comparando seu preço atual com os preços máximos e minimos nos ultimos 6 meses. Então temos uma ordenação desses ativos em relação a razão R$ (preço atual/preço minimo) <= 1.1 , sendo assim, obtemos uma lista de ativos proximos à 10% de atingir a minima dos ultimos 6 meses.
OBS: É importante ressaltar que a aplicação só irar disponibilizar a analise de ativos que estão com o balanço positivos nos ultimos 4 anos.

## Layout Web
![Web 1](https://github.com/louces85/Yfinance/blob/master/assets/main.png)


# Tecnologias utilizadas
## Back end
- Python
- Java
- Shell Script

## Front end
- HTML / CSS

## Pré-requisitos:
 - Ubuntu 20.04 ou distribuição similar
 - Python 3
 - Pip3
 - Java 8

# Como executar o projeto

```bash

# criar a pastar do projeto
mkdir ~/Documents/YFinance

# entrar na pasta do projeto front end web
cd ~/Documents/YFinance/

# clonar repositório
https://github.com/louces85/Yfinance.git

# instalar dependências
pip3 install config/requirements -U

# executar o projeto
./run.sh

# abrir a aplicação no navegador
google-chrome index.html
```
# Como atualizar o histórico de preço dos ativos
É recomendado atualizar o histórico de preços a cada 7 dias. Este procedimento pode demorar alguns minutos, então recomenda-se que ele seja realizado após o pregrão.
OBS: Na primeira execução este arquivo está ausente, então sendo necessário rodar o script abaixo para a sua criação.

```bash

~/Documents/Yfinance/history_6mo.py

```
# Alterando os ativos que serão analizados
Os ativos podem ser alterados no arquivo de configuração a seguir:

```bash

vim ~/Documents/Yfinance/files/stocks_file

```

# Autor

Fabiano Louzada Cesario

https://www.linkedin.com/in/fabiano-louzada-cesario/

