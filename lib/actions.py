import aiofile
import asyncio
import binascii
import os
from pathlib import Path
import time

chunk_length = 16
sleep_for = 0.001


def bytes_to_chunks(b):
    pos = 0
    while pos < len(b):
        newpos = pos + chunk_length
        chunk = b[pos:newpos]
        pos = newpos
        yield chunk


class Action:
    def do(self, data):
        for msg in bytes_to_chunks(data):
            self.do_one(msg)

    async def async_do(self, data):
        for msg in bytes_to_chunks(data):
            await self.async_do_one(msg)

    def do_one(self, data):
        raise NotImplementedError

    def async_do_one(self, data):
        raise NotImplementedError


class SleepAction(Action):
    def do_one(self, data):
        time.sleep(sleep_for)

    async def async_do_one(self, data):
        await asyncio.sleep(sleep_for)


class WriteFileAction(Action):
    base_dir = Path(__file__).parent.parent.joinpath('data')
    i = 0

    def __init__(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_file_path(self):
        filename = binascii.hexlify(os.urandom(8))
        file_path = self.base_dir.joinpath(filename)
        self.i += 1
        return file_path

    def do_one(self, data):
        filename = self.get_file_path()
        with open(filename, 'w') as f:
            f.write(data)

    async def async_do_one(self, data):
        filename = self.get_file_path()
        async with aiofile.AIOFile(str(filename), 'w') as f:
            await f.write(data)


actions = (SleepAction, WriteFileAction)