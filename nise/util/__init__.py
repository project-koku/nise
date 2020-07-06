#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Utility functions."""
from collections import abc

import yaml

from .log import LOG  # noqa: F401
from .log import LOG_FORMAT  # noqa: F401
from .log import LOG_VERBOSITY  # noqa: F401


def load_yaml(objekt):
    """Load a yaml document.

    Params:
        objekt (str): A filename containing a YAML document OR a YAML document.
    """
    if objekt is None:
        return None

    yamlfile = None
    try:
        with open(objekt, "r+") as yaml_file:
            yamlfile = yaml.safe_load(yaml_file)
    except (TypeError, OSError, IOError):
        yamlfile = yaml.safe_load(objekt)
    return yamlfile


def deepupdate(original, update):
    """Recursively update a dict.

    Subdict's won't be overwritten but also updated.
    """
    if not isinstance(original, abc.Mapping):
        return update
    for key, value in update.items():
        if isinstance(value, abc.Mapping):
            original[key] = deepupdate(original.get(key, {}), value)
        else:
            original[key] = value
    return original
