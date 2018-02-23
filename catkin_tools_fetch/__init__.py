# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .cli import main
from .cli import prepare_arguments_deps

# This describes this command to the loader
description_deps = dict(
    verb='deps',
    description='Manage dependencies',
    main=main,
    prepare_arguments=prepare_arguments_deps,
)

# This describes this command to the loader
description_dependencies = dict(
    verb='dependencies',
    description='Manage dependencies',
    main=main,
    prepare_arguments=prepare_arguments_deps,
)
