import asyncio
import os
from concurrent import futures

thread_executor = futures.ThreadPoolExecutor()
process_executor = futures.ProcessPoolExecutor()


def run(cb, func, *args):
    func(*args)
    cb()


def run_in_thread(cb, func, *args):
    future = thread_executor.submit(func, *args)
    future.add_done_callback(cb)


def run_in_process(cb, func, *args):
    future = process_executor.submit(func, *args)
    future.add_done_callback(cb)


async def async_task(cb, coro):
    await coro
    cb()


def async_run_task(cb, func, *args):
    asyncio.create_task(async_task(cb, func(*args)))


async def async_run_sync(cb, func, *args):
    func(*args)
    cb()


async def async_run_in_thread(cb, func, *args):
    await asyncio.get_event_loop().run_in_executor(thread_executor, func, *args)
    cb()


async def async_run_in_process(cb, func, *args):
    await asyncio.get_event_loop().run_in_executor(process_executor, func, *args)
    cb()


if os.name == 'posix':
    sync_executors = (run, run_in_thread, run_in_process)
    coro_executors = (async_run_task,)
    asyncio_sync_executors = (async_run_sync, async_run_in_thread, async_run_in_process)
else:
    sync_executors = (run, run_in_thread, run_in_process)
    coro_executors = (async_run_task,)
    asyncio_sync_executors = (async_run_sync, async_run_in_thread, async_run_in_process)


