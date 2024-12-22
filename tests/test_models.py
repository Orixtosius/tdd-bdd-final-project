# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        read_product = Product.find(product.id)
        self.assertEqual(read_product.id, product.id)
        self.assertEqual(read_product.name, product.name)
        self.assertEqual(read_product.description, product.description)
        self.assertEqual(read_product.price, product.price)
        self.assertEqual(read_product.available, product.available)
        self.assertEqual(read_product.category, product.category)

    def test_update_a_product(self):
        """ It should update a product """
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.description = "Foobar"
        original_id = product.id
        product.update()
        self.assertEqual(original_id, product.id)
        self.assertEqual(product.description, "Foobar")
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "Foobar")

    def test_delete_a_product(self):
        """ It should update a product  """
        product = ProductFactory()
        product.id = None
        product.create()
        first_product_id = product.id
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 2)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, first_product_id)

    def test_list_all_products(self):
        """ It should list all products """
        products = Product.all()
        self.assertEqual(products, [])
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """ It should find products by name """
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        target = products[0]
        occurrence = sum([
            int(target.name == product.name)
            for product in products
        ])
        products = Product.find_by_name(target.name)
        self.assertEqual(products.count(), occurrence)
        for product in products:
            self.assertEqual(target.name, product.name)

    def test_find_by_availablity(self):
        """ It should find products by availablity """
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        target = products[0]
        occurrence = sum([
            int(target.available == product.available)
            for product in products
        ])
        products = Product.find_by_availability(
            target.available
        )
        self.assertEqual(products.count(), occurrence)
        for product in products:
            self.assertEqual(target.available, product.available)

    def test_find_by_category(self):
        """ It should find products by category """
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        target = products[0]
        occurrence = sum([
            int(target.category == product.category)
            for product in products
        ])
        products = Product.find_by_category(
            target.category
        )
        self.assertEqual(products.count(), occurrence)
        for product in products:
            self.assertEqual(target.category, product.category)

    def test_find_by_price(self):
        """ It should find products by price """
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        target = products[0]
        occurrence = sum([
            int(target.price == product.price)
            for product in products
        ])
        products = Product.find_by_price(
            target.price
        )
        self.assertEqual(products.count(), occurrence)
        for product in products:
            self.assertEqual(target.price, product.price)

    def test_find_by_str_type_price(self):
        """ It should find products by string price """
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        target = products[0]
        target.price = str(target.price)
        occurrence = sum([
            int(target.price == product.price)
            for product in products
        ])
        products = Product.find_by_price(
            target.price
        )
        self.assertEqual(products.count(), occurrence)
        for product in products:
            self.assertEqual(target.price, product.price)

    def test_update_null_product(self):
        """ It should raise an error during update """
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.id = 0
        self.assertRaises(DataValidationError, product.update)

    def test_deserialize_unavailable_product(self):
        """ It should raise an error for an unavailable product """
        product = ProductFactory()
        data = product.serialize()
        recreated = product.deserialize(data)
        self.assertEqual(product, recreated)
        data["available"] = "Foo"
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_missing_product_data(self):
        """ It should raise a key error for missing info """
        product = ProductFactory()
        data = product.serialize()
        del data["name"]
        self.assertRaises(DataValidationError, product.deserialize, data)
