setup:
	sudo apt install python3.9 python3.9-venv python3.9-dev libpq-dev -y
	python3.9 -m venv venv
	venv/bin/pip install --upgrade pip wheel
	venv/bin/pip install -r requirements-dev.txt -r requirements-pandas.txt -r requirements-bigquery.txt
layers:
	mkdir python
	pip install -r requirements-pandas.txt --target python
	zip -r layer_pandas.zip python/
	rm -r python
	mkdir python
	pip install -r requirements-bigquery.txt --target python
	zip -r layer_bigquery.zip python/
	rm -r python
deploy: layers
	sls deploy --stage dev
clean:
	rm layer_pandas.zip
	rm layer_bigquery.zip