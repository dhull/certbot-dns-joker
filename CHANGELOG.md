# Changelog

## Version 2.1.0 &mdash; 2023-02-15

This is version 2.1.0 of certbot-dns-joker because the convention is now that
a Certbot plugin uses the same version number as the Certbot version it is
built against.  There are no major changes in this version of
certbot-dns-joker.

### New Features

* Updates for Certbot 2.1.0.
* As a Certbot 2.0.0 change, config variables and names no longer use the
  `certbot-dns-joker:` prefix.  If upgrading, see the [Upgrading from
  1.2.0](https://github.com/dhull/certbot-dns-joker/README.md#upgrading-from-120)
  section of the README.

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
