from typing import List
from xml.etree.ElementTree import ParseError

import pytest
from pydantic import BaseModel, Field, ValidationError

from pydantic_xmlmodel.xmlmodel import XMLModel


class ExampleModel(XMLModel):
    __xml_name__ = "example"
    name: str
    value: int


class ExampleModelWithContent(XMLModel):
    __xml_name__ = "example"
    xml_content: str = "content"
    name: str
    value: int


class PydanticModel(BaseModel):
    name: str
    value: int


class ExampleModelWithPydantic(XMLModel):
    __xml_name__ = "example"
    value: PydanticModel


class ExampleModelLevel2(XMLModel):
    __xml_name__ = "level2"
    name: str
    value: int


class ExampleModelLevel1(XMLModel):
    __xml_name__ = "level1"
    level2: ExampleModelLevel2
    value: int


class ExampleModelWithMetaXmlName(XMLModel, xml_name="example"):
    name: str
    value: int


class ExampleModelWithXmlNameFunc(XMLModel):
    __xml_name_function__ = lambda s: s.upper()


class ExampleModelWithXmlNameFuncNone(XMLModel):
    __xml_name_function__ = None


class ExampleModelEmpty(XMLModel, xml_name="test"):
    pass


class ExampleModelWithSameNameInAttrAndChild(XMLModel, xml_name="test2"):
    test: str
    test_model: ExampleModelEmpty


class XmlContentRenameModel(XMLModel, xml_name="testmodel"):
    xml_content: str = Field(alias="test")


class XmlContentNonStrTypeModel(XMLModel, xml_name="test"):
    xml_content: int


class XmlContentListInnnerModel(XMLModel, xml_name="test_inner"):
    xml_content: str


class XmlContentListModel(XMLModel, xml_name="test"):
    xml_content: List[XmlContentListInnnerModel]


class XmlAttrList1Model(XMLModel, xml_name="list1"):
    xml_content: str = ""


class XmlAttrList2Model(XMLModel, xml_name="list2"):
    xml_content: str = ""


class XmlAttrListModel(XMLModel, xml_name="test"):
    list1: List[XmlAttrList1Model]
    list2: List[XmlAttrList2Model]


class XmlAttrListAndContentModel(XMLModel, xml_name="test"):
    xml_content: List[XmlContentListInnnerModel]
    list1: List[XmlAttrList1Model]
    list2: List[XmlAttrList2Model]


def test_xml_attr_and_content_list() -> None:
    # Arrange
    model = XmlAttrListAndContentModel(
        xml_content=[XmlContentListInnnerModel(xml_content=str(i)) for i in range(3)],
        list1=[XmlAttrList1Model(xml_content=str(i)) for i in range(3)],
        list2=[XmlAttrList2Model(xml_content=str(i)) for i in range(3)],
    )

    # Act
    result = model.to_xml()

    # Assert
    assert (
        "<test><list1>0</list1><list1>1</list1><list1>2</list1><list2>0</list2><list2>1</list2><list2>2</list2><test_inner>0</test_inner><test_inner>1</test_inner><test_inner>2</test_inner></test>"
        in result
    )


def test_xml_attr_and_content_list_load() -> None:
    # Arrange
    xml = "<test><list1>0</list1><list1>1</list1><list1>2</list1><list2>0</list2><list2>1</list2><list2>2</list2><test_inner>0</test_inner><test_inner>1</test_inner><test_inner>2</test_inner></test>"

    # Act
    model = XmlAttrListAndContentModel.from_xml(xml)

    # Assert
    assert len(model.list1) == 3
    assert model.list1[0].xml_content == "0"
    assert model.list1[1].xml_content == "1"
    assert model.list1[2].xml_content == "2"
    assert len(model.list2) == 3
    assert model.list2[0].xml_content == "0"
    assert model.list2[1].xml_content == "1"
    assert model.list2[2].xml_content == "2"
    assert len(model.xml_content) == 3
    assert model.xml_content[0].xml_content == "0"
    assert model.xml_content[1].xml_content == "1"
    assert model.xml_content[2].xml_content == "2"


def test_xml_attr_list() -> None:
    # Arrange
    model = XmlAttrListModel(
        list1=[XmlAttrList1Model(xml_content=str(i)) for i in range(3)],
        list2=[XmlAttrList2Model(xml_content=str(i)) for i in range(3)],
    )

    # Act
    result = model.to_xml()

    # Assert
    assert (
        "<test><list1>0</list1><list1>1</list1><list1>2</list1><list2>0</list2><list2>1</list2><list2>2</list2></test>"
        in result
    )


