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
"""Logging."""
import logging
import sys

# logging
LOG = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_VERBOSITY = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
logging.basicConfig(format=LOG_FORMAT, level=logging.ERROR, stream=sys.stdout)
