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
"""
This module holds all the configuration options for the agent. The options are loaded from both environment variables and
through code level, default values are provided for each option.

The environment variables must be named as `SW_AGENT_<option_variable>`.

To contributors: When adding an new configuration option, please preceed the option with a comment block like this:
# This option does bla bla
# could be multiple lines

The comments along with each option will be used to generate the documentation for the agent, you don't need to modify
any documentation to reflect changes here, just make sure to run `make doc-gen` to generate the documentation.
"""

import os
import re
import uuid

from typing import List, Pattern

RE_IGNORE_PATH: Pattern = re.compile('^$')
RE_HTTP_IGNORE_METHOD: Pattern = RE_IGNORE_PATH

options = None  # here to include 'options' in globals
options = globals().copy()
# THIS MUST PRECEDE DIRECTLY BEFORE LIST OF CONFIG OPTIONS!

# BEGIN: Agent Core Configuration Options
# The name of the Python service
service_name: str = os.getenv('SW_AGENT_SERVICE_NAME') or 'Python Service Name'
# The name of the Python service instance
service_instance: str = os.getenv('SW_AGENT_SERVICE_INSTANCE') or str(uuid.uuid1()).replace('-', '')
# The agent will report service instance properties every
# `factor * heartbeat period` seconds default: 10*30 = 300 seconds
service_instance_property_report_factor = int(os.getenv('SW_AGENT_SERVICE_INSTANCE_PROPERTY_REPORT_FACTOR', '10'))
# The agent will try to restart itself in any os.fork()-ed child process. Important note: it's not suitable for
# large numbered, short-lived processes such as multiprocessing.Pool, as each one will introduce overhead and create
# numerous instances in SkyWalking dashboard in format of `service_instance-child-<pid>`
experimental_fork_support: bool = os.getenv('SW_AGENT_EXPERIMENTAL_FORK_SUPPORT', '').lower() == 'true'
# The agent will exchange heartbeat message with SkyWalking OAP backend every `period` seconds
heartbeat_period: int = int(os.getenv('SW_AGENT_HEARTBEAT_PERIOD', '30'))
# DANGEROUS - This option controls the interval of each bulk report from telemetry data queues
# Do not modify unless you have evaluated its impact given your service load. 
queue_timeout: int = int(os.getenv('SW_AGENT_QUEUE_TIMEOUT', '1'))
# The agent namespace of the Python service
namespace: str = os.getenv('SW_AGENT_NAMESPACE', '')
# The backend OAP server address
collector_address: str = os.getenv('SW_AGENT_COLLECTOR_ADDRESS') or '127.0.0.1:11800'
# A list of host/port pairs to use for establishing the initial connection to the Kafka cluster. It is in the form
# host1:port1,host2:port2,...
kafka_bootstrap_servers: str = os.getenv('SW_AGENT_KAFKA_BOOTSTRAP_SERVERS') or 'localhost:9092'
# Specifying Kafka topic name for service instance reporting and registering.
kafka_topic_management: str = os.getenv('SW_AGENT_KAFKA_TOPIC_MANAGEMENT') or 'skywalking-managements'
# Specifying Kafka topic name for Tracing data.
kafka_topic_segment: str = os.getenv('SW_AGENT_KAFKA_TOPIC_SEGMENT') or 'skywalking-segments'
# Specifying Kafka topic name for Log data.
kafka_topic_log: str = os.getenv('SW_AGENT_KAFKA_TOPIC_LOG') or 'skywalking-logs'
# Specifying Kafka topic name for Meter data.
kafka_topic_meter: str = os.getenv('SW_AGENT_KAFKA_TOPIC_METER') or 'skywalking-meters'
# The configs to init KafkaProducer, supports the basic arguments (whose type is either `str`, `bool`, or `int`) listed 
# [here](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html#kafka.KafkaProducer)
# This config only works from environment variables, value should be passed by SW_AGENT_KAFKA_REPORTER_CONFIG_<KEY_NAME> 
kafka_reporter_config_key: str = os.getenv('SW_AGENT_KAFKA_REPORTER_CONFIG_<KEY_NAME>', '')
# Use TLS for communication with server (no cert required)
force_tls: bool = os.getenv('SW_AGENT_FORCE_TLS', '').lower() == 'true'
# The protocol to communicate with the backend OAP, `http`, `grpc` or `kafka`, **we highly suggest using `grpc` in
# production as it's well optimized than `http`**. The `kafka` protocol provides an alternative way to submit data to
# the backend.
protocol: str = (os.getenv('SW_AGENT_PROTOCOL') or 'grpc').lower()
# The authentication token to verify that the agent is trusted by the backend OAP, as for how to configure the
# backend, refer to [the yaml](https://github.com/apache/skywalking/blob/4f0f39ffccdc9b41049903cc540b8904f7c9728e/oap
# -server/server-bootstrap/src/main/resources/application.yml#L155-L158).
authentication: str = os.getenv('SW_AGENT_AUTHENTICATION', '')
# The logging level, could be one of `CRITICAL`, `FATAL`, `ERROR`, `WARN`(`WARNING`), `INFO`, `DEBUG`
logging_level: str = os.getenv('SW_AGENT_LOGGING_LEVEL') or 'INFO'
# The name patterns in CSV pattern, plugins whose name matches one of the pattern won't be installed
disable_plugins: List[str] = (os.getenv('SW_AGENT_DISABLE_PLUGINS') or '').split(',')
# The maximum queue backlog size for sending the segment data to backend, segments beyond this are silently dropped
max_buffer_size: int = int(os.getenv('SW_AGENT_MAX_BUFFER_SIZE', '10000'))
# You can setup multiple URL path patterns, The endpoints match these patterns wouldn't be traced. the current
# matching rules follow Ant Path match style , like /path/*, /path/**, /path/?.
trace_ignore_path: str = os.getenv('SW_AGENT_TRACE_IGNORE_PATH') or ''
# If the operation name of the first span is included in this set, this segment should be ignored.
ignore_suffix: str = os.getenv('SW_AGENT_IGNORE_SUFFIX') or '.jpg,.jpeg,.js,.css,.png,.bmp,.gif,.ico,.mp3,' \
                                                            '.mp4,.html,.svg '
