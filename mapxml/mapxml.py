# coding=utf
import inspect
from StringIO import StringIO

from lxml import etree


# region Field types.


class BaseFieldType(object):
    """
    Provides base for value types.
    """

    def __init__(self, selector=None, multiple=False,
                 object_type=None, optional=False, converter=None):
        """
        Constructor.
        """
        self.selector = selector
        self.optional = optional
        self.multiple = multiple
        self.object_type = object_type
        self.converter = converter

    def convert(self, value=None):
        """
        Converts value.
        """
        raise NotImplementedError()


class StringType(BaseFieldType):
    """
    Represents String typed value.
    """

    def __init__(self, **kwargs):
        super(StringType, self).__init__(**kwargs)
        self.type_name = "string"

    def convert(self, value=None):
        if self.converter:
            return self.converter(value)
        return str(value).strip() if type(value) is not unicode else value.strip()


class UnicodeType(BaseFieldType):
    """
    Represents String typed value.
    """

    def __init__(self, **kwargs):
        super(UnicodeType, self).__init__(**kwargs)
        self.type_name = "unicode"

    def convert(self, value=None):
        if self.converter:
            return self.converter(value)
        return unicode(value).strip() if type(value) is not unicode else value.strip()


class BooleanType(BaseFieldType):
    """
    Represents String typed value.
    """

    def __init__(self, **kwargs):
        super(BooleanType, self).__init__(**kwargs)
        self.type_name = "boolean"

    def convert(self, value=None):
        if self.converter:
            return self.converter(value)

        bool_map = {
            "true": True,
            "false": False,
            "0": False,
            "1": True,
            1: True,
            0: False
        }

        return bool_map[value.lower()]


class FloatType(BaseFieldType):
    """
    Represents String typed value.
    """

    def __init__(self, **kwargs):
        super(FloatType, self).__init__(**kwargs)
        self.type_name = "float"

    def convert(self, value=None):
        if self.converter:
            return self.converter(value)
        return float(value)


class NodeType(BaseFieldType):
    """
    Represents String typed value.
    """

    def __init__(self, **kwargs):
        super(NodeType, self).__init__(**kwargs)
        self.type_name = "node"


class IntegerType(BaseFieldType):
    """
    Represents String typed value.
    """

    def __init__(self, **kwargs):
        super(IntegerType, self).__init__(**kwargs)
        self.type_name = "integer"

    def convert(self, value=None):
        if self.converter:
            return self.converter(value)
        return int(value)


# endregion


class MapXml(object):
    """
    MapXml provides flexible functionality for XML mapping.
    It allows loading XML from string, file, StriongIO & web resource.
    It allows to use rules & map any xml to any class model.
    """

    def __init__(self, html_markup=False):
        """
        Constructor.
        """
        self.field_types = [StringType, NodeType, IntegerType, UnicodeType, FloatType, BooleanType]
        self.xml_tree = None
        self.xml = None
        self.html = html_markup

    def __init_tree(self):
        """
        Initializes tree.
        """
        if self.xml_tree is None:
            if self.html:
                self.xml_tree = etree.parse(self.xml, parser=etree.HTMLParser())
            else:
                self.xml_tree = etree.parse(self.xml)

    def load(self, xml=None):
        """
        Loads XML.
        """
        self.xml = StringIO(xml)

    def __get_fields(self, model=None):
        """
        Gets fields from model.
        """
        return filter(lambda x: type(x[1]) in self.field_types, inspect.getmembers(model))

    @staticmethod
    def __get_meta(model=None):
        """
        Gets meta field from model.
        """
        meta_raw = filter(lambda x: x[0].strip() == "meta", model.__dict__.iteritems())
        if len(meta_raw) == 1:
            return meta_raw[0][1]
        return {}

    def __get_root_nodes(self, root_name=None, condition=None):
        """
        Gets root nodes.
        """
        if condition:
            root_name = "%s[%s]" % (root_name, condition)
        return self.xml_tree.xpath("//%s" % root_name)

    def __map_node(self, node=None, fields=None):
        """
        Maps fields to node.
        """
        result = {}

        for fname, fvalue in fields:
            if fvalue.multiple:
                result[fname] = []
                multiple_values = node.xpath(fvalue.selector)

                if len(multiple_values) <= 0 and fvalue.optional:
                    result[fname] = None
                elif len(multiple_values) <= 0 and not fvalue.optional:
                    return None
                else:
                    subfields = self.__get_fields(fvalue.object_type)
                    for subvalue in multiple_values:
                        result[fname].append(self.__map_node(subvalue, subfields))

            else:
                field_value = node.xpath(fvalue.selector)

                if len(field_value) <= 0 and fvalue.optional:
                    result[fname] = None
                elif len(field_value) <= 0 and not fvalue.optional:
                    return None
                else:
                    field_value = field_value[0]
                    if fvalue.type_name == "node":
                        subfields = self.__get_fields(fvalue.object_type)
                        result[fname] = self.__map_node(field_value, subfields)
                    else:
                        result[fname] = fvalue.convert(field_value)

        return result

    def map(self, model=None):
        """
        Maps loaded XML to given model class.
        """

        # Get model fields & lookup for root node.
        fields = self.__get_fields(model)
        meta = self.__get_meta(model)
        root_name = meta.get("root", model.__name__).lower()

        # Init LXML tree from XML source & get all root nodes.
        self.__init_tree()
        root_nodes = self.__get_root_nodes(root_name, meta.get("condition", None))

        # Map dictionaries.
        mapped_nodes = map(lambda x: self.__map_node(x, fields), root_nodes)
        mapped_nodes = filter(lambda x: x, mapped_nodes)

        # Return clean list.
        return mapped_nodes