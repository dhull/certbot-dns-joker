"""DNS Authenticator for DNS servers with the Joker extension to the DynDNS API."""

import traceback
import sys
from pprint import pprint

import logging

import requests
import zope.interface
import re

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

    credentials_map = dict ()

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=120)
        add('credentials', help='Joker credentials INI file.', action='append')

    def more_info(self):  # pylint: disable=missing-function-docstring
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Joker v2 API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials', 'Joker credentials INI file',
            required_variables = {
                'username': 'domain-specific Joker dyndns username',
                'password': 'domain-specific Joker dyndns password',
                'domain':   'top-level domain for credentials',
            })

    def _perform(self, domain, validation_name, validation):
        self._get_joker_client(domain).add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_joker_client(domain).del_txt_record(domain, validation_name, validation)


    def _get_joker_client(self, default_domain):
        cc = self.credentials.for_domain(default_domain)
        try:
            return _JokerClient(cc.username(), cc.password(), cc.domain(), self.ttl)
        except:
            raise Exception(f'domain: {default_domain}: no credentials found. check configuration\n')

    def _configure_credentials(self, key, label, required_variables=None,
                               validator=None) -> 'MultiCredentialsConfiguration':

        def __validator(filename): # pylint: disable=unused-private-member
            configuration = CredentialsConfiguration(filename, self.dest)

            if required_variables:
                configuration.require(required_variables)

            if validator:
                validator(configuration)

        self._configure_file(key, label, __validator)

        credentials_configuration = MultiCredentialsConfiguration(self.conf(key), self.dest)
        if required_variables:
            for cc in credentials_configuration.domains():
              cc.require(required_variables)

        if validator:
            for cc in credentials_configuration.domains():
                validator()

        return credentials_configuration

    def _configure_file(self, key, label, validator=None):
        configured_value = self.conf(key)
        if not configured_value:
            new_value = self._prompt_for_file(label, validator)
            setattr(self.config, self.dest(key), [os.path.abspath(os.path.expanduser(new_value))])



class JokerCredentialsConfiguration(dns_common.CredentialsConfiguration):
    def __init__(self, filename, mapper=lambda x: x):
        super(JokerCredentialsConfiguration,self).__init__(filename, mapper)

    def username(self):
        return self.__get('username')

    def password(self):
        return self.__get('password')

    def domain(self):
        return self.__get('domain')

    def __get(self, var):
        return self.confobj [self.mapper(var)]

class MultiCredentialsConfiguration():
    def __init__(self, filenames, mapper=lambda x: x):
        self.creds_for = dict ()
        t = type(filenames)
        if type(filenames) == type(""):
            filenames = [ filenames ]
        for f in filenames:
            cc = JokerCredentialsConfiguration(f, mapper)
            self.creds_for [cc.confobj[mapper('domain')]] = cc

    def domains(self):
        return self.creds_for.values()

    def for_domain(self, domain):
        if domain in self.creds_for:
            return self.creds_for[domain]
        for name in self.creds_for.keys():
            m = re.compile(".*\." + name + "")
            if m.match(domain) != None:
                return self.creds_for [name]



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
