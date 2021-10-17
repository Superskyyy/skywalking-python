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
A management utility to handle testing matrix for different Pythons and Library versions
"""
import sys

import pytest

from skywalking.utils.exception import VersionRuleException

_operators = {
    '<': lambda cv, ev: cv < ev,
    '<=': lambda cv, ev: cv < ev or cv == ev,
    '==': lambda cv, ev: cv == ev,
    '>=': lambda cv, ev: cv > ev or cv == ev,
    '>': lambda cv, ev: cv > ev,
    '!=': lambda cv, ev: cv != ev
}


def compare_version(rule_unit):
    idx = 2 if rule_unit[1] == '=' else 1
    symbol = rule_unit[0:idx]
    expect_python_version = tuple(map(int, rule_unit[idx:].split('.')))
    test_python_version = sys.version_info[:2]  # type: tuple
    f = _operators.get(symbol) or None
    if not f:
        raise VersionRuleException("version rule {} error. only allow >,>=,==,<=,<,!= symbols".format(rule_unit))

    return f(test_python_version, expect_python_version)


def get_test_vector(lib_name: str, test_matrix: dict):
    """
    If gets empty or ! will get skipped
    Args:
        test_matrix: a test matrix including python version specification and lib version
        lib_name: the name of the tested lib, used for requirements.txt generation

    Returns:

    """
    for py_version in test_matrix:
        if compare_version(py_version):
            # proceed if current python version is valid
            version_row = test_matrix[py_version]
            return [f"{lib_name}=={idx}" for idx in version_row]
    return []  # non-match


if __name__ == '__main__':
    pytest.main(['-v', '../tests/plugin/sw_django'])
