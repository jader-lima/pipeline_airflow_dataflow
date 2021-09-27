#!/bin/bash
echo "Project id: $1"
echo "Service account: $2"

gcloud iam service-accounts create $2 --description=$2 --display-name=$2

#for i in $(gcloud iam service-accounts list  | grep "$2");do
#  if [[ "$i" =~ $2 ]]; then
#    echo "result $i"
#  fi
#done

roles=( "dataflow.worker" "composer.admin" "composer.worker" "storage.admin" "iam.serviceAccountUser" "bigquery.jobUser" "bigquery.dataEditor")

for i in $(gcloud iam service-accounts list  | grep "$2");do
  if [[ "$i" =~ $2 ]]; then
    for y in ${!roles[@]};do
      gcloud projects add-iam-policy-binding  " $1 " --member=serviceAccount:"$i "--role=roles/"${roles[$y]}
    done    
  fi
done



