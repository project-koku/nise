#
# Copyright 2020 Red Hat, Inc.
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
    """Recursively update a nested dict/list.

    original and update must have the same structure
    """
    if not (isinstance(update, list) or isinstance(update, dict)):
        return update

    if isinstance(update, dict):
        for key, value in update.items():
            original[key] = deepupdate(original.get(key, {}), value)

    if isinstance(update, list):
        for idx, item in enumerate(update):
            if not original:
                original = update
            elif len(original) <= idx:
                original.append(item)
            else:
                original[idx] = deepupdate(original[idx], update[idx])

    return original
