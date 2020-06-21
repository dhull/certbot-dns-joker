# -*- mode:makefile-gmake -*-

BASEDIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

VERSION=$(shell ./packaging/extract-meta version src/certbot_dns_joker/__init__.py)
CERTBOT_DNS_JOKER_TGZ=certbot-dns-joker-$(VERSION).tar.gz
CERTBOT_DNS_JOKER_WHL=certbot_dns_joker-$(VERSION)-py2.py3-none-any.whl
CERTBOT_DNS_JOKER_RPM=python3-certbot-dns-joker-$(VERSION)-1.el8.noarch.rpm
CERTBOT_DNS_JOKER_SPEC=python-certbot-dns-joker.spec
DOCKER_OTHER_PLUGINS=apache dns-nsone

all: dist

venv3/bin/certbot:
	python3 -m venv venv3
	source venv3/bin/activate && \
	pip install --upgrade pip && \
	pip install -e . && \
	certbot plugins

check: venv3/bin/certbot
	source venv3/bin/activate && \
	python setup.py test

dist: dist/$(CERTBOT_DNS_JOKER_TGZ) dist/$(CERTBOT_DNS_JOKER_WHL)

dist/$(CERTBOT_DNS_JOKER_TGZ) dist/$(CERTBOT_DNS_JOKER_WHL): venv3/bin/certbot
	rm -rf build dist
	find . -name '*~' -exec rm -f {} \;
	source venv3/bin/activate && \
	pip install --upgrade pep517 && \
	python -m pep517.build .

rpm: dist/$(CERTBOT_DNS_JOKER_RPM)

dist/$(CERTBOT_DNS_JOKER_RPM): dist/$(CERTBOT_DNS_JOKER_TGZ) packaging/$(CERTBOT_DNS_JOKER_SPEC)
	rm -rf rpmbuild
	mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	ln dist/$(CERTBOT_DNS_JOKER_TGZ) rpmbuild/SOURCES/
	perl -p -e 's/^(Version:\s+).*/$${1}$(VERSION)/;' packaging/$(CERTBOT_DNS_JOKER_SPEC) >rpmbuild/SPECS/$(CERTBOT_DNS_JOKER_SPEC)
	rpmbuild -ba -D '%_topdir $(BASEDIR)/rpmbuild' rpmbuild/SPECS/$(CERTBOT_DNS_JOKER_SPEC)
	test -f rpmbuild/RPMS/noarch/$(CERTBOT_DNS_JOKER_RPM)
	shopt -s nullglob && ln rpmbuild/RPMS/noarch/* rpmbuild/SRPMS/* dist/
	rm -rf rpmbuild

docker-image: dist/$(CERTBOT_DNS_JOKER_WHL) packaging/Dockerfile packaging/install-other-plugins
	rm -rf docker-context; mkdir docker-context
	ln packaging/Dockerfile packaging/install-other-plugins dist/$(CERTBOT_DNS_JOKER_WHL) docker-context/
	docker build --tag certbot-joker:$(VERSION) --tag certbot-joker \
	  --build-arg CERTBOT_DNS_JOKER_WHL=$(CERTBOT_DNS_JOKER_WHL) \
	  --build-arg DOCKER_OTHER_PLUGINS="$(DOCKER_OTHER_PLUGINS)" \
	  docker-context
	rm -rf docker-context

publish-pypi: venv3/bin/certbot dist/$(CERTBOT_DNS_JOKER_TGZ) dist/$(CERTBOT_DNS_JOKER_WHL)
	git rev-parse $(VERSION) >/dev/null 2>&1 || { echo "version $(VERSION) not tagged"; exit 1; }
	source venv3/bin/activate && \
	pip install --upgrade twine
	python3 -m twine upload dist/$(CERTBOT_DNS_JOKER_TGZ) dist/$(CERTBOT_DNS_JOKER_WHL)

publish-github: dist/$(CERTBOT_DNS_JOKER_TGZ) dist/$(CERTBOT_DNS_JOKER_WHL) dist/$(CERTBOT_DNS_JOKER_RPM)
	git rev-parse $(VERSION) >/dev/null 2>&1 || { echo "version $(VERSION) not tagged"; exit 1; }
	./packaging/format-release-message certbot-dns-joker $(VERSION) | \
	  hub release create -d -F - $(addprefix -a ,$(wildcard dist/*-$(VERSION)*)) $(VERSION)

clean:
	rm -rf build dist rpmbuild docker-context certbot_dns_joker.egg-info

distclean: clean
	rm -rf venv3
	find . -name '*~' -exec rm -f {} \;
	find . -name __pycache__ -prune -exec rm -rf {} \;

maintainer-clean: distclean
	rm -rf .eggs .pytest_cache

.PHONY: all check dist docker-image clean distclean maintainer-clean
