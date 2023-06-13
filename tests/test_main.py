from xml.etree.ElementTree import ParseError

import pytest
from pydantic import BaseModel, ValidationError

from pydantic_xmlmodel.xmlmodel import XMLModel


class ExampleModel(XMLModel):
    __xml_name__ = "example"
    name: str
    value: int


class ExampleModelWithContent(XMLModel):
    __xml_name__ = "example"
    __xml_content__ = "content"
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
    assert model.__xml_content__ == "content modified"


def test_xml_content_set_init() -> None:
    # Arrange
    model = ExampleModelWithContent(
        name="test", value=123, __xml_content__="content modified"
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
    model.set_xml_content("content modified")

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
    print(result)

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
