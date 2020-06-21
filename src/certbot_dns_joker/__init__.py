"""
The `~certbot_dns_joker.dns_joker` plugin automates the process of
completing a ``dns-01`` challenge (`~acme.challenges.DNS01`) by creating, and
subsequently removing, TXT records using the Joker DynDNS API.


Named Arguments
---------------

========================================  =====================================
``--dns-joker-credentials``               Joker credentials_ INI file.
                                          (Required)
``--dns-joker-propagation-seconds``       The number of seconds to wait for DNS
                                          to propagate before asking the ACME
                                          server to verify the DNS record.
                                          (Default: 120)
========================================  =====================================


Credentials
-----------

Use of this plugin requires a configuration file containing Joker DynDNS API
credentials, obtained from your Joker account.
`https://joker.com/faq/content/6/496/en/let_s-encrypt-support.html`_.

https://configobj.readthedocs.io/en/latest/configobj.html

.. code-block:: ini
   :name: credentials.ini
   :caption: Example credentials file:

   # Joker DynDNS API credentials used by Certbot
   username = USERNAME
   password = PASSWORD

The path to this file can be provided interactively or using the
``--dns-joker-credentials`` command-line argument. Certbot records the path
to this file for use during renewal, but does not store the file's contents.

.. caution::
   You should protect these API credentials as you would the password to your
   Joker account. Users who can read this file can use these credentials
   to issue arbitrary API calls on your behalf. Users who can cause Certbot to
   run using these credentials can complete a ``dns-01`` challenge to acquire
   new certificates or revoke existing certificates for associated domains,
   even if those domains aren't being managed by this server.

Certbot will emit a warning if it detects that the credentials file can be
accessed by other users on your system. The warning reads "Unsafe permissions
on credentials configuration file", followed by the path to the credentials
file. This warning will be emitted each time Certbot uses the credentials file,
including for renewal, and cannot be silenced except by addressing the issue
(e.g., by using a command like ``chmod 600`` to restrict access to the file).


Examples
--------

.. code-block:: bash
   :caption: To acquire a certificate for ``example.com``

   certbot certonly \\
     --authenticator certbot-dns-joker:dns-joker \\
     --certbot-dns-joker:dns-joker-credentials ~/.secrets/certbot/example.com.ini \\
     -d example.com

.. code-block:: bash
   :caption: To acquire a single certificate for both ``example.com`` and
             ``www.example.com``

   certbot certonly \\
     --authenticator certbot-dns-joker:dns-joker \\
     --certbot-dns-joker:dns-joker-credentials ~/.secrets/certbot/example.com.ini \\
     -d example.com \\
     -d www.example.com

.. code-block:: bash
   :caption: To acquire a certificate for ``example.com``, waiting 60 seconds
             for DNS propagation

   certbot certonly \\
     --authenticator certbot-dns-joker:dns-joker \\
     --certbot-dns-joker:dns-joker-credentials ~/.secrets/certbot/example.com.ini \\
     --certbot-dns-joker:dns-joker-propagation-seconds 60 \\
     -d example.com

"""

# The following lines are extracted so they must be of the form:
# __KEY__ = "VALUE"

__version__ = "1.0.0"

__title__ = "certbot-dns-joker"
__description__ = "Joker DNS Authenticator plugin for Certbot"
__url__ = "https://github.com/dhull/certbot-dns-joker"
__doc__ = __description__ + " <" + __url__ + ">"

__author__ = "David Hull"
__email__ = "github@davidhull.org"
__issue_tracker__ = 'https://github.com/dhull/certbot-dns-joker/issues'

__license__ = "Apache 2.0"
__copyright__ = "Copyright 2020 David Hull"
