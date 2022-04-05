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
import re

import faker


SEEN_NAMES = set()
SEEN_ACCOUNT_IDS = set()
SEEN_RESOURCE_IDS = set()

DBL_DASH = re.compile("-+")
FAKER = faker.Faker()


def generate_words(config):
    """
    Generate a hyphen-separated string of words.
    The number of words is specified in the config. (config.max_name_words)
    """
    return "-".join(FAKER.words(config.max_name_words))


def generate_number_str(max_len):
    """
    Generate a string of digits of arbitrary length.
    The maximum length is specified in the config. (max_len)
    """
    return str(FAKER.random_int(int(10 ** (max_len - 1)), 10 ** max_len)).zfill(max_len)


def generate_name(config, prefix="", suffix="", dynamic=True, generator=generate_words, cache=SEEN_NAMES):
    """
    Generate a random resource name using faker.
    Params:
        config : dicta - config information for the generator
        prefix : str - a static prefix
        suffix : str - a static suffix
        dynamic : bool - flag to run the generator function
        generator : func - function that will generate the dynamic portion of the name
        cache : set - a cache for uniqueness across all calls
    Returns:
        str
    """
    new_name = None
    while True:
        if prefix:
            prefix += "-"
        if suffix:
            suffix = "-" + suffix
        mid = generator(config) if dynamic else ""
        new_name = f"{prefix}{mid}{suffix}"
        if new_name not in cache:
            cache.add(new_name)
            break

    return DBL_DASH.sub("-", new_name)


def generate_resource_id(config, prefix="", suffix="", dynamic=True):
    """
    Generate a random resource id using faker.
    Params:
        config : dicta - config information for the generator
        prefix : str - a static prefix
        suffix : str - a static suffix
        dynamic : bool - flag to run the generator function
        generator : func - function that will generate the dynamic portion of the resource id
        cache : set - a cache for uniqueness across all calls
    Returns:
        str
    """
    return generate_name(
        config.max_resource_id_length,
        prefix=prefix,
        suffix=suffix,
        dynamic=dynamic,
        generator=generate_number_str,
        cache=SEEN_RESOURCE_IDS,
    )


def generate_account_id(config, prefix="", suffix="", dynamic=True):
    """
    Generate a random account id using faker.
    Params:
        config : dicta - config information for the generator
        prefix : str - a static prefix
        suffix : str - a static suffix
        dynamic : bool - flag to run the generator function
        generator : func - function that will generate the dynamic portion of the resource id
        cache : set - a cache for uniqueness across all calls
    Returns:
        str
    """
    return generate_name(
        config.max_account_id_length,
        prefix=prefix,
        suffix=suffix,
        dynamic=dynamic,
        generator=generate_number_str,
        cache=SEEN_ACCOUNT_IDS,
    )


class dicta(dict):
    """
    Dict subclass that can access values via key or attribute.

    Ex:
        x = dicta(a=1, b=2)
        print(x.a)     # 1
        print(x['b'])  # 2
    """

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
