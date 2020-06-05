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
from unittest import TestCase

from nise.yaml_generators.utils import dicta
from nise.yaml_generators.utils import generate_name
from nise.yaml_generators.utils import generate_number_str
from nise.yaml_generators.utils import generate_resource_id
from nise.yaml_generators.utils import generate_words


class UtilTestCase(TestCase):
    """Test cases for utility generators."""

    def setUp(self):
        """Setup the test."""
        self.dc = dicta(max_resource_id_length=10, max_name_words=2)

    def test_generate_words(self):
        "Test length of generated word is equal to maximum defined in config."
        words = generate_words(self.dc).split("-")
        self.assertEqual(len(words), self.dc.max_name_words)

    def test_generate_number_str(self):
        "Test length of generated number is equal to maximum defined in config."
        num_str = generate_number_str(self.dc.max_resource_id_length)
        self.assertEqual(len(num_str), self.dc.max_resource_id_length)

    def test_generate_name(self):
        "Test length of generated name is equal to maximum defined in config."
        name = generate_name(self.dc).split("-")
        self.assertEqual(len(name), self.dc.max_name_words)

    def test_generate_name_with_prefix(self):
        "Test length of generated name is equal to maximum defined in config + 1 for prefix."
        prefix = "prefix"
        name = generate_name(self.dc, prefix=prefix).split("-")
        self.assertEqual(len(name), self.dc.max_name_words + 1)
        self.assertEqual(name[0], prefix)

    def test_generate_name_with_suffix(self):
        "Test length of generated name is equal to maximum defined in config + 1 for suffix."
        suffix = "prefix"
        name = generate_name(self.dc, suffix=suffix).split("-")
        self.assertEqual(len(name), self.dc.max_name_words + 1)
        self.assertNotEqual(name[0], suffix)
        self.assertEqual(name[-1], suffix)

    def test_generate_name_with_prefix_and_suffix(self):
        "Test length of generated name is equal to maximum defined in config + 2."
        prefix = "prefix"
        suffix = "suffix"
        name = generate_name(self.dc, prefix=prefix, suffix=suffix).split("-")
        self.assertEqual(len(name), self.dc.max_name_words + 2)
        self.assertEqual(name[0], prefix)
        self.assertEqual(name[-1], suffix)

    def test_generate_name_not_dynamic_with_prefix_and_suffix(self):
        "Test length of generated name is equal to 2 (prefix + suffix)"
        prefix = "prefix"
        suffix = "suffix"
        name = generate_name(self.dc, prefix=prefix, suffix=suffix, dynamic=False).split("-")
        self.assertEqual(len(name), 2)
        self.assertEqual(name[0], prefix)
        self.assertEqual(name[-1], suffix)

    def test_generate_resource_id(self):
        "Test length of generated id is equal to maximum defined in config."
        res_id = generate_resource_id(self.dc)
        self.assertEqual(len(res_id), self.dc.max_resource_id_length)

    def test_generate_resource_id_with_prefix(self):
        "Test length of generated id is equal to maximum defined in config + 2 for prefix."
        prefix = "p"
        res_id = generate_resource_id(self.dc, prefix=prefix)
        self.assertEqual(len(res_id), self.dc.max_resource_id_length + 2)
        self.assertEqual(res_id.split("-")[0], prefix)

    def test_generate_resource_id_with_suffix(self):
        "Test length of generated id is equal to maximum defined in config + 2 for suffix."
        suffix = "s"
        res_id = generate_resource_id(self.dc, suffix=suffix)
        self.assertEqual(len(res_id), self.dc.max_resource_id_length + 2)
        self.assertEqual(res_id.split("-")[-1], suffix)
        self.assertNotEqual(res_id.split("-")[0], suffix)

    def test_generate_resource_id_with_prefix_and_suffix(self):
        "Test length of generated id is equal to maximum defined in config + 4."
        prefix = "p"
        suffix = "s"
        res_id = generate_resource_id(self.dc, prefix=prefix, suffix=suffix)
        self.assertEqual(len(res_id), self.dc.max_resource_id_length + 4)
        self.assertEqual(res_id.split("-")[0], prefix)
        self.assertEqual(res_id.split("-")[-1], suffix)

    def test_generate_resource_id_not_dynamic_with_prefix_and_suffix(self):
        "Test length of generated id is equal to 3 (prefix + suffix)"
        prefix = "p"
        suffix = "s"
        res_id = generate_resource_id(self.dc, prefix=prefix, suffix=suffix, dynamic=False)
        self.assertEqual(len(res_id), 3)  # 3 because double -- is replaced with a single -
        self.assertEqual(res_id.split("-")[0], prefix)
        self.assertEqual(res_id.split("-")[-1], suffix)


class TestDicta(TestCase):
    """Test cases for dicta."""

    def test_dicta(self):
        """
        Test dicta class
        """
        td = dicta()
        self.assertEqual(len(td), 0)

        td.test = 1
        self.assertEqual(len(td), 1)
        self.assertEqual(td.test, td["test"])

        td.test = 2
        self.assertEqual(td.test, 2)

        td2 = td.copy()
        self.assertTrue(isinstance(td2, dicta))
        self.assertEqual(td2, td)

        with self.assertRaises(KeyError):
            td.x

        del td.test
        self.assertEqual(len(td), 0)
