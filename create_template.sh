#!/bin/bash
echo "runner $1"
echo "project $2"
echo "region $3"
echo "staging_location $4"
echo "temp_location $5"
echo "template_location $6" 
python etl_olist_template.py --runner $1 --project $2 --region $3 --staging_location $4 --temp_location $5 --template_location $6
