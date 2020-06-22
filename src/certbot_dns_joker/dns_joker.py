"""DNS Authenticator for DNS servers with the Joker extension to the DynDNS API."""
import logging

import requests
import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

JOKER_ENDPOINT = 'https://svc.joker.com/nic/replace'


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Joker.

    This Authenticator uses the Joker DynDNS API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Joker for DNS).'
    ttl = 60

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=120)
        add('credentials', help='Joker credentials INI file.')

    def more_info(self):  # pylint: disable=missing-function-docstring
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Joker v2 API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials', 'Joker credentials INI file',
            required_variables = {
                'username': 'domain-specific Joker dyndns username',
                'password': 'domain-specific Joker dyndns password',
                # 'domain': 'top-level domain for credentials',
            })

    def _perform(self, domain, validation_name, validation):
        self._get_joker_client(domain).add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_joker_client(domain).del_txt_record(domain, validation_name, validation)

    def _get_joker_client(self, default_domain):
        username = self.credentials.conf('username')
        password = self.credentials.conf('password')
        domain = self.credentials.conf('domain')
        if not domain:
            domain = default_domain
        return _JokerClient(username, password, domain, self.ttl)


class _JokerClient(object):
    """
    Encapsulates all communication with the Joker.
    """

    # These are the error codes documented at https://help.dyn.com/remote-access-api/return-codes/
    error = {
       'badauth'  : 'Bad authorization (username or password)',
       'badsys'   : 'The system parameter given was not valid',

       'notfqdn'  : 'A Fully-Qualified Domain Name was not provided',
       'nohost'   : 'The hostname specified does not exist in the database',
       '!yours'   : 'The hostname specified exists, but not under the username currently being used',
       '!donator' : 'The offline setting was set, when the user is not a donator',
       '!active'  : 'The hostname specified is in a Custom DNS domain which has not yet been activated.',
       'abuse'    : 'The hostname specified is blocked for abuse; you should receive an email notification '
                     'which provides an unblock request link.  More info can be found on '
                     'https://www.dyndns.com/support/abuse.html',

       'numhost'  : 'System error: Too many or too few hosts found. Contact support@dyndns.org',
       'dnserr'   : 'System error: DNS error encountered. Contact support@dyndns.org',

       'nochg'    : 'No update required; unnecessary attempts to change to the current address are considered abusive',
    }

    def __init__(self, username, password, domain, ttl, endpoint=JOKER_ENDPOINT):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.domain = domain
        self.ttl = ttl
        self.session = requests.Session()

    def add_txt_record(self, cert_domain, record_name, record_content):
        # Documentation for the Joker TXT record API is here:
        # https://joker.com/faq/content/6/496/en/let_s-encrypt-support.html

        # print(f'ADD domain:{cert_domain} record_name:{record_name} endpoint:{self.endpoint}')

        # Joker adds the domain to the end of the label of the TXT record that
        # it creates, but the record_name that certbot passed us already has
        # it so we need to remove it before calling the Joker API.
        dotdomain = '.' + self.domain
        if record_name.endswith(dotdomain):
            record_name = record_name[0:-len(dotdomain)]

        r = self.session.post(
            self.endpoint,
            data = {
                'username': self.username,
                'password': self.password,
                'zone': self.domain,
                'label': record_name,
                'type': 'TXT',
                'value': record_content,
                'ttl': self.ttl,
            })

        # print(f'ADD {r} {r.text}\n  REQ URL: {r.request.url}\n  REQ BODY: {r.request.body}\n')

        if r.status_code >= 300:
            self._handle_http_error(r.text, record_name, self.domain)

    def del_txt_record(self, domain, record_name, record_content):
        self.add_txt_record(domain, record_name, '')

    def _handle_http_error(self, error, record_name, domain_name):
        hint = self.error.get(error)
        raise errors.PluginError('Error setting {0} TXT record for {1}: {2}.{3}'
                                 .format(record_name, domain_name, error,
                                         ' ({0})'.format(hint) if hint else ''))
