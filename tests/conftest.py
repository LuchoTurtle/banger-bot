import asyncio

import pytest
from decouple import config
from pyrogram import Client

from tgintegration import BotController

import subprocess
import time
from definitions.definitions import SRC_DIR


@pytest.fixture(scope="session", autouse=True)
def run_bot():
    print("Starting bot...")
    ds_proc = subprocess.Popen(
        [
            "python",
            str(SRC_DIR + "main.py"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Give the bot time to start
    time.sleep(2)

    yield ds_proc

    # Shut it down at the end of the pytest session
    ds_proc.terminate()


@pytest.fixture(scope="session", autouse=True)
def event_loop(request):
    """ Create an instance of the default event loop for the session and boots up bot """
    loop = asyncio.get_event_loop_policy().new_event_loop()

    yield loop

    # Teardown
    loop.close()


@pytest.fixture(scope="session")
async def client() -> Client:
    client = Client(
        "banger_bot_test",
        api_id=config("TEST_API_ID"),
        api_hash=config("TEST_API_HASH")
    )
    await client.start()
    yield client

    # Teardown
    await client.stop()


@pytest.fixture(scope="module")
async def controller(client):
    c = BotController(
        peer="@banger_music_bot",  # We are going to run tests on https://t.me/banger_music_bot
        client=client,
        max_wait=8,  # Maximum timeout for responses (optional)
        wait_consecutive=2,  # Minimum time to wait for more/consecutive messages (optional)
        raise_no_response=True,  # Raise `InvalidResponseError` when no response received (defaults to True)
        global_action_delay=2.5,  # Choosing a rather high delay so we can follow along in realtime (optional)
    )
    yield c
