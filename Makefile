setup:
	sudo apt install libpq-dev python3.9-dev
deploy-dev:
	mkdir python
	pip install -r requirements-pandas.txt --target python
	zip -r layer_pandas.zip python/
	rm -r python
	mkdir python
	pip install -r requirements-cockroachdb.txt --target python
	zip -r layer_cockroachdb.zip python/
	rm -r python
	sls deploy --stage dev --aws-profile palpiteiro
	rm layer_pandas.zip
	rm layer_cockroachdb.zip
deploy-main:
	mkdir python
	pip install -r requirements-pandas.txt --target python
	zip -r layer_pandas.zip python/
	rm -r python
	mkdir python
	pip install -r requirements-cockroachdb.txt --target python
	zip -r layer_cockroachdb.zip python/
	rm -r python
	sls deploy --stage main --aws-profile palpiteiro
	rm layer_pandas.zip
	rm layer_cockroachdb.zip