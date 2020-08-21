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


def deepupdate(original, update):  # noqa: C901
    """Recursively update a nested dict/list.

    original and update must have the same structure.

    """
    if not (isinstance(update, list) or isinstance(update, dict)):
        return update

    if isinstance(update, dict):
        for key, value in update.items():
            # TODO: change static file syntax to not require these special cases
            if key == "tags" and value:
                # don't preserve generated tags, only overwrite
                original[key] = value
            elif key == "generators":
                # line up FooGenerator keys within the generators list and update matching dicts.
                original[key] = _deepupdate_generators(original[key], value)
            elif key in original or "Generator" not in key:
                # only "drill in" if the FooGenerator keys match, or it's another key name
                original[key] = deepupdate(original.get(key, {}), value)

    if isinstance(update, list):
        if not original:
            return update

        for idx, item in enumerate(update):
            if len(original) <= idx:
                original.append(item)
            else:
                original[idx] = deepupdate(original[idx], update[idx])

    return original


def _deepupdate_generators(original, update):
    """Handle the generators deepupdate special-case."""

    update_keys = [key for x in update for key in list(x.keys())]
    original_keys = [key for x in original for key in list(x.keys())]

    for origkey in set(original_keys):
        if origkey in set(update_keys):
            original_indices = [idx for idx, item in enumerate(original_keys) if item == origkey]
            update_indices = [idx for idx, item in enumerate(update_keys) if item == origkey]

            for idx, up_idx in enumerate(update_indices):
                original[original_indices[idx]][origkey] = deepupdate(
                    original[original_indices[idx]][origkey], update[up_idx][origkey]
                )
    return original
