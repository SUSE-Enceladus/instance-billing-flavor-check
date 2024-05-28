# Copyright (c) 2024 SUSE Software Solutions Germany GmbH. All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

from pytest import raises
from unittest import mock
from unittest.mock import patch, Mock
from requests import exceptions
from instance_billing_flavor_check import utils

IPV4_ADDR = '203.0.113.1'
IPV6_ADDR = '2001:DB8::1'

@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv4(mock_request_get):
    """Test make request with IPV4_ADDR without issues."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'flavor': 'amazing flavor'}
    mock_request_get.return_value = response
    assert utils.make_request(IPV4_ADDR, 'foo', 'bar') == 'amazing flavor'
    mock_request_get.assert_called_once_with(
        'https://203.0.113.1/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )


@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv6(mock_request_get):
    """Test make request with IPv6 without issues."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'flavor': 'supa flavor'}
    mock_request_get.return_value = response
    assert utils.make_request(IPV6_ADDR, 'foo', 'bar') == 'supa flavor'
    mock_request_get.assert_called_once_with(
        'https://[2001:DB8::1]/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )

@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv6_http_error(mock_request_get, caplog):
    """Test make request with IPv6 when HTTP error exception."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'flavor': 'supa flavor'}
    mock_request_get.side_effect = exceptions.HTTPError('foo')
    assert utils.make_request(IPV6_ADDR, 'foo', 'bar') is None
    assert 'Http Error:foo' in caplog.text
    mock_request_get.assert_called_once_with(
        'https://[2001:DB8::1]/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )


@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv6_connection_error(mock_request_get, caplog):
    """Test make request with IPv6 when Connection error exception."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'flavor': 'supa flavor'}
    mock_request_get.side_effect = exceptions.ConnectionError('foo')
    assert utils.make_request(IPV6_ADDR, 'foo', 'bar') is None
    assert 'Error Connecting:foo' in caplog.text
    mock_request_get.assert_called_once_with(
        'https://[2001:DB8::1]/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )


@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv6_timeout_error(mock_request_get, caplog):
    """Test make request with IPv6 when Timeout error exception."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'flavor': 'supa flavor'}
    mock_request_get.side_effect = exceptions.Timeout('foo')
    assert utils.make_request(IPV6_ADDR, 'foo', 'bar') is None
    assert 'Timeout Error:foo' in caplog.text
    mock_request_get.assert_called_once_with(
        'https://[2001:DB8::1]/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )


@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv6_request_error(mock_request_get, caplog):
    """Test make request with IPv6 when Request error exception."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'flavor': 'supa flavor'}
    mock_request_get.side_effect = exceptions.RequestException('foo')
    assert utils.make_request(IPV6_ADDR, 'foo', 'bar') is None
    assert 'Request error:foo' in caplog.text
    mock_request_get.assert_called_once_with(
        'https://[2001:DB8::1]/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )


@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv6_unexpected_error(mock_request_get, caplog):
    """Test make request with IPv6 when Request error exception."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'flavor': 'supa flavor'}
    mock_request_get.side_effect = Exception('foo')
    assert utils.make_request(IPV6_ADDR, 'foo', 'bar') is None
    assert 'Unexpected error: foo' in caplog.text
    mock_request_get.assert_called_once_with(
        'https://[2001:DB8::1]/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )


@patch('instance_billing_flavor_check.utils.requests.get')
def test_make_request_ipv6_request_ok_wrong_status_code(
    mock_request_get,
    caplog
):
    """
    Test make request with IPv6 when request returns fine
    but wrong status code.
    """
    response = Mock()
    response.status_code = 404
    response.reason = 'oh well, this is odd but it is not found'
    mock_request_get.return_value = response
    assert utils.make_request(IPV6_ADDR, 'foo', 'bar') is None
    error_message = 'Request to check if instance is PAYG/BYOS failed: ' \
        'oh well, this is odd but it is not found'

    assert error_message in caplog.text
    mock_request_get.assert_called_once_with(
        'https://[2001:DB8::1]/api/instance/check',
        proxies=None,
        timeout=2,
        verify=False,
        params={'metadata': 'foo', 'identifier': 'bar'}
    )


def test_make_request_not_valid_ip(caplog):
    """
    Test make request with a not valid IP."""
    assert utils.make_request('foo', 'foo', 'bar') is None
    error_message = 'The RMT IP address foo is not valid.'
    assert error_message in caplog.text


@patch('instance_billing_flavor_check.utils.has_ipv6_access')
@patch('instance_billing_flavor_check.utils.configparser.ConfigParser.read')
def test_check_payg_byos_no_identifier(mock_configparser, mock_ipv6_access):
    mock_configparser.return_value = False
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '12'


@patch('instance_billing_flavor_check.utils.has_ipv6_access')
@patch('instance_billing_flavor_check.utils.get_metadata')
def test_check_payg_byos_no_instance_metadata(mock_get_metadata, mock_ipv6):
    mock_get_metadata.return_value = 'foo'
    file_mock = Mock()
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.side_effect = [
            FileNotFoundError, file_mock
        ]
        with raises(SystemExit):
            assert utils.check_payg_byos() is None


@patch('instance_billing_flavor_check.utils.has_ipv6_access')
@patch('instance_billing_flavor_check.command.Command.run')
@patch('instance_billing_flavor_check.utils.get_instance_data_command')
def test_check_payg_byos_no_command(mock_configparser, mock_popen, mock_ipv6):
    mock_process = Mock()
    mock_process.communicate = Mock(
        return_value=[str.encode(''), str.encode('')]
    )
    mock_process.returncode = 1
    mock_popen.return_value = mock_process
    mock_configparser.return_value = 'super cloud'
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '12'
    mock_popen.called_once_with(['super', 'cloud'])


@patch('instance_billing_flavor_check.utils.has_ipv6_access')
@patch('instance_billing_flavor_check.command.subprocess.Popen')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
@patch('instance_billing_flavor_check.utils.get_identifier')
@patch('instance_billing_flavor_check.utils.configparser.ConfigParser')
def test_check_payg_byos_no_rmt_ip_addr(
    mock_configparser, mock_get_id, mock_get_rmt_ip_addr,
    mock_popen, mock_ipv6_access
):
    mock_process = Mock()
    mock_process.communicate = Mock(
        return_value=[str.encode('stdout'), str.encode('')]
    )
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    data = """
    [instance]
    dataProvider = SUPER_CLOUD
    """
    mock_configparser.open.return_value = data.encode()
    mock_get_rmt_ip_addr.return_value = []
    mock_get_id.return_value = 'foo'
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '12'


@patch('instance_billing_flavor_check.utils.has_ipv6_access')
@patch('instance_billing_flavor_check.command.subprocess.Popen')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
@patch('instance_billing_flavor_check.utils.get_identifier')
@patch('instance_billing_flavor_check.utils.configparser.ConfigParser.read')
def test_check_payg_byos_no_region_srv_client_file(
    mock_configparser, mock_get_id, mock_get_rmt_ip_addr,
    mock_popen, mock_ipv6_access
):
    mock_process = Mock()
    mock_process.communicate = Mock(
        return_value=[str.encode('stdout'), str.encode('')]
    )
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    mock_configparser.return_value = 'data'
    mock_get_rmt_ip_addr.return_value = []
    mock_get_id.return_value = 'foo'
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '12'


def test_no_etc_hosts_file():
    file_mock = Mock()
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.side_effect = [
            FileNotFoundError, file_mock
        ]
        assert utils._get_ips_from_etc_hosts() is None


@patch('instance_billing_flavor_check.utils.ipaddress.ip_address')
def test_etc_hosts_file_wrong_ip(mock_ip_addr):
    mock_ip_addr.side_effect = ValueError('wrong ip!')
    assert utils._get_ips_from_etc_hosts() == []


def test_etc_hosts_file_valid_ip():
    foo = '1.1.1.1 susecloud.net'
    with patch('builtins.open', mock.mock_open(read_data=foo)):
        assert utils._get_ips_from_etc_hosts() == ['1.1.1.1']


@patch('instance_billing_flavor_check.utils.get_smt')
@patch('instance_billing_flavor_check.utils.has_ipv4_access')
@patch('instance_billing_flavor_check.utils.has_ipv6_access')
def test_get_ips_from_cloudregister_only_ipv6(
    mock_ipv6, mock_ipv4, mock_get_smt
):
    mock_smt = Mock()
    mock_smt.get_ipv6.return_value = IPV6_ADDR
    mock_get_smt.return_value = mock_smt
    mock_ipv6.return_value = True
    mock_ipv4.return_value = False
    assert utils._get_ips_from_cloudregister() == ['[{}]'.format(IPV6_ADDR)]


@patch('instance_billing_flavor_check.utils.get_smt')
@patch('instance_billing_flavor_check.utils.has_ipv4_access')
@patch('instance_billing_flavor_check.utils.has_ipv6_access')
def test_get_ips_from_cloudregister_only_ipv4(
    mock_ipv6, mock_ipv4, mock_get_smt
):
    mock_smt = Mock()
    mock_smt.get_ipv4.return_value = IPV4_ADDR
    mock_get_smt.return_value = mock_smt
    mock_ipv6.return_value = False
    mock_ipv4.return_value = True
    assert utils._get_ips_from_cloudregister() == [IPV4_ADDR]


@patch('instance_billing_flavor_check.utils.get_smt')
@patch('instance_billing_flavor_check.utils.has_ipv4_access')
@patch('instance_billing_flavor_check.utils.has_ipv6_access')
def test_get_ips_from_cloudregister_ipv6_and_ipv4(
    mock_ipv6, mock_ipv4, mock_get_smt
):
    mock_smt = Mock()
    mock_smt.get_ipv4.return_value = IPV4_ADDR
    mock_smt.get_ipv6.return_value = IPV6_ADDR
    mock_get_smt.return_value = mock_smt
    mock_ipv6.return_value = True
    mock_ipv4.return_value = True
    assert utils._get_ips_from_cloudregister() == [
        '[{}]'.format(IPV6_ADDR),
        IPV4_ADDR
    ]


@patch.dict('sys.modules', {'cloudregister': Mock()})
@patch('instance_billing_flavor_check.utils._get_ips_from_cloudregister')
@patch('instance_billing_flavor_check.utils._get_ips_from_etc_hosts')
def test_get_rmt_ip_addr_from_cloudregister(
    mock_ips_from_etc_hosts, mock_ips_from_cloudreg
):
    mock_ips_from_etc_hosts.return_value = None
    # sys.modules['cloudregister'] = Mock()
    mock_ips_from_cloudreg.return_value = ['1.1.1.1']
    assert utils.get_rmt_ip_addr() == ['1.1.1.1']


@patch.dict('sys.modules', {'cloudregister': Mock()})
@patch('instance_billing_flavor_check.utils._get_ips_from_cloudregister')
@patch('instance_billing_flavor_check.utils._get_ips_from_etc_hosts')
def test_get_rmt_ip_addr_no_ips(
    mock_ips_from_etc_hosts, mock_ips_from_cloudreg
):
    mock_ips_from_etc_hosts.return_value = None
    mock_ips_from_cloudreg.return_value = []
    assert utils.get_rmt_ip_addr() is None


@patch('instance_billing_flavor_check.utils.has_ipv6_access')
@patch('instance_billing_flavor_check.utils.make_request')
@patch('instance_billing_flavor_check.command.subprocess.Popen')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
@patch('instance_billing_flavor_check.utils.get_instance_data_command')
def test_check_payg_byos_no_flavor_found(
    mock_get_instance_data_command, mock_get_rmt_ip_addr,
    mock_popen, mock_make_request, mock_ipv6_access
):
    mock_process = Mock()
    mock_process.communicate = Mock(
        return_value=[str.encode('stdout'), str.encode('')]
    )
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    mock_get_instance_data_command.return_value = 'foo'
    mock_get_rmt_ip_addr.return_value = ['foo']
    mock_make_request.return_value = None
    mock_ipv6_access.return_value = True
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '12'


@patch('instance_billing_flavor_check.utils.has_ipv6_access')
@patch('instance_billing_flavor_check.utils.make_request')
@patch('instance_billing_flavor_check.command.subprocess.Popen')
@patch('instance_billing_flavor_check.utils.get_rmt_ip_addr')
@patch('instance_billing_flavor_check.utils.get_instance_data_command')
def test_check_payg_byos_PAYG_flavor_found(
    mock_get_instance_data_command, mock_get_rmt_ip_addr,
    mock_popen, mock_make_request, mock_has_ipv6_access
):
    mock_process = Mock()
    mock_process.communicate = Mock(
        return_value=[str.encode('stdout'), str.encode('')]
    )
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    mock_get_instance_data_command.return_value = 'foo'
    mock_get_rmt_ip_addr.return_value = ['foo']
    mock_make_request.return_value = 'PAYG'
    mock_has_ipv6_access.return_value = True
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '10'

    mock_make_request.mock_reset()
    mock_make_request.return_value = 'BYOS'
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '11'


@patch('instance_billing_flavor_check.utils.has_ipv4_access')
@patch('instance_billing_flavor_check.utils.has_ipv6_access')
def test_check_payg_byos_PAYG_no_network_access(
    mock_has_ipv6_access, mock_has_ipv4_access
):
    mock_has_ipv6_access.return_value = False
    mock_has_ipv4_access.return_value = False
    with raises(SystemExit) as cm:
        assert utils.check_payg_byos() is None
    assert str(cm.value) == '12'
