import pytest
from unittest import mock

import xjsonrpc
from xjsonrpc.client.integrations.pytest import PjRpcAiohttpMocker
from xjsonrpc.client.backend import aiohttp as aiohttp_client


async def test_using_fixture(xjsonrpc_aiohttp_mocker):
    client = aiohttp_client.Client('http://localhost/api/v1')

    xjsonrpc_aiohttp_mocker.add('http://localhost/api/v1', 'sum', result=2)
    result = await client.proxy.sum(1, 1)
    assert result == 2

    xjsonrpc_aiohttp_mocker.replace(
        'http://localhost/api/v1', 'sum', error=xjsonrpc.exc.JsonRpcError(code=1, message='error', data='oops'),
    )
    with pytest.raises(xjsonrpc.exc.JsonRpcError) as exc_info:
        await client.proxy.sum(a=1, b=1)

    assert exc_info.type is xjsonrpc.exc.JsonRpcError
    assert exc_info.value.code == 1
    assert exc_info.value.message == 'error'
    assert exc_info.value.data == 'oops'

    localhost_calls = xjsonrpc_aiohttp_mocker.calls['http://localhost/api/v1']
    assert localhost_calls[('2.0', 'sum')].call_count == 2
    assert localhost_calls[('2.0', 'sum')].mock_calls == [mock.call(1, 1), mock.call(a=1, b=1)]


async def test_using_resource_manager():
    client = aiohttp_client.Client('http://localhost/api/v1')

    with PjRpcAiohttpMocker() as mocker:
        mocker.add('http://localhost/api/v1', 'div', result=2)
        result = await client.proxy.div(4, 2)
        assert result == 2

        localhost_calls = mocker.calls['http://localhost/api/v1']
        assert localhost_calls[('2.0', 'div')].mock_calls == [mock.call(4, 2)]
