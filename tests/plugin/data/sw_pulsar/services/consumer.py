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

if __name__ == '__main__':
    import pulsar

    client = pulsar.Client(
        service_url='pulsar://pulsar-server:6650',
        authentication=None,
        operation_timeout_seconds=30,
        io_threads=1,
        message_listener_threads=1,
        concurrent_lookup_requests=50000,
        log_conf_file_path=None,
        use_tls=False,
        tls_trust_certs_file_path=None,
        tls_allow_insecure_connection=False,
        tls_validate_hostname=False,
        logger=None,
        connection_timeout_ms=10000,
        listener_name=None
    )
    consumer = client.subscribe('sw-topic', 'sw-subscription')

    while True:
        try:
            msg = consumer.receive()
            print('Received message = ', str(msg.data().decode('utf-8')), '|message_id = ', msg.message_id())
            consumer.acknowledge(msg)
        except pulsar.Interrupted:
            break

    client.close()