def test_xml_attr_list_load() -> None:
    # Arrange
    xml = "<test><list1>0</list1><list1>1</list1><list1>2</list1><list2>0</list2><list2>1</list2><list2>2</list2></test>"

    # Act
    model = XmlAttrListModel.from_xml(xml)

    # Assert
    assert len(model.list1) == 3
    assert model.list1[0].xml_content == "0"
    assert model.list1[1].xml_content == "1"
    assert model.list1[2].xml_content == "2"
    assert len(model.list2) == 3
    assert model.list2[0].xml_content == "0"
    assert model.list2[1].xml_content == "1"
    assert model.list2[2].xml_content == "2"


def test_xml_content_list() -> None:
    # Arrange
    model = XmlContentListModel(
        xml_content=[XmlContentListInnnerModel(xml_content=str(i)) for i in range(3)]
    )

    # Act
    result = model.to_xml()

    # Assert
    assert (
        "<test><test_inner>0</test_inner><test_inner>1</test_inner><test_inner>2</test_inner></test>"
        in result
    )


def test_xml_content_list_load() -> None:
    # Arrange
    xml = "<test><test_inner>0</test_inner><test_inner>1</test_inner><test_inner>2</test_inner></test>"

    # Act
    model = XmlContentListModel.from_xml(xml)

    # Assert
    assert len(model.xml_content) == 3
    assert model.xml_content[0].xml_content == "0"
    assert model.xml_content[1].xml_content == "1"
    assert model.xml_content[2].xml_content == "2"


def test_xml_content_rename() -> None:
    # Arrange
    model = XmlContentRenameModel(test="test")

    # Act
    result = model.to_xml()

    # Assert
    assert "<testmodel>test</testmodel>" in result


def test_xml_content_rename_load() -> None:
    # Arrange
    xml = "<testmodel>test</testmodel>"

    # Act
    model = XmlContentRenameModel.from_xml(xml)

    # Assert
    assert model.xml_content == "test"


def test_xml_content_non_str_type() -> None:
    # Arrange
    model = XmlContentNonStrTypeModel(xml_content=1)

    # Act
    result = model.to_xml()

    # Assert
    assert "<test>1</test>" in result


def test_xml_content_non_str_type_load() -> None:
    # Arrange
    xml = "<test>1</test>"

    # Act
    model = XmlContentNonStrTypeModel.from_xml(xml)

    # Assert
    assert model.xml_content == 1


# Test the `to_xml` method
def test_to_xml() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.to_xml()

    # Assert
    assert '<example name="test" value="123"/>' in result


