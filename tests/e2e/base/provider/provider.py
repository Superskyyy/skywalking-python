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
import logging
import random
import time

import uvicorn
from fastapi import FastAPI


class SWFormatterMock(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        return 'e2e:\n' + result


formatter = SWFormatterMock(logging.BASIC_FORMAT)

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
    e2e_provider_logger.warning('Warning! This is reported!')

    # shouldn't be reported according to agent setting
    e2e_provider_logger.debug('Casual Debug...not reported!')

    return {'artist': 'Luis Fonsi'}


if __name__ == '__main__':
    # noinspection PyTypeChecker
    uvicorn.run(app, host='0.0.0.0', port=9090)
