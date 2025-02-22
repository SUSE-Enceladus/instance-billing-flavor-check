import os

from unittest import mock
from unittest.mock import patch
from instance_billing_flavor_check import utils

CACHE_FILE_PATH = '/tmp/instance-billing-flavor-check'
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


def test_check_payg_byos_no_network():
    """Check proper return when we do not have network access"""
    utils.has_ipv4_access = _no_ip
    utils.has_ipv6_access = _no_ip
    utils.CACHE_FILE_PATH = CACHE_FILE_PATH
    result = utils.check_payg_byos()
    assert(result[0] == 'BYOS')
    assert(result[1] == 12)
    assert(open(CACHE_FILE_PATH).read() == 'BYOS')
    os.unlink(CACHE_FILE_PATH)


@patch('instance_billing_flavor_check.utils.get_identifier')
@patch('instance_billing_flavor_check.utils.get_metadata')
def test_check_payg_byos_no_instance_data(
        mock_metadata, mock_identifier, caplog
):
    """Check proper return when there is no instance information"""
    utils.has_ipv4_access = _has_ip
    utils.has_ipv6_access = _no_ip
    utils.CACHE_FILE_PATH = CACHE_FILE_PATH
    mock_identifier.return_value = False
    mock_metadata.return_value = False
    result = utils.check_payg_byos()
    assert(result[0] == 'BYOS')
    assert(result[1] == 12)
    assert(open(CACHE_FILE_PATH).read() == 'BYOS')
    assert('No instance metadata and identifier' in caplog.text)
    os.unlink(CACHE_FILE_PATH)


@patch('instance_billing_flavor_check.utils.get_identifier')
@patch('instance_billing_flavor_check.utils.get_metadata')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
def test_check_payg_byos_no_server_ip(
        mock_rmt_ip, mock_metadata, mock_identifier, caplog
):
    """Check proper return when the update server claims to have no IP"""
    utils.has_ipv4_access = _no_ip
    utils.has_ipv6_access = _has_ip
    utils.CACHE_FILE_PATH = CACHE_FILE_PATH
    mock_identifier.return_value = True
    mock_metadata.return_value = True
    mock_rmt_ip.return_value = None
    result = utils.check_payg_byos()
    assert(result[0] == 'BYOS')
    assert(result[1] == 12)
    assert(open(CACHE_FILE_PATH).read() == 'BYOS')
    assert('Instance can be either' in caplog.text)
    os.unlink(CACHE_FILE_PATH)


@patch('instance_billing_flavor_check.utils.get_identifier')
@patch('instance_billing_flavor_check.utils.get_metadata')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
@patch('instance_billing_flavor_check.utils.make_request')
def test_check_payg_byos_is_payg(
        mock_request, mock_rmt_ip, mock_metadata, mock_identifier
):
    """Check proper return based on the update server status"""
    utils.has_ipv4_access = _no_ip
    utils.has_ipv6_access = _has_ip
    utils.CACHE_FILE_PATH = CACHE_FILE_PATH
    mock_identifier.return_value = True
    mock_metadata.return_value = True
    mock_rmt_ip.return_value = ['1.1.1.1']
    mock_request.return_value = 'PAYG'
    result = utils.check_payg_byos()
    assert(result[0] == 'PAYG')
    assert(result[1] == 10)
    assert(open(CACHE_FILE_PATH).read() == 'PAYG')
    os.unlink(CACHE_FILE_PATH)


@patch('instance_billing_flavor_check.utils.get_identifier')
@patch('instance_billing_flavor_check.utils.get_metadata')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
@patch('instance_billing_flavor_check.utils.make_request')
def test_check_payg_byos_is_byos(
        mock_request, mock_rmt_ip, mock_metadata, mock_identifier
):
    """Check proper return based on the update server status"""
    utils.has_ipv4_access = _no_ip
    utils.has_ipv6_access = _has_ip
    utils.CACHE_FILE_PATH = CACHE_FILE_PATH
    mock_identifier.return_value = True
    mock_metadata.return_value = True
    mock_rmt_ip.return_value = ['1.1.1.1']
    mock_request.return_value = 'BYOS'
    result = utils.check_payg_byos()
    assert(result[0] == 'BYOS')
    assert(result[1] == 11)
    assert(open(CACHE_FILE_PATH).read() == 'BYOS')
    os.unlink(CACHE_FILE_PATH)


@patch('instance_billing_flavor_check.utils.get_identifier')
@patch('instance_billing_flavor_check.utils.get_metadata')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
@patch('instance_billing_flavor_check.utils.make_request')
def test_check_payg_byos_use_cache(
        mock_request, mock_rmt_ip, mock_metadata, mock_identifier
):
    """Check proper return based on the update server status"""
    utils.has_ipv4_access = _no_ip
    utils.has_ipv6_access = _has_ip
    utils.CACHE_FILE_PATH = CACHE_FILE_PATH
    cf = open(CACHE_FILE_PATH, 'w')
    cf.write('PAYG')
    cf.close()
    mock_identifier.return_value = True
    mock_metadata.return_value = True
    mock_rmt_ip.return_value = ['1.1.1.1']
    mock_request.return_value = 'PAYG'
    result = utils.check_payg_byos()
    assert(result[0] == 'PAYG')
    assert(result[1] == 10)
    assert(open(CACHE_FILE_PATH).read() == 'PAYG')
    os.unlink(CACHE_FILE_PATH)

    
## Test helpers
def _no_ip():
    return False


def _has_ip():
    return True
