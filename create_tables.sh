#!/bin/bash
echo "dataset $1"
echo "table $2"
echo "location $3"
echo "description $4"

bq --location=$3 mk -d --default_table_expiration 0  --description $4 $1

bq mk -t \
--schema schema.json \
--time_partitioning_field partition_date $1.$2
