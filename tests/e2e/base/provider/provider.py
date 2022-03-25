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
This module contains the Provider part of the e2e tests.
We also cover the usage of logging interception in this module.
"""
import io
import logging
import random
import time
import traceback

import uvicorn
from fastapi import FastAPI


class E2EProviderFormatter(logging.Formatter):
    """
    User defined formatter should in no way be
    interfered by the log reporter formatter.
    """

    def format(self, record):
        result = super().format(record)
        return 'e2e_provider:=' + result

    def formatException(self, ei):  # noqa
        """
        Mock user defined formatter which limits the traceback depth
        """
        sio = io.StringIO()
        tb = ei[2]
        traceback.print_exception(ei[0], ei[1], tb, 1, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == '\n':
            s = s[:-1]
        return s


formatter = E2EProviderFormatter(logging.BASIC_FORMAT)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

app = FastAPI()

e2e_provider_logger = logging.getLogger('__name__')
e2e_provider_logger.setLevel(logging.INFO)

e2e_provider_logger.addHandler(stream_handler)


@app.get('/artist')
@app.post('/artist')
async def application():
    time.sleep(random.random())
    # set agent threshold to surpass the warning log which is 10 and the debug log which is 5
    e2e_provider_logger.warning('E2E Provider Warning, this is reported!')
    # shouldn't be reported according to agent setting
    e2e_provider_logger.debug('Casual Debug...not reported.')

    # try:
    #     raise Exception('This is an exception!')
    # except Exception:  # noqa
    #     e2e_provider_logger.exception('E2E Provider Exception, this is reported!')

    return {'artist': 'Luis Fonsi'}


if __name__ == '__main__':
    # noinspection PyTypeChecker
    uvicorn.run(app, host='0.0.0.0', port=9090)
