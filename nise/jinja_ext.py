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
"""Jinja2 extensions."""
from faker import Faker

FAKE = Faker()


def faker_passthrough(provider, **kwargs):
    """Expose faker inside of a Jinja template.

    Example:

        {{ faker('faker_provider', keyword_arg=1, keyword_arg=other) }}

    The first argument MUST be the faker provider being called.

    All keyword arguments are passed through to the Faker object using the named provider.

    """
    return getattr(FAKE, provider)(**kwargs)
