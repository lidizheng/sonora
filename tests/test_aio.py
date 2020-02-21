import grpc
import pytest

import sonora.aio
from tests import helloworld_pb2, helloworld_pb2_grpc


@pytest.mark.asyncio
async def test_helloworld_sayhelloslowly_with(asgi_grpc_server):
    async with sonora.aio.insecure_web_channel(
        f"http://localhost:{asgi_grpc_server}"
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
async def test_helloworld_sayhelloslowly_with_timeout(asgi_grpc_server):
    async with sonora.aio.insecure_web_channel(
        f"http://localhost:{asgi_grpc_server}"
    ) as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)

        request = helloworld_pb2.HelloRequest(name="timeout")

        with pytest.raises(grpc.RpcError) as exc:
            with stub.SayHelloSlowly(request, timeout=0.0000001) as call:
                response = await call.read()

                while response:
                    await call.read()

        assert exc.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED