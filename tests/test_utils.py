import logging
import os

from unittest import mock
from unittest.mock import patch
from requests import exceptions
from instance_billing_flavor_check import utils

FAKE_PROXY = {'http_proxy': 'foo', 'https_proxy': 'bar', 'no_proxy': 'foobar'}

@patch.dict(os.environ, FAKE_PROXY, clear=True)
def test_get_proxies():
    """Test proxy settings are the same as environment, if any."""
    assert not utils._get_proxies()


def test_get_proxies_no_proxy_env_no_proxy_file():
    """Test proxy value is the same as set on the proxy file."""
    with patch('builtins.open', create=True) as mock_open:
        mock_open.side_effect = FileNotFoundError('oh no')
        assert not utils._get_proxies()



def test_get_proxies_no_proxy_env_proxy_file(caplog):
    """Test proxy value is the same as set on the file."""
    with patch('builtins.open', create=True) as mock_open:
        proxy_content = """
        HTTP_PROXY="http://foo.com"
        HTTPS_PROXY="https://foo.com"
        NO_PROXY="localhost, 127.0.0.1"
        """
        with mock.patch(
            'builtins.open',
            mock.mock_open(read_data=proxy_content)
        ):
            assert utils._get_proxies() == {
                'http_proxy': 'http://foo.com',
                'https_proxy': 'https://foo.com',
                'no_proxy': 'localhost, 127.0.0.1'
            }
