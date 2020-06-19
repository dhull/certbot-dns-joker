venv3/bin/certbot:
	python3 -m venv venv3
	source venv3/bin/activate && \
	pip install --upgrade pip && \
	pip install -e . && \
	certbot plugins

check: venv3/bin/certbot
	source venv3/bin/activate && \
	python -m unittest tests/dns_joker_test.py
