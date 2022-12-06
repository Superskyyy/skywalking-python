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
Post-fork hook for uWSGI

We simply inject this module for users, so they don't need to provide a @postfork hook

Used by: bootstrap/cli/sw_python.py to inject uWSGI option --import [this module]

Potential issue, if the user also uses --import, what would happen?


This is a workaround for the fact that uwsgi has problems with forking signal as of
2022, https://github.com/unbit/uwsgi/pull/2388 - fixed but lock exception occurs
https://github.com/unbit/uwsgi/issues/1978 - not fixed

For Gunicorn - we don't use a hook, since it's not possible to inject a hook without overriding
the entire gunicorn config file, which is not a good idea. Instead, inside the sitecustomize.py we
inject a gunicorn hook that will start the agent after the worker is forked. (with os.register_at_fork)
"""
from uwsgidecorators import postfork
from skywalking import agent
import os

from skywalking.loggings import logger
#
# config.init(collector_address='localhost:12800', protocol='http', service_name='test-fastapi-service',
#             log_reporter_active=True, service_instance=f'test_instance-{os.getpid()} forkfork',
#             logging_level='CRITICAL')


@postfork
def setup_skywalking():
    logger.debug(f'Apache SkyWalking Python agent started in forked process PID {os.getpid()}')
    agent.start()
