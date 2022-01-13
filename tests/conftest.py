import asyncio

import pytest
from decouple import config
from pyrogram import Client

from tgintegration import BotController

import subprocess
import time
from src.definitions.definitions import SRC_DIR

#coverage run --omit="*/tests*" --source=. -m pytest tests/unit -s
#https://stackoverflow.com/questions/63623930/how-to-create-unit-test-for-a-python-telegram-bot
# Para o main, criar mock Updater e Context para testar o main como se fosse um unit test


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def event_loop():
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
async def controller(client, event_loop, run_bot):
    c = BotController(
        peer="@banger_music_bot",  # We are going to run tests on https://t.me/banger_music_bot
        client=client,
        max_wait=8,  # Maximum timeout for responses (optional)
        wait_consecutive=2,  # Minimum time to wait for more/consecutive messages (optional)
        raise_no_response=True,  # Raise `InvalidResponseError` when no response received (defaults to True)
        global_action_delay=2.5,  # Choosing a rather high delay so we can follow along in realtime (optional)
    )
    yield c
