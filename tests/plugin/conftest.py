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

import inspect
import os
import time
from os.path import dirname
from typing import Callable

import pytest
from _pytest.fixtures import FixtureRequest
from testcontainers.compose import DockerCompose


@pytest.fixture
def version():
    # type: () -> str
    return ''


# noinspection PyUnusedLocal
@pytest.fixture
def prepare():
    # type: () -> Callable
    return lambda *_: None


@pytest.fixture
def docker_compose(request, prepare, version):
    # type: (FixtureRequest, Callable, str) -> None

    module = request.module
    cwd = dirname(inspect.getfile(module))

    if version:
        with open(os.path.join(cwd, 'requirements.txt'), mode='w') as req:
            req.write(version)

    with DockerCompose(filepath=cwd) as compose:

        exception = None
        exception_delay = 100
        for _ in range(1):
            try:
                # prepare()
                stdout, stderr = compose.get_logs()
                if stderr:
                    print(f'Errors\n:{stderr}')
                else:
                    print('what?')
                if stdout:
                    print(f'OUTSKY:\n{stdout}')
                else:
                    print('what???')
                print('hello world!')
                exception = None
                break
            except Exception as e:
                time.sleep(1)
                exception = e
        if exception:
            # time.sleep(exception_delay)
            compose.stop()
            raise Exception(f"""Wait time exceeded {exception_delay} secs. Exception {exception}""")

        yield compose
