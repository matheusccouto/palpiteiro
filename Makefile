setup:
	sudo apt install libpq-dev graphviz -y
	pip install --upgrade pip wheel
	pip install -r requirements-dev.txt
	npm install -g serverless@3
	npm install --save-dev serverless-step-functions
layer_pandas.zip:
	mkdir python
	pip install --target python --platform manylinux2014_x86_64 --implementation cp --python 3.9 --only-binary=:all: -r requirements-pandas.txt
	zip -r layer_pandas.zip python/
	rm -r python
layer_bigquery.zip:
	mkdir python
	pip install --target python --platform manylinux2014_x86_64 --implementation cp --python 3.9 --only-binary=:all: -r requirements-bigquery.txt
	zip -r layer_bigquery.zip python/
	rm -r python
deploy: layer_pandas.zip layer_bigquery.zip
	sls config credentials --provider aws --key $AWS_KEY --secret $AWS_SECRET -o
	sls deploy --stage dev
clean:
	rm layer_pandas.zip
	rm layer_bigquery.zip
gcloud:
	sudo apt-get install apt-transport-https ca-certificates gnupg -y
	echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
	curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
	sudo apt-get update && sudo apt-get install google-cloud-cli