# Max element count of the correlation context.
correlation_element_max_number: int = int(os.getenv('SW_AGENT_CORRELATION_ELEMENT_MAX_NUMBER') or '3')
# Max value length of correlation context element.
correlation_value_max_length: int = int(os.getenv('SW_AGENT_CORRELATION_VALUE_MAX_LENGTH') or '128')

# BEGIN: SW_PYTHON Auto Instrumentation CLI
# Special: can only be passed via environment. This config controls the child process agent bootstrap behavior in
# `sw-python` CLI, if set to `False`, a valid child process will not boot up a SkyWalking Agent. Please refer to the [
# CLI Guide](CLI.md) for details.
sw_python_bootstrap_propagate = os.getenv('SW_AGENT_SW_PYTHON_BOOTSTRAP_PROPAGATE', '').lower() == 'true'

# BEGIN: Profiling configurations
# If `True`, Python agent will enable profile when user create a new profile task. Otherwise disable profile.
profiler_active: bool = os.getenv('SW_AGENT_PROFILER_ACTIVE', '').lower() != 'false'
# The number of seconds between two profile task query.
get_profile_task_interval: int = int(os.getenv('SW_AGENT_GET_PROFILE_TASK_INTERVAL') or '20')
# The number of parallel monitor segment count.
profile_max_parallel: int = int(os.getenv('SW_AGENT_PROFILE_MAX_PARALLEL') or '5')
# The maximum monitor segment time(minutes), if current segment monitor time out of limit, then stop it.
profile_duration: int = int(os.getenv('SW_AGENT_PROFILE_DURATION') or '10')
# The number of max dump thread stack depth
profile_dump_max_stack_depth: int = int(os.getenv('SW_AGENT_PROFILE_DUMP_MAX_STACK_DEPTH') or '500')
# The number of snapshot transport to backend buffer size
profile_snapshot_transport_buffer_size: int = int(os.getenv('SW_AGENT_PROFILE_SNAPSHOT_TRANSPORT_BUFFER_SIZE') or '50')

