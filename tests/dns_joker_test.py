"""Tests for certbot_dns_joker.dns_joker."""

import unittest

try:
    import mock
except ImportError: # pragma: no cover
    from unittest import mock # type: ignore
from requests.exceptions import HTTPError
import urllib.parse
import requests
import requests_mock

from certbot.compat import os
from certbot.errors import PluginError
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

FAKE_USERNAME = 'fake_username'
FAKE_PASSWORD = 'fake_password'
MOCK_ENDPOINT = 'mock://endpoint'

class AuthenticatorTest(test_util.TempDirTestCase,
                        dns_test_common.BaseAuthenticatorTest):

    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_joker.dns_joker import Authenticator

        path = os.path.join(self.tempdir, 'file.ini')
        dns_test_common.write({
            # 'certbot_dns_joker:dns_joker_username': FAKE_USERNAME,
            # 'certbot_dns_joker:dns_joker_password': FAKE_PASSWORD,
            'joker_username': FAKE_USERNAME,
            'joker_password': FAKE_PASSWORD,
        }, path)

        self.config = mock.MagicMock(joker_credentials=path,
                                     joker_propagation_seconds=0)  # don't wait during tests

        # self.auth = Authenticator(self.config, "certbot_dns_joker:dns_joker")
        self.auth = Authenticator(self.config, "joker")

        self.mock_client = mock.MagicMock()
        # _get_joker_client | pylint: disable=protected-access
        self.auth._get_joker_client = mock.MagicMock(return_value=self.mock_client)


    def test_perform(self):
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_txt_record(
                DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY
            )
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup(self):
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [
            mock.call.del_txt_record(
                DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY
            )
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)


class JokerClientTest(unittest.TestCase):
    record_name = "foo"
    record_content = "bar"
    record_ttl = 42

    def setUp(self):
        from certbot_dns_joker.dns_joker import _JokerClient

        self.client = _JokerClient(FAKE_USERNAME, FAKE_PASSWORD, self.record_ttl, endpoint=MOCK_ENDPOINT)

        self.adapter = requests_mock.Adapter()
        self.client.session.mount('mock://', self.adapter)

    def _register_response(self, response='good', additional_matcher=None, **kwargs):
        def add_matcher(request):
            data = urllib.parse.parse_qs(request.text)
            add_result = True
            if additional_matcher is not None:
                add_result = additional_matcher(request)

            return (
                ("username" in data and data["username"] == [FAKE_USERNAME]) and
                ("password" in data and data["password"] == [FAKE_PASSWORD]) and
                add_result
            )

        self.adapter.register_uri(
            requests_mock.ANY,
            MOCK_ENDPOINT,
            text=response,
            status_code=200 if response == 'good' else 400,
            additional_matcher=add_matcher,
            **kwargs
        )

    def test_add_txt_record(self):
        self._register_response()
        self.client.add_txt_record(
            DOMAIN, self.record_name, self.record_content
        )

    def test_add_txt_record_fail_to_authenticate(self):
        self._register_response(response='badauth')
        with self.assertRaises(PluginError) as context:
            self.client.add_txt_record(
                DOMAIN, self.record_name, self.record_content
            )


    def test_add_txt_record_fail_to_find_domain(self):
        self._register_response(response='nohost')
        with self.assertRaises(PluginError) as context:
            self.client.add_txt_record(
                DOMAIN, self.record_name, self.record_content
            )

    def test_del_txt_record(self):
        self._register_response()
        self.client.del_txt_record(
            DOMAIN, self.record_name, self.record_content
        )


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
