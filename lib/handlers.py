import asyncio
from functools import partial
import socketserver
import time


def get_handler(handler_cls, executor, action_cls, done_event):
    description = ' '.join([handler_cls.__name__, executor.__name__, action_cls.__name__])
    return partial(handler_cls, description, executor, action_cls, done_event)


class SomeMessagesNotProcessed(Exception):
    pass


class Tracker:
    first_message_time = None
    last_message_time = None
    messages_received = None
    messages_processed = None

    def __init__(self, description):
        self.description = description

    def received(self):
        self.messages_received += 1
        if not self.first_message_time:
            self.first_message_time = time.time()

    def processed(self):
        self.messages_processed += 1
        self.last_message_time = time.time()

    def check_finish(self):
        finished = self.messages_received == self.messages_processed
        if finished:
            self._print_time_taken()
        return finished

    def finish(self):
        finished = self.check_finish()
        if not finished:
            raise SomeMessagesNotProcessed

    def _print_time_taken(self):
        time_taken = self.last_message_time - self.first_message_time
        print(self.description, time_taken)


class SyncServerHandler(socketserver.BaseRequestHandler):
    messages_received = 0
    messages_processed = 0
    first_message_time = None
    last_message_time = None
    sender = None

    def __init__(self, description, executor, action_cls, done_event, *args, **kwargs):
        super(SyncServerHandler, self).__init__(*args, **kwargs)
        self.executor = executor
        self.done_event = done_event
        self.action = action_cls()
        self.sender = self.client_address[0]
        self.tracker = Tracker(description)

    def handle(self):
        data = None
        while data != '':
                data = self.request.recv(1024).strip()
                if data:
                    self.tracker.received()
                    self.executor(self.tracker.processed, self.action.do, data)

    def finish(self):
        self.tracker.finish()
        self.done_event.set()


async def async_server_sync_handler(description, executor, action_cls, done_event, reader, writer):
    tracker = Tracker(description)
    action = action_cls()
    addr = writer.get_extra_info('peername')
    data = None

    while data != b'':
        data = await reader.read(1024)
        if data:
            tracker.received()
            executor(tracker.processed, action.do, data)
    tracker.finish()
    done_event.set()


async def async_server_async_handler(description, executor, action, done_event, reader, writer):
    tracker = Tracker(description)
    addr = writer.get_extra_info('peername')
    data = None

    while data != b'':
        data = await reader.read(1024)
        if data:
            tracker.received()
            executor(tracker.processed, action.async_do, data)

    tracker.finish()
    done_event.set()


class AsyncProtocol(asyncio.Protocol):
    transport = None

    def __init__(self, description, executor, action, done_event):
        self.executor = executor
        self.action = action
        self.tracker = Tracker(description)
        self.done_event = done_event

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.tracker.check_finish()

    def data_received(self, data):
        self.tracker.received()
        self.executor(self.action_done, self.do_action, data)

    def action_done(self):
        self.tracker.processed()
        if self.transport.is_closing():
            finished = self.tracker.check_finish()
            if finished:
                self.done_event.set()

    def do_action(self, data):
        raise NotImplementedError


class AsyncProtocolSyncHandler(AsyncProtocol):
    def do_action(self, data):
        self.executor(self.action_done, self.action.do, data)


class AsyncProtocolTaskHandler(AsyncProtocol):
    def do_action(self, data):
        asyncio.create_task(self.executor(self.action_done, self.action.async_do, data))


sync_handlers = (SyncServerHandler,)
async_handlers = (async_server_async_handler, AsyncProtocolTaskHandler)
async_handlers_sync = (async_server_sync_handler, AsyncProtocolSyncHandler)
