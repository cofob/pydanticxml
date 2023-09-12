from pydantic import Field

from pydantic_xmlmodel.xmlmodel import XMLModel


class NamespaceInnerModel(XMLModel, xml_name="test:inner"):
    __xml_namespaces__ = {"test": "http://test.com"}


class NamespaceModel(XMLModel, xml_name="namespace"):
    xmlns_test = Field(default="http://test.com", alias="xmlns:test")
    inner: NamespaceInnerModel


def test_namespace() -> None:
    # Arrange
    model = NamespaceModel(inner=NamespaceInnerModel())

    # Act
    result = model.to_xml()

    # Assert
    assert (
        '<?xml version="1.0" ?><namespace xmlns:test="http://test.com"><test:inner/></namespace>'
        == result
    )


def test_namespace_load() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><namespace xmlns:test="http://test.com"><test:inner/></namespace>'

    # Act
    model = NamespaceModel.from_xml(xml)

    # Assert
    assert model.inner is not None
