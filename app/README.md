# API de Cálculo e Operações de Variações de Médias Móveis Simples

Projeto responsável por disponibilizar uma API, que permite executar as seguintes operações:
- Calcular a Variação de Média Móveis Simple de uma moeda, com base em um período informado, e gravar em banco de dados.
- Retornar informações das médias previamente calculadas, usando como filtro moeda, periodo e range de dias.
- Checkar se houve se houve a falha de algum dia especifico dentre de um período calculado.

## Dependências

- Python 3.8
- Pipenv
- MySQL
- mysql-connector-python
- Flask
- requests

##Arquivo de configurações


## Como executar
- É necessário que o client do Mysql instalado e startado localmente em seu computador.
- Usar como base o arquivo de configurações settings.py para criar/definir os objetos do banco de dados.

### Criação da base de dados

- Executar o comando de criação do banco de dados:
  - CREATE DATABASE {DATABASE_NAME};
  - USE {DATABASE_NAME};
- Executar o comando de criar a tabela no banco de dados:
  - CREATE TABLE {DATABASE_TABLE_NAME}(pair VARCHAR(50) NOT NULL,timestamp INTEGER(15) NOT NULL,mms_20 FLOAT NOT NULL default 0,mms_50 FLOAT NOT NULL default 0,mms_200 FLOAT NOT NULL default 0);


### Preparação do ambiente

O primeiro passo para executar o projeto será configurar o ambiente, instalando as dependências necessárias, isso pode
ser feito através do comando no seu terminal:

```bash
pipenv install
```

### Executando

Para subir a aplicação basta rodar o seguinte comando:

```bash
python -m flask run
```

## Variáveis de ambiente

O arquivo settings.py serve para definir a nomenclatura dos objetos de banco de dados, e definir o modo de execução do serviço(DEBUG), tambem define as variáveis que são usadas como Default na execução.

**Ps**: Em ambiente de desenvolvimento local(DEBUG=True), os calculos iram ignorar a chamada de API do mercado bitcion, e irá assumir os valores definidos em arquivos locais, juntamente com o periodo definido no settings.py.

### Variáveis do serviço

| Nome                    | Descrição                                            | Valor padrão |
|-------------------------|------------------------------------------------------|--------------|
| DATABASE_NAME           | Nome do Banco de Dados                               | mms_database |
| DATABASE_TABLE_NAME     | Nome da Tabela do Banco de Dados                     | mms_table    |
| DATABASE_HOST           | Endereço de Host do Banco de Dados                   | localhost    |
| DATABASE_USER           | Nome do Usuário do Banco de Dados                    | root         |
| DATABASE_PASSWORD       | Senha do Banco de Dados                              | ''           |
| FROM_DEFAULT_TIMESTAMP  | Timestamp padrão do início do período                | 1609459200   |
| TO_DEFAULT_TIMESTAMP    | Timestamp padrão do final do período                 | 1640908800   |
| DEFAULT_COIN            | Moeda padrão para o serviço de monitoramento         | ETH          |
| DEFAULT_RANGE           | Range de dias padrão para o serviço de monitoramento | 20           |

## API e Funçoes

### Calcular mms
####API Address
    - GET http://127.0.0.1:5000/calc_mms 
- Paramêtros
  - Nenhum
- 
- Retorno
  - 200 - Sucesso/Erro
    - Texto com a lista de moedas processadas ou não processadas.

- Fucionalidade
  - Será executado o cálculo de Variações de Médias Móveis Simples, de um determinado período e moedas pré-definidas.
    - Com o parametro Debug = False, será considerado o período de 1 ano, considerando o período de 365 adias para trás, a base histórica de informações de fechamento da moeda, será buscado de uma API disponibilizada pelo Mercado Bitcoin(Ex. https://mobile.mercadobitcoin.com.br/v4/BRLBTC/candle?from=1577836800&to=160656530
6&precision=1d).
    - Com o parametro Debug = True, será considerado o periodo disposto no arquivo settings.py, os arquivos de fechamento de moeda, seram os arquivos .json dispostos no projeto.
  - As moedas padrões para calculo são: BTC e ETH
  - Os dias de range para calculo são 20, 50, 100.
  - O processamento irá calcular, com base no fechamento que cada moeda, será calculado diariamente, com base no range, o valor médio de 20, 50, 200 dias anteriores, base de calculo : 
####
    - MMS = ( Fechamento[D0] + Fechamento[D-1] + Fechamento[D-2] ) / 3

- Após a execução do cálculo de todos os dias, será armazenado unitáriamente na tabela de banco de dados.   


### Consultar mms
####API Address
    - GET http://127.0.0.1:5000/:pair:/mms
- Exemplo request = http://127.0.0.1:5000/ETH/mms?from=1640822400&to=1640822400&range=20
- Paramêtros
  - pair - Indica a moeda a ser consultada
  - from - Int - Timestamp inicial da pesquisa
  - to - Int - Timestamp final da pesquisa
  - range - Int - Dias para base de cálculo [20,50,200]

- Retorno
  - 500 - Mensagem do erro
  - 200 - Sucesso
    - Dict com os valores unitários por dia/moeda e valor do range de dias.
    - Exemplo: 
    - [
  {
    "mms": 22511.3,
    "timestamp": 1640822400
  }
]

- Funcionalidade:
  - Será consultado no banco de dados, com base nos filtros, com os registros previamente calculados e retornado um dict com os valores por dia.


### Checkar dias não calculados
####API Address
    - GET http://127.0.0.1:5000/check_regs
- Paramêtros
  - Nenhum
- 
- Retorno
  - 200 - Sucesso
    - Dict com o valor dos dias que não foram calculados.
    - Exemplo: 
    - [
  {
    "timestamp": 1609545600
  }
]

- Funcionalidade:
  - Será validado um periodo padrão e uma moeda padrão definidos no settings.py, e será validado dia a dia se está presente na base de dados, caso falte um registro, será retornado uma lista com esses valores.