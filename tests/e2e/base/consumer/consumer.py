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
import logging

import aiohttp
import uvicorn
from fastapi import FastAPI
from fastapi import Request

from tests.e2e.base.logger import stream_handler

app = FastAPI()

e2e_consumer_logger = logging.getLogger('__name__')
e2e_consumer_logger.setLevel(logging.INFO)

e2e_consumer_logger.addHandler(stream_handler)


@app.post('/artist')
async def application(request: Request):
    payload = await request.json()
    e2e_consumer_logger.info('Info! This is not reported!')

    e2e_consumer_logger.warning('Warning! This is reported!')

    try:
        async with aiohttp.ClientSession() as session:
            # change to localhost to run locally
            async with session.post('http://localhost:9091/artist', data=payload) as response:
                return await response.json()
    except Exception as e:
        print(e)
        return {'message': 'Error'}


if __name__ == '__main__':
    # noinspection PyTypeChecker
    uvicorn.run(app, host='0.0.0.0', port=9090)