# BEGIN: Log reporter configurations
# If `True`, Python agent will report collected logs to the OAP or Satellite. Otherwise, it disables the feature.
log_reporter_active: bool = os.getenv('SW_AGENT_LOG_REPORTER_ACTIVE', '').lower() != 'false'
# If `True`, Python agent will filter out HTTP basic auth information from log records. Otherwise, it disables the
# feature due to potential performance impact brought by regular expression
log_reporter_safe_mode: bool = os.getenv('SW_AGENT_LOG_REPORTER_SAFE_MODE', '').lower() == 'true'
# The maximum queue backlog size for sending log data to backend, logs beyond this are silently dropped.
log_reporter_max_buffer_size: int = int(os.getenv('SW_AGENT_LOG_REPORTER_MAX_BUFFER_SIZE') or '10000')
# This config specifies the logger levels of concern, any logs with a level below the config will be ignored.
log_reporter_level: str = os.getenv('SW_AGENT_LOG_REPORTER_LEVEL') or 'WARNING'
# This config customizes whether to ignore the application-defined logger filters, if `True`, all logs are reported
# disregarding any filter rules.
log_reporter_ignore_filter: bool = os.getenv('SW_AGENT_LOG_REPORTER_IGNORE_FILTER', '').lower() == 'true'
# If `True`, the log reporter will transmit the logs as formatted. Otherwise, puts logRecord.msg and logRecord.args
# into message content and tags(`argument.n`), respectively. Along with an `exception` tag if an exception was raised.
log_reporter_formatted: bool = os.getenv('SW_AGENT_LOG_REPORTER_FORMATTED', '').lower() != 'false'
# The log reporter formats the logRecord message based on the layout given.
log_reporter_layout: str = os.getenv('SW_AGENT_LOG_REPORTER_LAYOUT') or \
                           '%(asctime)s [%(threadName)s] %(levelname)s %(name)s - %(message)s'
# This configuration is shared by log reporter and tracer
# This config limits agent to report up to `limit` stacktrace, please refer to [Python traceback](
# https://docs.python.org/3/library/traceback.html#traceback.print_tb) for more explanations.
cause_exception_depth: int = int(os.getenv('SW_AGENT_CAUSE_EXCEPTION_DEPTH') or '10')

# BEGIN: Meter reporter configurations
# If `True`, Python agent will report collected meters to the OAP or Satellite. Otherwise, it disables the feature.
meter_reporter_active: bool = os.getenv('SW_AGENT_METER_REPORTER_ACTIVE', '').lower() != 'false'
# The maximum queue backlog size for sending meter data to backend, meters beyond this are silently dropped.
meter_reporter_max_buffer_size: int = int(os.getenv('SW_AGENT_METER_REPORTER_MAX_BUFFER_SIZE') or '10000')
# The interval in seconds between each meter data report
meter_reporter_period: int = int(os.getenv('SW_AGENT_METER_REPORTER_PERIOD') or '20')
# If `True`, Python agent will report collected Python Virtual Machine (PVM) meters to the OAP or Satellite.
# Otherwise, it disables the feature.
pvm_meter_reporter_active: bool = os.getenv('SW_AGENT_PVM_METER_REPORTER_ACTIVE', '').lower() != 'false'

