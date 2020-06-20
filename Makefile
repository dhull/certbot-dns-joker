BASEDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

VERSION=$(shell ./extract-meta version src/certbot_dns_joker/__init__.py)
CERTBOT_DNS_JOKER_TGZ=certbot-dns-joker-$(VERSION).tar.gz
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
	python setup.py test

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
	rm -rf build dist docker-context certbot_dns_joker.egg-info

distclean: clean
	rm -rf venv3
	find . -name '*~' -exec rm -f {} \;
	find . -name __pycache__ -prune -exec rm -rf {} \;

maintainer-clean: distclean
	rm -rf .eggs .pytest_cache

.PHONY: all check dist docker-image clean distclean maintainer-clean
