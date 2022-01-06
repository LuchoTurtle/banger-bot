import pytest
import asyncio
from tgintegration import Response


# Mark these tests as async for PyTest
pytestmark = pytest.mark.asyncio


async def test_ping(event_loop, controller, client):
    print("Clearing chat to start with a blank screen...")
    await controller.clear_chat()

    print("Sending /start and waiting for exactly 3 messages...")
    async with controller.collect(count=1) as response:  # type: Response
        await controller.send_command("/start ")

    assert response.num_messages == 1



