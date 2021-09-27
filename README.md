# pipeline_airflow_dataflow


![Logo of the project](https://beam.apache.org/images/logos/full-color/name-right/beam-logo-full-color-name-right-100.png)
![Logo of the project](/images/bigquery-productcard.png)

# ApacheBeam-OlistDataset
O objetivo desse projeto é demonstrar a utilização do apache-beam para criar um processo de ETL (extração ,transformação e carga de dados).
Primeiramente os dados são carregados e limpos , operações de contagem e soma são realizados conforme a necessidade e operações de junção são realizadas
para unir os datasets.
Os dados obtidos podem ser utilizados para criação de analises de dados ou dashboard com sua ferramenta de visualização preferida



## Instalação

Baixe o https://www.anaconda.com/products/individual#Downloads , ele instala a ultima versão do python , no momento que subi o repositório , a ultima versão é 3.7.


### Configuração inicial

Com o Anaconda instalado, baixe o apache-beam em no ambiente python desejado ou crie um novo ambiente e instale o apache-beam,
assim é possível desenvolver e testar o notebook  disponibilizado.

Caso deseje rodar a versão em script, após instalar o anaconda, execute o script criar_ambiente.bat que se encontra na pasta do projeto,
ele cria um ambiente python e instala o apache-beam.
Para ativar o ambeinte recem criado, execute o comando beam_python37\Scripts\activate  


## Desenvolvimento

```shell
git clone https://github.com/jader-lima/ApacheBeam-OlistDataset.git


```
Caso deseje utilizar a versão notebook, utilize o anaconda para editar e testar o notebook.
Para e versão em Script, utilize seu editor de texto favorito 


### Teste
Descompacte o arquivo zip data.zip .
Para a versão notebook, basta rodar o notebook passo a passou o em "Run all"
Já para a versão em script é necessário ativar o ambiente python criado , entrando dentro a pasta do projeto e executando via prompt beam_python37\Scripts\activate  
Ainda com o prompt,execute o comando abaixo , ele passa os arquivos da pasta data como entrada e grava um arquivo na pasta output, 
python etl.py --input_itens  data/olist_order_items_dataset.csv --input_sellers data/olist_sellers_dataset.csv --input_products data/olist_products_dataset.csv --input_order data/olist_orders_dataset.csv --input_reviews data/olist_order_reviews_dataset.csv --input_payments data/olist_order_payments_dataset.csv --input_customer data/olist_customers_dataset.csv --output output/saida.txt


## Links

- Página do projeto: https://github.com/jader-lima/pipeline_airflow_dataflow/

- Projetos relacionados:
  - Anaconda: https://www.anaconda.com
  - Apache Beam : https://beam.apache.org/
  - OlistDataset : https://www.kaggle.com/olistbr/brazilian-ecommerce?select=olist_customers_dataset.csv
  
 ## Autor
 
* **jader-lima**: (https://github.com/jader-lima)