# Test the `from_xml` method
def test_from_xml() -> None:
    # Arrange
    xml = '<example name="test" value="123"/>'

    # Act
    model = ExampleModel.from_xml(xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


# Test that the `from_xml` method raises an error for invalid XML
def test_from_xml_invalid_xml() -> None:
    # Arrange
    xml = "<invalid>"

    # Act and assert
    with pytest.raises(Exception):
        ExampleModel.from_xml(xml)


# Test the `__xml_name__` attribute
def test_xml_name() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.to_xml()

    # Assert
    assert "<example" in result


def test_xml_content() -> None:
    # Arrange
    model = ExampleModelWithContent(name="test", value=123)

    # Act
    result = model.to_xml()

    # Assert
    assert (
        '<?xml version="1.0" ?><example name="test" value="123">content</example>'
        in result
    )


def test_xml_content_load() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><example name="test" value="123">content modified</example>'

    # Act
    model = ExampleModelWithContent.from_xml(xml)

    # Assert
    assert model.xml_content == "content modified"


def test_xml_content_set_init() -> None:
    # Arrange
    model = ExampleModelWithContent(
        name="test", value=123, xml_content="content modified"
    )

    # Act
    result = model.to_xml()

    # Assert
    assert (
        '<?xml version="1.0" ?><example name="test" value="123">content modified</example>'
        in result
    )


def test_xml_content_set() -> None:
    # Arrange
    model = ExampleModelWithContent(name="test", value=123)
    model.xml_content = "content modified"

    # Act
    result = model.to_xml()

    # Assert
    assert (
        '<?xml version="1.0" ?><example name="test" value="123">content modified</example>'
        in result
    )


# Test for empty XML
def test_from_xml_empty_xml() -> None:
    # Arrange
    xml = ""

    # Act and assert
    with pytest.raises(ParseError):
        ExampleModel.from_xml(xml)


# Test for XML with missing attributes
def test_from_xml_missing_attributes() -> None:
    # Arrange
    xml = '<example name="test"/>'

    # Act and assert
    with pytest.raises(ValidationError):
        ExampleModel.from_xml(xml)


# Test for XML with extra attributes
def test_from_xml_extra_attributes() -> None:
    # Arrange
    xml = '<example name="test" value="123" extra="extra"/>'

    # Act
    model = ExampleModel.from_xml(xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


# Test for large XML input
def test_from_xml_large_input() -> None:
    # Arrange
    xml = '<example name="{}" value="123"/>'.format("a" * 100000)

    # Act
    model = ExampleModel.from_xml(xml)

    # Assert
    assert model.name == "a" * 100000
    assert model.value == 123


# Test for XML with special characters in attribute values
def test_from_xml_special_characters() -> None:
    # Arrange
    xml = '<example name="test&test" value="123"/>'

    # Act and assert
    with pytest.raises(ParseError):
        ExampleModel.from_xml(xml)


def test_to_xml_with_indent() -> None:
    # Arrange
    model = ExampleModelLevel1(
        level2=ExampleModelLevel2(name="test", value=123), value=456
    )

    # Act
    result = model.to_xml(indent=2)

    # Assert
    assert (
        '<?xml version="1.0" ?>\n'
        '<level1 value="456">\n'
        '  <level2 name="test" value="123"/>\n'
        "</level1>\n"
    ) == result


def test_to_xml_with_level() -> None:
    # Arrange
    model = ExampleModelLevel1(
        level2=ExampleModelLevel2(name="test", value=123), value=456
    )

    # Act
    result = model.to_xml()

    # Assert
    assert (
        '<?xml version="1.0" ?><level1 value="456"><level2 name="test" value="123"/></level1>'
        == result
    )


def test_from_xml_with_level() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><level1 value="456"><level2 name="test" value="123"/></level1>'

    # Act
    model = ExampleModelLevel1.from_xml(xml)

    # Assert
    assert model.value == 456
    assert model.level2.name == "test"
    assert model.level2.value == 123


def test_to_xml_with_pydantic_model() -> None:
    # Arrange
    model = ExampleModelWithPydantic(value=PydanticModel(name="test", value=123))

    # Act
    result = model.to_xml()

    # Assert
    assert (
        '<?xml version="1.0" ?><example><PydanticModel name="test" value="123"/></example>'
        == result
    )


# Don't support this yet
# def test_from_xml_with_pydantic_model() -> None:
#     # Arrange
#     xml = '<?xml version="1.0" ?><example><PydanticModel name="test" value="123"/></example>'

#     # Act
#     model = ExampleModelWithPydantic.from_xml(xml)

#     # Assert
#     assert model.value.name == "test"
#     assert model.value.value == 123


def test_to_xml_without_xml_version() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.to_xml(include_xml_version=False)

    # Assert
    assert '<example name="test" value="123"/>' == result


def test_to_xml_with_meta_xml_name() -> None:
    # Arrange
    model = ExampleModelWithMetaXmlName(name="test", value=123)

    # Act
    result = model.to_xml()

    # Assert
    assert '<example name="test" value="123"/>' in result


def test_to_xml_with_xml_name_func() -> None:
    # Arrange
    model = ExampleModelWithXmlNameFunc()

    # Act
    result = model.to_xml()

    # Assert
    assert "<EXAMPLEMODELWITHXMLNAMEFUNC/>" in result


def test_to_xml_with_xml_name_func_none() -> None:
    # Arrange
    model = ExampleModelWithXmlNameFuncNone()

    # Act
    result = model.to_xml()

    # Assert
    assert "<ExampleModelWithXmlNameFuncNone/>" in result


def test_from_xml_with_same_attr() -> None:
    # Arrange
    model = ExampleModelWithSameNameInAttrAndChild(
        test="test str", test_model=ExampleModelEmpty()
    )

    # Act
    result = ExampleModelWithSameNameInAttrAndChild.from_xml(model.to_xml())

    # Assert
    assert result.to_xml() == model.to_xml()
