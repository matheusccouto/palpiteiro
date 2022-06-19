setup:
	sudo apt install libpq-dev python3.9-dev
deploy:
	mkdir python
	pip install -r requirements-pandas.txt --target python
	zip -r layer_pandas.zip python/
	rm -r python
	mkdir python
	pip install -r requirements-bigquery.txt --target python
	zip -r layer_bigquery.zip python/
	rm -r python
	sls deploy --stage dev
	rm layer_pandas.zip
	rm layer_bigquery.zip