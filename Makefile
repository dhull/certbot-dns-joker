VERSION=1.0.0.dev0
CERTBOT_DNS_JOKER_WHL=certbot_dns_joker-$(VERSION)-py2.py3-none-any.whl
DOCKER_OTHER_PLUGINS=apache dns-nsone

venv3/bin/certbot:
	python3 -m venv venv3
	source venv3/bin/activate && \
	pip install --upgrade pip && \
	pip install -e . && \
	certbot plugins

check: venv3/bin/certbot
	source venv3/bin/activate && \
	python -m unittest tests/dns_joker_test.py

dist: venv3/bin/certbot
	rm -rf build dist
	source venv3/bin/activate && \
	pip install --upgrade pep517 && \
	python -m pep517.build .

docker-image: dist/$(CERTBOT_DNS_JOKER_WHL) Dockerfile
	rm -rf docker-context; mkdir docker-context
	ln Dockerfile install-other-plugins dist/$(CERTBOT_DNS_JOKER_WHL) docker-context/
	docker build --tag certbot-joker:$(VERSION) --tag certbot-joker \
	  --build-arg CERTBOT_DNS_JOKER_WHL=$(CERTBOT_DNS_JOKER_WHL) \
	  --build-arg DOCKER_OTHER_PLUGINS="$(DOCKER_OTHER_PLUGINS)" \
	  docker-context
	rm -rf docker-context

clean:
	rm -rf build dist docker-context

distclean: clean
	rm -rf venv3
	find . -name '*~' -exec rm -f {} \;
	find . -name __pycache__ -exec rm -rf {} \;
