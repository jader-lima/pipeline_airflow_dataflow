gcloud composer environments create airflow-jobs --location=us-east1 --zone=us-east1-b --machine-type=n1-standard-1 \
	--image-version=composer-1.16.16-airflow-1.10.12 --disk-size=20 --python-version=3 \
	--service-account=data-engineering-composer@dataengineering-324315.iam.gserviceaccount.com --node-count=3

