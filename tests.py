from lib.testcases import BaseTestCase
from lib.actions import actions
from lib.servers import sync_servers
from lib.executors import sync_executors
from lib.handlers import sync_handlers


class TestSyncServersSleeping(BaseTestCase):

    def run_server(self, s, h, e, a):
        from lib.actions import actions
        from lib.servers import sync_servers
        from lib.executors import sync_executors
        from lib.handlers import sync_handlers
        action_cls = actions[a]
        server_cls = sync_servers[a]
        executor_cls = sync_executors[a]
        handler_cls = sync_handlers[a]
        server_cls(handler_cls, executor_cls, action_cls, self.stop_event, self.done_event)



    def test_run(self):
        for s in range(0, len(sync_servers)):
            for h in range(0, len(sync_handlers)):
                for e in range(0, len(sync_executors)):
                    for a in range(0, len(actions)):
                        self.start_server_process(s, h, e, a)
                        self.run_client()
                        self.wait_done()
                        self.stop_server()

