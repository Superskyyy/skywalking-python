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
A tool to generate test matrix report for SkyWalking Python Plugins
"""
import pkgutil

from skywalking.plugins import __path__ as plugins_path

doc_head = """# Supported Libraries
This document is **automatically** generated from the SkyWalking Python testing matrix.
The column of versions only indicates the set of library versions tested in a best-effort manner.
If you find newer major versions that are missing from the following table, and it's not documented as a limitation,
please PR to update the test matrix in the plugin.
Versions marked as NOT SUPPORTED may be due to
an incompatible version with Python in the original library
or a limitation of SkyWalking auto-instrumentation (welcome to contribute!)
"""
table_head = """### Plugin Support Table
Library | Python Version - Lib Version | Plugin Name
| :--- | :--- | :--- |
"""


def generate_plugin_doc():
    """
    This function generates a plugin.md doc to the docs folder
    Returns: None
    Raises: Attribute Error - missing matrix/link/note in sw_plugin
    """
    table_entries = []
    note_entries = []
    for importer, modname, _ispkg in pkgutil.iter_modules(plugins_path):
        plugin = importer.find_module(modname).load_module(modname)
        libs_tested, links_tested, plugin_support_matrix = [], [], {}
        try:
            plugin_support_matrix = plugin.support_matrix  # type: dict
            plugin_support_links = plugin.link_vector  # type: list
            libs_tested = list(plugin_support_matrix.keys())
            links_tested = plugin_support_links  # type: list
            if plugin.note:
                note_entries.append(plugin.note)
        except AttributeError:
            print(f'Missing attribute in {modname}, please follow the correct plugin style.')

        for lib, link in zip(libs_tested, links_tested):  # NOTE: maybe a two lib support like http.server + werkzeug
            lib_entry = str(lib)
            lib_link = link
            version_vector = plugin_support_matrix[lib_entry]  # type: dict
            pretty_vector = ''
            for python_version, lib_versions in version_vector.items():
                python_version_text = f'Python {python_version}'
                lib_version_text = f"{str(lib_versions) if lib_versions else 'NOT SUPPORTED YET'}; "
                pretty_vector += f'{python_version_text} - {lib_version_text}'
            table_entry = f'| [{lib_entry}]({lib_link}) | {pretty_vector} | `{modname}` |'
            table_entries.append(table_entry)

    with open('docs/en/setup/Plugins.md', 'w') as plugin_doc:
        plugin_doc.write(doc_head)

        plugin_doc.write(table_head)
        for table_entry in table_entries:
            plugin_doc.write(f'{table_entry}\n')

        plugin_doc.write('### Notes\n')
        for note_entry in note_entries:
            plugin_doc.write(f'- {note_entry}\n')


if __name__ == '__main__':
    generate_plugin_doc()
