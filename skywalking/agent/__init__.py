#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import atexit
import functools
import os
from queue import Queue, Full
from threading import Thread, Event
from typing import TYPE_CHECKING

from skywalking import config, plugins
from skywalking import loggings
from skywalking import profile
from skywalking import meter
from skywalking.agent.protocol import Protocol
from skywalking.command import command_service
from skywalking.loggings import logger
from skywalking.profile.profile_task import ProfileTask
from skywalking.profile.snapshot import TracingThreadSnapshot
from skywalking.protocol.logging.Logging_pb2 import LogData
from skywalking.protocol.language_agent.Meter_pb2 import MeterData

if TYPE_CHECKING:
    from skywalking.trace.context import Segment

__started = False
__protocol = None  # type: Protocol
__heartbeat_thread = __report_thread = __log_report_thread = __query_profile_thread = __command_dispatch_thread \
    = __send_profile_thread = __queue = __log_queue = __snapshot_queue = __meter_queue = __finished = None


def report_with_backoff(init_wait):
    """
    An exponential backoff for retrying reporters.
    """

    def backoff_decorator(func):
        @functools.wraps(func)
        def backoff_wrapper(*args, **kwargs):
            wait = base = init_wait
            while not __finished.is_set():
                try:
                    func(*args, **kwargs)
                    wait = base  # reset to base wait time on success
                except Exception:  # noqa
                    wait = min(60, wait * 2 or 1)  # double wait time with each consecutive error up to a maximum
                    logger.exception(f'Exception in reporter in pid {os.getpid()}, retry in {wait} seconds')

                __finished.wait(wait)
            logger.info('finished reporter thread')

        return backoff_wrapper

    return backoff_decorator


@report_with_backoff(init_wait=config.heartbeat_period)
def __heartbeat():
    __protocol.heartbeat()


@report_with_backoff(init_wait=0)
def __report_segment():
    if not __queue.empty():
        __protocol.report_segment(__queue)


@report_with_backoff(init_wait=0)
def __report_log():
    if not __log_queue.empty():
        __protocol.report_log(__log_queue)


@report_with_backoff(init_wait=config.meter_reporter_period)
def __report_meter():
    if not __meter_queue.empty():
        __protocol.report_meter(__meter_queue)


@report_with_backoff(init_wait=0.5)
def __send_profile_snapshot():
    if not __snapshot_queue.empty():
        __protocol.report_snapshot(__snapshot_queue)


@report_with_backoff(init_wait=config.get_profile_task_interval)
def __query_profile_command():
    __protocol.query_profile_commands()


def __command_dispatch():
    # command dispatch will stuck when there are no commands
    command_service.dispatch()


def __init_threading():
    global __heartbeat_thread, __report_thread, __log_report_thread, __query_profile_thread, \
        __command_dispatch_thread, __send_profile_thread, __queue, __log_queue, __snapshot_queue, __meter_queue, __finished

    __queue = Queue(maxsize=config.trace_reporter_max_buffer_size)
    __finished = Event()
    __heartbeat_thread = Thread(name='HeartbeatThread', target=__heartbeat, daemon=True)
    __report_thread = Thread(name='ReportThread', target=__report_segment, daemon=True)
    __command_dispatch_thread = Thread(name='CommandDispatchThread', target=__command_dispatch, daemon=True)

    __heartbeat_thread.start()
    __report_thread.start()
    __command_dispatch_thread.start()

    if config.meter_reporter_active:
        __meter_queue = Queue(maxsize=config.meter_reporter_max_buffer_size)
        __meter_report_thread = Thread(name='MeterReportThread', target=__report_meter, daemon=True)
        __meter_report_thread.start()

        if config.pvm_meter_reporter_active:
            from skywalking.meter.pvm.cpu_usage import CPUUsageDataSource
            from skywalking.meter.pvm.gc_data import GCDataSource
            from skywalking.meter.pvm.mem_usage import MEMUsageDataSource
            from skywalking.meter.pvm.thread_data import ThreadDataSource

            MEMUsageDataSource().registry()
            CPUUsageDataSource().registry()
            GCDataSource().registry()
            ThreadDataSource().registry()

    if config.log_reporter_active:
        __log_queue = Queue(maxsize=config.log_reporter_max_buffer_size)
        __log_report_thread = Thread(name='LogReportThread', target=__report_log, daemon=True)
        __log_report_thread.start()

    if config.profiler_active:
        __snapshot_queue = Queue(maxsize=config.profile_snapshot_transport_buffer_size)

        __query_profile_thread = Thread(name='QueryProfileCommandThread', target=__query_profile_command, daemon=True)
        __query_profile_thread.start()

        __send_profile_thread = Thread(name='SendProfileSnapShotThread', target=__send_profile_snapshot, daemon=True)
        __send_profile_thread.start()


def __init():
    global __protocol
    if config.protocol == 'grpc':
        from skywalking.agent.protocol.grpc import GrpcProtocol
        __protocol = GrpcProtocol()
    elif config.protocol == 'http':
        from skywalking.agent.protocol.http import HttpProtocol
        __protocol = HttpProtocol()
    elif config.protocol == 'kafka':
        from skywalking.agent.protocol.kafka import KafkaProtocol
        __protocol = KafkaProtocol()

    plugins.install()
    if config.log_reporter_active:  # todo - Add support for printing traceID/ context in logs
        from skywalking import log
        log.install()

    __init_threading()


def __fini():
    __protocol.report_segment(__queue, False)
    __queue.join()

    if config.log_reporter_active:
        __protocol.report_log(__log_queue, False)
        __log_queue.join()

    if config.profiler_active:
        __protocol.report_snapshot(__snapshot_queue, False)
        __snapshot_queue.join()

    __finished.set()


def start():
    global __started
    if __started:
        return
    __started = True

    flag = False
    try:
        from gevent import monkey
        flag = monkey.is_module_patched('socket')
    except ModuleNotFoundError:
        logger.debug("it was found that no gevent was used, if you don't use, please ignore.")
    if flag:
        import grpc.experimental.gevent as grpc_gevent
        grpc_gevent.init_gevent()

    loggings.init()
    config.finalize()
    profile.init()
    meter.init()

    __init()

    atexit.register(__fini)


def stop():
    atexit.unregister(__fini)
    __fini()


def started():
    return __started


def isfull():
    return __queue.full()


def archive(segment: 'Segment'):
    try:  # unlike checking __queue.full() then inserting, this is atomic
        __queue.put(segment, block=False)
    except Full:
        logger.warning('the queue is full, the segment will be abandoned')


def archive_log(log_data: 'LogData'):
    try:
        __log_queue.put(log_data, block=False)
    except Full:
        logger.warning('the queue is full, the log will be abandoned')


def archive_meter(meterdata: 'MeterData'):
    try:
        __meter_queue.put(meterdata, block=False)
    except Full:
        logger.warning('the queue is full, the meter will be abandoned')


def add_profiling_snapshot(snapshot: TracingThreadSnapshot):
    try:
        __snapshot_queue.put(snapshot)
    except Full:
        logger.warning('the snapshot queue is full, the snapshot will be abandoned')


def notify_profile_finish(task: ProfileTask):
    try:
        __protocol.notify_profile_task_finish(task)
    except Exception as e:
        logger.error(f'notify profile task finish to backend fail. {str(e)}')
