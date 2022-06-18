setup:
	sudo apt install libpq-dev python3.9-dev
deploy-dev:
	mkdir python
	pip install -r requirements-pandas.txt --target python
	zip -r layer_pandas.zip python/
	rm -r python
	mkdir python
	pip install -r requirements-bigquery.txt --target python
	zip -r layer_bigquery.zip python/
	rm -r python
	pip install -r requirements-sklearn.txt --target python
	zip -r layer_sklearn.zip python/
	rm -r python
	sls deploy --stage dev --aws-profile palpiteiro
	rm layer_pandas.zip
	rm layer_bigquery.zip
deploy-main:
	mkdir python
	pip install -r requirements-pandas.txt --target python
	zip -r layer_pandas.zip python/
	rm -r python
	mkdir python
	pip install -r requirements-bigquery.txt --target python
	zip -r layer_bigquery.zip python/
	rm -r python
	sls deploy --stage main --aws-profile palpiteiro
	rm layer_pandas.zip
	rm layer_bigquery.zip