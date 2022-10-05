codespaces: diagrams
pip:
	pip install --upgrade pip wheel
diagrams: pip
	sudo apt install graphviz -y
	pip install diagrams