# BEGIN: Plugin specific configurations
# The maximum length of the collected parameter, parameters longer than the specified length will be truncated,
# length 0 turns off parameter tracing
sql_parameters_length: int = int(os.getenv('SW_AGENT_SQL_PARAMETERS_LENGTH') or '0')
# Indicates whether to collect the filters of pymongo
pymongo_trace_parameters: bool = os.getenv('SW_AGENT_PYMONGO_TRACE_PARAMETERS', '').lower() == 'true'
# The maximum length of the collected filters, filters longer than the specified length will be truncated
pymongo_parameters_max_length: int = int(os.getenv('SW_AGENT_PYMONGO_PARAMETERS_MAX_LENGTH') or '512')
# If true, trace all the DSL(Domain Specific Language) in ElasticSearch access, default is false
elasticsearch_trace_dsl: bool = os.getenv('SW_AGENT_ELASTICSEARCH_TRACE_DSL', '').lower() == 'true'
# When `COLLECT_HTTP_PARAMS` is enabled, how many characters to keep and send to the OAP backend, use negative
# values to keep and send the complete parameters, NB. this config item is added for the sake of performance.
http_params_length_threshold: int = int(os.getenv('SW_AGENT_HTTP_PARAMS_LENGTH_THRESHOLD') or '1024')
# Comma-delimited list of http methods to ignore (GET, POST, HEAD, OPTIONS, etc...)
http_ignore_method: str = os.getenv('SW_AGENT_HTTP_IGNORE_METHOD', '').upper()
# This config item controls that whether the Flask plugin should collect the parameters of the request.
flask_collect_http_params: bool = os.getenv('SW_AGENT_FLASK_COLLECT_HTTP_PARAMS', '').lower() == 'true'
# This config item controls that whether the Sanic plugin should collect the parameters of the request.
sanic_collect_http_params: bool = os.getenv('SW_AGENT_SANIC_COLLECT_HTTP_PARAMS', '').lower() == 'true'
# This config item controls that whether the Django plugin should collect the parameters of the request.
django_collect_http_params: bool = os.getenv('SW_AGENT_DJANGO_COLLECT_HTTP_PARAMS', '').lower() == 'true'
# This config item controls that whether the FastAPI plugin should collect the parameters of the request.
fastapi_collect_http_params: bool = os.getenv('SW_AGENT_FASTAPI_COLLECT_HTTP_PARAMS', '').lower() == 'true'
# This config item controls that whether the Bottle plugin should collect the parameters of the request.
bottle_collect_http_params: bool = os.getenv('SW_AGENT_BOTTLE_COLLECT_HTTP_PARAMS', '').lower() == 'true'
# The maximum length of `celery` functions parameters, longer than this will be truncated, 0 turns off
celery_parameters_length: int = int(os.getenv('SW_AGENT_CELERY_PARAMETERS_LENGTH') or '512')

# THIS MUST FOLLOW DIRECTLY AFTER LIST OF CONFIG OPTIONS!
options = [key for key in globals() if key not in options]  # THIS MUST FOLLOW DIRECTLY AFTER LIST OF CONFIG OPTIONS!

options_with_default_value_and_type = {key: (globals()[key], type(globals()[key])) for key in options}


def init(**kwargs) -> None:
    """
    Used to initialize the configuration of the SkyWalking Python Agent.
    Refer to the official online documentation
    https://skywalking.apache.org/docs/skywalking-python/next/en/setup/configurations/
    for more information on the configuration options.

    Args:
        **kwargs: Any of the configuration options listed
    """
    glob = globals()
    for key, val in kwargs.items():
        if key not in options:
            raise KeyError(f'Invalid configuration option {key}')

        glob[key] = val


def finalize():
    reesc = re.compile(r'([.*+?^=!:${}()|\[\]\\])')
    suffix = r'^.+(?:' + '|'.join(reesc.sub(r'\\\1', s.strip()) for s in ignore_suffix.split(',')) + ')$'
    method = r'^' + '|'.join(s.strip() for s in http_ignore_method.split(',')) + '$'
    path = '^(?:' + \
           '|'.join(  # replaces ","
               '/(?:[^/]*/)*'.join(  # replaces "/**/"
                   '(?:(?:[^/]+/)*[^/]+)?'.join(  # replaces "**"
                       '[^/]*'.join(  # replaces "*"
                           '[^/]'.join(  # replaces "?"
                               reesc.sub(r'\\\1', s) for s in p3.split('?')
                           ) for p3 in p2.split('*')
                       ) for p2 in p1.strip().split('**')
                   ) for p1 in p0.split('/**/')
               ) for p0 in trace_ignore_path.split(',')
           ) + ')$'

    global RE_IGNORE_PATH, RE_HTTP_IGNORE_METHOD
    RE_IGNORE_PATH = re.compile(f'{suffix}|{path}')
    RE_HTTP_IGNORE_METHOD = re.compile(method, re.IGNORECASE)


def ignore_http_method_check(method: str):
    return RE_HTTP_IGNORE_METHOD.match(method)
