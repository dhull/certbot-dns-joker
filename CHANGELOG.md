# Changelog

## Version 1.2.0 &mdash; 2022-11-23

Rebuild for certbot-1.30.

## Version 1.1.0 &mdash; 2020-06-23

Previously certbot-dns-joker only allowed getting certificates at the root
level of the domain, so, for example, if you owned the domain "example.com"
you could get a certificate for "example.com" or "*.example.com".  Now you can
also get a certificate for a subdomain such as sub.example.com.  Since
certbot-dns-joker doesn't know how to determine what the root domain is for a
given subdomain you will have to specify the root domain in the credentials
file as "domain = ROOT_DOMAIN".

### New Features

* Allow getting certificates for subdomains.

## Version 1.0.0 &mdash; 2020-06-21

This is the initial public release.

### New Features

* Package as wheel (whl) and build Docker image.
* Add RPM packaging.
* Publish to PyPI.
* Create GitHub releases.
