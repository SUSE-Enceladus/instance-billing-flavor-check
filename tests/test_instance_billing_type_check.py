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
