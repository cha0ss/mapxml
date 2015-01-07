# coding=utf-8
from datetime import datetime
from unittest import TestCase
from mapxml.mapxml import StringType, IntegerType, MapXml


# Test data.
TEST_XML = """<?xml version="1.0"?>
<items>
    <item>
        <id> f4373d1c56c278f70568f8ba0e9bdab3   </id>
        <subaccount>1234 </subaccount>
        <status>wait</status>
        <date>1371801875</date>
    </item>
</items>"""

TEST_XML_2 = """<?xml version="1.0"?>
<items>
    <item>
        <id> f4373d1c56c278f70568f8ba0e9bdab3   </id>
        <subaccount>1234 </subaccount>
        <status>wait</status>
        <date>1371801875</date>
    </item>
    <item>
        <id> f4373d1c56c278f70568f8ba0e9bdab3   </id>
        <subaccount>9877 </subaccount>
        <status>cancel</status>
        <date>1371801875</date>
    </item>
</items>"""

TEST_XML_3 = """<?xml version="1.0"?>
<items>
    <item>
        <id> f4373d1c56c278f70568f8ba0e9bdab3   </id>
        <status>wait</status>
        <date>1371801875</date>
    </item>
    <item>
        <id> f4373d1c56c278f70568f8ba0e9bdab3   </id>
        <subaccount>9877 </subaccount>
        <status>cancel</status>
        <date>1371801875</date>
    </item>
</items>"""

TEST_HTML_1 = """<html>
    <head>
        <title>Hello</title>
    </head>
    <body>
        <div id="products">
            <div class="product">
                <span id="price">1000</span>
                <label id="brand">Thing</span>
            </div>
            <div class="product">
                <span id="price">2000</span>
                <label id="brand">Thing2</span>
            </div>
        </div>
    </body>
</html>"""


