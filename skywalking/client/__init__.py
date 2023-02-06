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
import functools
import os
import platform
import socket
from abc import ABC, abstractmethod
from typing import List

from skywalking import config
from skywalking.config import service_instance_property_report_factor
from skywalking.loggings import logger
from skywalking.protocol.common.Common_pb2 import KeyStringValuePair


class ServiceManagementClient(ABC):
    def __init__(self):
        self.sent_properties_counter = 0

    @abstractmethod
    def send_instance_props(self) -> None:
        """
        Unique to each protocol, send instance properties to OAP.
        """
        raise NotImplementedError()

    def refresh_instance_props(self) -> None:
        """
        Periodically refresh the instance properties to prevent loss on OAP TTL records expiration.
        """
        self.sent_properties_counter += 1
        if self.sent_properties_counter % service_instance_property_report_factor == 0:
            self.send_instance_props()

    @property
    @functools.lru_cache()
    def instance_properties(self) -> List[dict]:
        """
        Get current running Python interpreter's system properties.
        Returns: [{'key': str, 'value': str}, ...]
        """
        try:
            properties = [
                {'key': 'language', 'value': 'python'},
                {'key': 'OS Name', 'value': os.name},
                {'key': 'Process No.', 'value': str(os.getpid())},
                {'key': 'hostname', 'value': socket.gethostname()},
                {'key': 'ipv4', 'value': '; '.join(socket.gethostbyname_ex(socket.gethostname())[2])},
                {'key': 'python_implementation', 'value': platform.python_implementation()},
                {'key': 'python_version', 'value': platform.python_version()},
            ]

        except Exception as e:  # noqa
            logger.exception('Failed to get OS info, fallback to basic properties.')
            properties = [
                KeyStringValuePair(key='language', value='python'),
                KeyStringValuePair(key='Process No.', value=str(os.getpid())),
            ]

        namespace = config.namespace
        if namespace:
            properties.append({'key': 'namespace', 'value': namespace})

        return properties

    @property
    @functools.lru_cache()
    def instance_properties_proto(self) -> List[KeyStringValuePair]:
        """
        Converts to protobuf format.
        Returns: [KeyStringValuePair, ...]
        """
        return [KeyStringValuePair(key=prop['key'], value=prop['value']) for prop in self.instance_properties]

    def send_heart_beat(self) -> None:
        """
        Each protocol must implement this method to send heart beat to OAP.
        Returns: None
        """
        raise NotImplementedError()


class Service(ABC):
    @abstractmethod
    def report(self, segment: bytes) -> None:
        raise NotImplementedError()


class TraceSegmentReportService(Service):
    @abstractmethod
    def report(self, generator):
        raise NotImplementedError()


class MeterReportService(Service):
    @abstractmethod
    def report(self, generator):
        raise NotImplementedError()


class LogDataReportService(Service):
    @abstractmethod
    def report(self, generator):
        raise NotImplementedError()


class ProfileTaskChannelService(Service):
    @abstractmethod
    def do_query(self):
        raise NotImplementedError()

    @abstractmethod
    def report(self, generator):
        raise NotImplementedError()
