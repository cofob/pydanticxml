from pydantic import Field

from pydantic_xmlmodel.xmlmodel import XMLModel


class ExampleModelWithContent(XMLModel):
    __xml_name__ = "example"
    xml_content: str = "content"
    name: str
    value: int


class XmlContentRenameModel(XMLModel, xml_name="testmodel"):
    xml_content: str = Field(alias="test")


class XmlContentNonStrTypeModel(XMLModel, xml_name="test"):
    xml_content: int


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
