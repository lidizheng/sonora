import grpc
import pytest

import sonora.aio
from tests import helloworld_pb2, helloworld_pb2_grpc


@pytest.mark.asyncio
async def test_helloworld_sayhelloslowly_with(asgi_greeter_server):
    async with sonora.aio.insecure_web_channel(
        f"http://localhost:{asgi_greeter_server}"
    ) as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)

        for name in ("you", "world"):
            buffer = []

            request = helloworld_pb2.HelloRequest(name=name)

            with stub.SayHelloSlowly(request) as call:
                response = await call.read()

                while response:
                    buffer.append(response.message)
                    response = await call.read()

            message = "".join(buffer)
            assert message != name
            assert name in message


@pytest.mark.asyncio
async def test_helloworld_streamtimeout(asgi_greeter):
    request = helloworld_pb2.HelloRequest(name="client timeout")

    with pytest.raises(grpc.RpcError) as exc:
        with asgi_greeter.StreamTimeout(request, timeout=0) as call:
            response = await call.read()

            while response:
                await call.read()

    assert exc.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED


@pytest.mark.asyncio
async def test_helloworld_unarytimeout(asgi_greeter):
    request = helloworld_pb2.HelloRequest(name="client timeout")
    with pytest.raises(grpc.RpcError) as exc:
        await asgi_greeter.UnaryTimeout(request, timeout=0)
    assert exc.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED
