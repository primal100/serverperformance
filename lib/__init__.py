import asyncio
import os

if os.name=='linux':
    import uvloop
    loop_policy = uvloop.EventLoopPolicy
else:
    class WindowsEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
        def new_event_loop(self):
            return asyncio.ProactorEventLoop()
    loop_policy = WindowsEventLoopPolicy


def set_loop_policy():
    asyncio.set_event_loop_policy(loop_policy())
