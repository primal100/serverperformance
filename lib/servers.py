import asyncio
import threading
import socketserver

from lib.handlers import get_handler


class BaseServer:
    server = None

    def __init__(self, handler_cls, executor_cls, action_cls, stop_event, done_event, host="localhost", port=9999):
        self.stop_event = stop_event
        self.host = host
        self.port = port
        self.handler = get_handler(executor_cls, handler_cls, action_cls, done_event)

    def start_server(self):
        raise NotImplementedError

    def stop_server(self):
        raise NotImplementedError


class BaseSyncServer(BaseServer):
    server_cls = None

    def monitor_event(self):
        self.stop_event.wait()
        self.stop_server()

    def start_monitor_thread(self):
        thread = threading.Thread(target=self.monitor_event)
        thread.start()

    def start_server(self):
        self.start_monitor_thread()
        self.server = self.server_cls((self.host, self.port), self.handler)
        self.server.serve_forever()

    def stop_server(self):
        self.server.shutdown()


class TCPServer(BaseSyncServer, socketserver.TCPServer):
    server_cls = socketserver.TCPServer


class AsyncioCallbackServer(BaseServer):

    async def start_monitor_task(self):
        await asyncio.get_running_loop().run_in_executor(None, self.stop_event.wait())
        await self.stop_server()
        await self.server.wait_closed()

    async def start_server(self):
        await self.start_monitor_task()
        self.server = await asyncio.start_server(self.handler, host=self.host, port=self.port)

    async def stop_server(self):
        self.server.close()
        await self.server.wait_closed()


class AsyncioProtocolServer(AsyncioCallbackServer):

    async def start_server(self):
        await self.start_monitor_task()
        self.server = await asyncio.get_event_loop().create_server(self.handler, host=self.host, port=self.port)


sync_servers = (TCPServer,)
async_cb_servers = (AsyncioCallbackServer,)
async_protocol_servers = (AsyncioProtocolServer,)
