from xml.etree.ElementTree import ParseError

import pytest
from pydantic import ValidationError

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
