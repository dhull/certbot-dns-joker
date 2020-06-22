<!-- -*- mode:gfm -*- github-flavored markdown -->

# certbot-dns-joker

Certbot DNS Authenticator plugin for [Joker](https://joker.com/).

This [Certbot](https://certbot.eff.org/docs/index.html) plugin automates the
process of completing a `dns-01` by creating (and removing) TXT records using
the [Joker TXT record
API](https://joker.com/faq/content/6/496/en/let_s-encrypt-support.html).

## Configuring Joker

For each of your domains hosted using the Joker DNS server that would would
like to obtain certificates for you must enable Dynamic DNS for the domain in
the Joker web console.  Do this by visiting your [Joker
Dashboard](https://joker.com/user/dashboard), clicking the "DNS" action for
the domain you want to enable Dynamic DNS for, then ensuring that the "Dynamic
DNS active" slider is turned on.  A dialog should appear with the DynDNS
username and password for that domain.  These will be used in the credentials
file described below.

## Installation

``` bash
pip install certbot-dns-joker
```

## Certbot Arguments

To use Joker DNS authentication, pass the following arguments on certbot's command line:

| Option | Description |
| --- | --- |
| `--authenticator certbot-dns-joker:dns-joker` | Select the Joker authenticator plugin. (required) |
| `--certbot-dns-joker:dns-joker-credentials` _credentials_file_ | Full path to config file containing domain credentials. |
| `--certbot-dns-joker:dns-joker-propagation-seconds` _delay_ | Delay between setting DNS TXT record and asking the ACME server to verify it. Default: 120 |

If you don't supply the credentials file on the certbot command line you will
be prompted for its location.

## Credentials

You need to create a configuration file on your system (for example
`/etc/letsencrypt/secrets/DOMAIN.ini`) that contains the per-domain secrets
that you obtained when you enabled DynDNS for your domain.

``` plain
certbot_dns_joker:dns_joker_username = USERNAME
certbot_dns_joker:dns_joker_password = PASSWORD
```

## Example

``` bash
certbot certonly \
  --authenticator certbot-dns-joker:dns-joker \
  --certbot-dns-joker:dns-joker-credentials /etc/letsencrypt/secrets/example.com.ini \
  -d example.com -d '*.example.com'
```

## Alternate Deployment Methods

### PyPI

This project has a PyPI page at <https://pypi.org/project/certbot-dns-joker/>.

### RPM

I have built an RPM for CentOS 8, which is the platform I use.  The Makefile
has an `rpm` target that builds the RPM, but this has only been tested on
CentOS 8.  In addition, the GitHub release contains an SRPM from which is
should be possible to build a new RPM on other RPM-based Linux distributions,
but again I have not tested this.

### Docker

The Makefile has a `docker-image` target to create a certbot docker image with
the certbot-dns-joker plugin installed.  In addition if you set the
DOCKER_OTHER_PLUGINS makefile variable to a (space-separated) list of plugins
those plugins will also be installed.

Once the docker image is built you can run it with a command such as the
following.

``` bash
docker run --rm \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/log/letsencrypt:/var/log/letsencrypt \
  --cap-drop=all \
  certbot-joker \
  certonly \
  --authenticator certbot-dns-joker:dns-joker \
  --certbot-dns-joker:dns-joker-propagation-seconds 900 \
  --certbot-dns-joker:dns-joker-credentials /etc/letsencrypt/secrets/example.com.ini \
  --no-self-upgrade \
  --keep-until-expiring --non-interactive --expand \
  --server https://acme-v02.api.letsencrypt.org/directory \
  -d example.com -d '*.example.com'
```

Then you can run a command such as the following from cron to renew your
certificates.

``` bash
docker run --rm \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/log/letsencrypt:/var/log/letsencrypt \
  --cap-drop=all \
  certbot-joker \
  renew
```

Note that plugins that attempt to do operations outside of the container (such
as the apache plugin, which wants to run apachectl) will fail.

## Acknowledgments

This plugin is based in large part on Matthias Bilger's
[certbot-dns-ispconfig](https://github.com/m42e/certbot-dns-ispconfig) plugin
and the certbot-dns-dnsimple plugin.
