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
import os
import platform
import socket
from abc import ABC, abstractmethod
from typing import List

from skywalking import config
from skywalking.config import service_instance_property_report_factor
from skywalking.protocol.common.Common_pb2 import KeyStringValuePair
from skywalking.utils.integer import AtomicInteger


class ServiceManagementClient(ABC):
    def __init__(self):
        self.sent_properties_counter = AtomicInteger(var=0)
        self.os_info = self.get_os_info()

    def fork_regenerate_properties(self):
        self.sent_properties_counter = AtomicInteger(var=0)
        self.os_info = self.get_os_info()

    @abstractmethod
    def fork_after_in_child(self):
        """
        This method is to be implemented by the subclass,
        to handle post-fork behavior in the child process.
        """
        pass

    def send_instance_props(self) -> None:
        raise NotImplementedError()

    def refresh_instance_props(self) -> None:
        """
        Periodically refresh the instance properties to prevent loss on OAP TTL records expiration.
        """
        if self.sent_properties_counter.add_and_get(delta=1) % service_instance_property_report_factor == 0:
            self.send_instance_props()

    @staticmethod
    def get_os_info() -> List[dict]:
        """
        Get current running Python interpreter's system properties.
        Returns: [{'key': str, 'value': str}, ...]
        """
        properties = [
            {'key': 'language', 'value': 'python'},
            {'key': 'OS Name', 'value': os.name},
            {'key': 'hostname', 'value': socket.gethostname()},
            {'key': 'ipv4', 'value': '; '.join(socket.gethostbyname_ex(socket.gethostname())[2])},
            {'key': 'python_implementation', 'value': platform.python_implementation()},
            {'key': 'python_version', 'value': platform.python_version()},
        ]
        namespace = config.namespace
        if namespace:
            properties.append({'key': 'namespace', 'value': namespace})
        return properties

    @property
    def process_pid(self) -> dict:
        """
        This is not cached since it can change upon fork.
        Get current running Python interpreter's process id.
        Returns: int
        """
        return {'key': 'Process No.', 'value': str(os.getpid())}

    @property
    def instance_properties(self):
        """
        os_info is pre-initialized, while process_pid is reevaluated each time.
        Returns:

        """
        self.os_info.append(self.process_pid)
        return self.os_info

    @property
    def instance_properties_proto(self):
        return [KeyStringValuePair(key=prop['key'], value=prop['value']) for prop in self.instance_properties]

    def send_heart_beat(self) -> None:
        raise NotImplementedError()


class Service(ABC):
    @abstractmethod
    def report(self, segment: bytes) -> None:
        raise NotImplementedError()


class TraceSegmentReportService(Service):
    def report(self, generator):
        raise NotImplementedError()


class MeterReportService(Service):
    def report(self, generator):
        raise NotImplementedError()


class LogDataReportService(Service):
    def report(self, generator):
        raise NotImplementedError()


class ProfileTaskChannelService(Service):
    def do_query(self):
        raise NotImplementedError()

    def report(self, generator):
        raise NotImplementedError()