class TestMapXml(TestCase):
    def test_map_works_as_expected(self):
        """
        It should map documents XML properly.
        It should trim strings properly.
        It should support custom root name.
        It should support conditional root parsing.
        It should support custom value converters.
        It should support HTML markup.
        """

        # SPEC: It should map documents XML properly.
        # SPEC: It should trim strings properly.
        # SPEC: Case 1.
        class Item(object):
            item_id = StringType(selector="id/text()")
            subacc = IntegerType(selector="subaccount/text()")
            status = StringType(selector="status/text()")
            date = IntegerType(selector="date/text()")
            level = IntegerType(selector="level/text()", optional=True)

        mxml = MapXml()
        mxml.load(TEST_XML)
        res = mxml.map(Item)

        self.assertEqual(1, len(res))
        self.assertEqual("f4373d1c56c278f70568f8ba0e9bdab3", res[0]["item_id"])
        self.assertEqual(1234, res[0]["subacc"])
        self.assertEqual("wait", res[0]["status"])
        self.assertEqual(1371801875, res[0]["date"])
        self.assertEqual(None, res[0]["level"])

        # SPEC: It should support custom root name.
        # SPEC: Case 2.
        class Stat(object):
            item_id = StringType(selector="id/text()")
            subacc = IntegerType(selector="subaccount/text()")
            status = StringType(selector="status/text()")
            date = IntegerType(selector="date/text()")

            meta = {"root": "item"}

        mxml = MapXml()
        mxml.load(TEST_XML)
        res = mxml.map(Stat)

        self.assertEqual(1, len(res))
        self.assertEqual("f4373d1c56c278f70568f8ba0e9bdab3", res[0]["item_id"])
        self.assertEqual(1234, res[0]["subacc"])
        self.assertEqual("wait", res[0]["status"])
        self.assertEqual(1371801875, res[0]["date"])

        # SPEC: It should support conditional root parsing.
        # SPEC: Case 3.
        class Stat(object):
            item_id = StringType(selector="id/text()")
            subacc = IntegerType(selector="subaccount/text()")
            status = StringType(selector="status/text()")
            date = IntegerType(selector="date/text()")

            meta = {"root": "item", "condition": "status='cancel'"}

        mxml = MapXml()
        mxml.load(TEST_XML_2)
        res = mxml.map(Stat)

        self.assertEqual(1, len(res))
        self.assertEqual("f4373d1c56c278f70568f8ba0e9bdab3", res[0]["item_id"])
        self.assertEqual(9877, res[0]["subacc"])
        self.assertEqual("cancel", res[0]["status"])
        self.assertEqual(1371801875, res[0]["date"])

        # SPEC: It should support custom value converters.
        # SPEC: Case 4.
        class Stat(object):
            item_id = StringType(selector="id/text()")
            subacc = IntegerType(selector="subaccount/text()")
            status = StringType(selector="status/text()")
            date = IntegerType(selector="date/text()", converter=lambda x: datetime.fromtimestamp(float(x)))

            meta = {"root": "item", "condition": "status='cancel'"}

        mxml = MapXml()
        mxml.load(TEST_XML_2)
        res = mxml.map(Stat)

        self.assertEqual(1, len(res))
        self.assertEqual("f4373d1c56c278f70568f8ba0e9bdab3", res[0]["item_id"])
        self.assertEqual(9877, res[0]["subacc"])
        self.assertEqual("cancel", res[0]["status"])
        self.assertEqual(datetime, type(res[0]["date"]))
        self.assertEqual(21, res[0]["date"].day)
        self.assertEqual(6, res[0]["date"].month)
        self.assertEqual(2013, res[0]["date"].year)
        self.assertEqual(11, res[0]["date"].hour)
        self.assertEqual(4, res[0]["date"].minute)
        self.assertEqual(35, res[0]["date"].second)

        # SPEC: It should support custom value converters.
        # SPEC: Case 5.
        class Stat(object):
            item_id = StringType(selector="id/text()")
            subacc = IntegerType(selector="subaccount/text()")
            status = StringType(selector="status/text()")
            date = IntegerType(selector="date/text()",
                               converter=lambda x: datetime.fromtimestamp(float(x)).strftime("%d-%m-%Y_%H:%M:%S"))

            meta = {"root": "item", "condition": "status='cancel'"}

        mxml = MapXml()
        mxml.load(TEST_XML_2)
        res = mxml.map(Stat)

        self.assertEqual(1, len(res))
        self.assertEqual("f4373d1c56c278f70568f8ba0e9bdab3", res[0]["item_id"])
        self.assertEqual(9877, res[0]["subacc"])
        self.assertEqual("cancel", res[0]["status"])
        self.assertEqual(str, type(res[0]["date"]))
        self.assertEqual("21-06-2013_11:04:35", res[0]["date"])

        # SPEC: It should not parse whole element if field is missing and is not marked as optional.
        # SPEC: Case 6.
        class Stat(object):
            item_id = StringType(selector="id/text()")
            subacc = IntegerType(selector="subaccount/text()")
            status = StringType(selector="status/text()")
            date = IntegerType(selector="date/text()",
                               converter=lambda x: datetime.fromtimestamp(float(x)).strftime("%d-%m-%Y_%H:%M:%S"))

            meta = {"root": "item"}

        mxml = MapXml()
        mxml.load(TEST_XML_3)
        res = mxml.map(Stat)

        self.assertEqual(1, len(res))
        self.assertEqual("f4373d1c56c278f70568f8ba0e9bdab3", res[0]["item_id"])
        self.assertEqual(9877, res[0]["subacc"])
        self.assertEqual("cancel", res[0]["status"])
        self.assertEqual(str, type(res[0]["date"]))
        self.assertEqual("21-06-2013_11:04:35", res[0]["date"])

        # SPEC: It should support HTML markup.
        # SPEC: Case 7.
        class Product(object):
            price = IntegerType(selector="span[@id='price']/text()")
            brand = StringType(selector="label[@id='brand']/text()")
            meta = {"root": "div", "condition": "@class='product'"}

        mxml = MapXml(html_markup=True)
        mxml.load(TEST_HTML_1)
        res = mxml.map(Product)

        self.assertEqual(2, len(res))
        self.assertEqual(1000, res[0]['price'])
        self.assertEqual(2000, res[1]['price'])
        self.assertEqual('Thing', res[0]['brand'])
        self.assertEqual('Thing2', res[1]['brand'])