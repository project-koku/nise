#! /usr/bin/env python3
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
"""Utility functions for large yaml generator."""
# pylint: disable=invalid-name,useless-super-delegation


class dicta(dict):
    """
    Dict subclass that can access values via key or attribute.

    Ex:
        x = dicta(a=1, b=2)
        print(x.a)     # 1
        print(x['b'])  # 2
    """

    def __init__(self, *args, **kwargs):
        """Dicta constructor."""
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        """Get attribute."""
        return super().__getitem__(key)

    def __setattr__(self, key, val):
        """Set attribute."""
        super().__setitem__(key, val)

    def __delattr__(self, key):
        """Delete attribute."""
        super().__delitem__(key)

    def copy(self):
        """Get a copy."""
        return self.__class__(self)
