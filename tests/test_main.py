from xml.etree.ElementTree import ParseError

import pytest
from pydantic import BaseModel, ValidationError

from pydantic_xmlmodel.serde import model_dump_xml, model_validate_xml
from pydantic_xmlmodel.xmlmodel import BaseModelXML, XMLConfigDict, XMLModel


class ExampleModel(XMLModel):
    __xml_name__ = "example"
    name: str
    value: int


class ExampleBaseModelXML(BaseModelXML):
    model_config = XMLConfigDict(xml_name="example")

    name: str
    value: int


class PydanticModel(BaseModel):
    name: str
    value: int


class ExampleModelWithPydantic(XMLModel):
    __xml_name__ = "example"
    value: PydanticModel


class ExampleModelWithMetaXmlName(XMLModel, xml_name="example"):
    name: str
    value: int


class ExampleModelEmpty(XMLModel, xml_name="test"):
    pass


class ExampleModelWithSameNameInAttrAndChild(XMLModel, xml_name="test2"):
    test: str
    test_model: ExampleModelEmpty


# Test the `to_xml` method
def test_to_xml() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.to_xml()

    # Assert
    assert '<example name="test" value="123" />' in result


# Test the `from_xml` method
def test_from_xml() -> None:
    # Arrange
    xml = '<example name="test" value="123"/>'

    # Act
    model = ExampleModel.from_xml(xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


# Test the `to_xml` method
def test_to_xml_new_method() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.model_dump_xml()

    # Assert
    assert '<example name="test" value="123" />' in result


# Test the `from_xml` method
def test_from_xml_new_method() -> None:
    # Arrange
    xml = '<example name="test" value="123"/>'

    # Act
    model = ExampleModel.model_validate_xml(xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


# Test the `to_xml` method with func
def test_to_xml_func() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model_dump_xml(model)

    # Assert
    assert '<example name="test" value="123" />' in result


# Test the `from_xml` method
def test_from_xml_func() -> None:
    # Arrange
    xml = '<example name="test" value="123"/>'

    # Act
    model = model_validate_xml(ExampleModel, xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


# Test the `to_xml` method with func
def test_to_xml_basemodel_xml() -> None:
    # Arrange
    model = ExampleBaseModelXML(name="test", value=123)

    # Act
    result = model_dump_xml(model)

    # Assert
    assert '<example name="test" value="123" />' in result


# Test the `from_xml` method
def test_from_xml_basemodel_xml() -> None:
    # Arrange
    xml = '<example name="test" value="123"/>'

    # Act
    model = model_validate_xml(ExampleBaseModelXML, xml)

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


def test_to_xml_with_pydantic_model_2() -> None:
    # Arrange
    model = PydanticModel(name="test", value=123)

    # Act
    result = model_dump_xml(model)

    # Assert
    assert '<PydanticModel name="test" value="123" />' in result


def test_from_xml_with_pydantic_model_2() -> None:
    # Arrange
    xml = '<PydanticModel name="test" value="123"/>'

    # Act
    model = model_validate_xml(PydanticModel, xml)

    # Assert
    assert model.name == "test"
    assert model.value == 123


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


# Test for XML with special characters in attribute values
def test_from_xml_special_characters() -> None:
    # Arrange
    xml = '<example name="test&test" value="123"/>'

    # Act and assert
    with pytest.raises(ParseError):
        ExampleModel.from_xml(xml)


def test_to_xml_with_pydantic_model() -> None:
    # Arrange
    model = ExampleModelWithPydantic(value=PydanticModel(name="test", value=123))

    # Act
    result = model.to_xml()

    # Assert
    assert (
        '<?xml version="1.0" ?><example><PydanticModel name="test" value="123" /></example>'
        == result
    )


def test_from_xml_with_pydantic_model() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><example><PydanticModel name="test" value="123"/></example>'

    # Act
    model = ExampleModelWithPydantic.from_xml(xml)

    # Assert
    assert model.value.name == "test"
    assert model.value.value == 123


def test_to_xml_without_xml_version() -> None:
    # Arrange
    model = ExampleModel(name="test", value=123)

    # Act
    result = model.to_xml(include_xml_version=False)

    # Assert
    assert '<example name="test" value="123" />' == result


def test_to_xml_with_meta_xml_name() -> None:
    # Arrange
    model = ExampleModelWithMetaXmlName(name="test", value=123)

    # Act
    result = model.to_xml()

    # Assert
    assert '<example name="test" value="123" />' in result


def test_from_xml_with_same_attr() -> None:
    # Arrange
    model = ExampleModelWithSameNameInAttrAndChild(
        test="test str", test_model=ExampleModelEmpty()
    )

    # Act
    result = ExampleModelWithSameNameInAttrAndChild.from_xml(model.to_xml())

    # Assert
    assert result.to_xml() == model.to_xml()
