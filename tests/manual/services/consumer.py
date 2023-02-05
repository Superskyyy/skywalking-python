"""
This module contains the Consumer part of the e2e tests.
consumer (FastAPI) -> consumer (AIOHTTP) -> provider (FastAPI + logging_with_exception)
"""
import threading
import time

import requests

# import threading
#
# import aiohttp
# import uvicorn
# from fastapi import FastAPI
# from fastapi import Request

from skywalking import agent, config

config.init(collector_address='localhost:11800', protocol='grpc', service_name='your not good service',
            service_instance='instance-01',
            experimental_fork_support=True, logging_level='DEBUG', log_reporter_active=True,
            meter_reporter_active=False,
            profiler_active=False)  # proflier and log reporter keep creating new threads

agent.start()

from skywalking.decorators import trace
import os
import logging

parent_pid = os.getpid()
pid = os.fork()

while True:
    time.sleep(5)


    @trace()
    def abc():
        if os.getpid() == parent_pid:
            logging.critical(f'logging critical test from parent process {os.getpid()}')
        else:
            logging.critical(f'logging critical test from child process {os.getpid()}')

        requests.get('http://localhost:9091/users')
    abc()

# pid = 999
# app = FastAPI()
#
#
# @app.get('/artist')
# @app.post('/artist')
# async def application(request: Request):
#
#
#     # pid greater than 0 represents
#     # the parent process
#     if pid > 0:
#         print("I am parent process:")
#         print("Process ID:", os.getpid())
#         print("Child's process ID:", pid)
#
#     # pid equal to 0 represents
#     # the created child process
#     else:
#         print("\nI am child process:")
#         print("Process ID:", os.getpid())
#         print("Parent's process ID:", os.getppid())
#     for thread in threading.enumerate():
#         print(thread.name)
#     return {'message': 'hello world'}
#
#
# if __name__ == '__main__':
#     # noinspection PyTypeChecker
#     uvicorn.run(app, host='0.0.0.0', port=9091 if pid > 0 else 9092)
