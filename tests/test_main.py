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


# Test the `dicttoxml` method
def test_dicttoxml() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.dicttoxml()

    # Assert
    assert '<example name="test" value="123"/>' in result


# Test the `fromxml` method
def test_fromxml() -> None:
    # Arrange
    xml = '<example name="test" value="123"/>'

    # Act
    model = ExampleModel.fromxml(xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


# Test that the `fromxml` method raises an error for invalid XML
def test_fromxml_invalid_xml() -> None:
    # Arrange
    xml = "<invalid>"

    # Act and assert
    with pytest.raises(Exception):
        ExampleModel.fromxml(xml)


# Test the `__xml_name__` attribute
def test_xml_name() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.dicttoxml()

    # Assert
    assert "<example" in result


def test_xml_content() -> None:
    # Arrange
    model = ExampleModelWithContent(name="test", value=123)

    # Act
    result = model.dicttoxml()

    # Assert
    assert (
        '<?xml version="1.0" ?><example name="test" value="123">content</example>'
        in result
    )


def test_xml_content_load() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><example name="test" value="123">content modified</example>'

    # Act
    model = ExampleModelWithContent.fromxml(xml)

    # Assert
    assert model.__xml_content__ == "content modified"


# Test for empty XML
def test_fromxml_empty_xml() -> None:
    # Arrange
    xml = ""

    # Act and assert
    with pytest.raises(ParseError):
        ExampleModel.fromxml(xml)


# Test for XML with missing attributes
def test_fromxml_missing_attributes() -> None:
    # Arrange
    xml = '<example name="test"/>'

    # Act and assert
    with pytest.raises(ValidationError):
        ExampleModel.fromxml(xml)


# Test for XML with extra attributes
def test_fromxml_extra_attributes() -> None:
    # Arrange
    xml = '<example name="test" value="123" extra="extra"/>'

    # Act
    model = ExampleModel.fromxml(xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


# Test for large XML input
def test_fromxml_large_input() -> None:
    # Arrange
    xml = '<example name="{}" value="123"/>'.format("a" * 100000)

    # Act
    model = ExampleModel.fromxml(xml)

    # Assert
    assert model.name == "a" * 100000
    assert model.value == 123


# Test for XML with special characters in attribute values
def test_fromxml_special_characters() -> None:
    # Arrange
    xml = '<example name="test&test" value="123"/>'

    # Act and assert
    with pytest.raises(ParseError):
        ExampleModel.fromxml(xml)
