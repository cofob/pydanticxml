from pydantic_xmlmodel.xmlmodel import XMLModel


class ExampleModelLevel2(XMLModel):
    __xml_name__ = "level2"
    name: str
    value: int


class ExampleModelLevel1(XMLModel):
    __xml_name__ = "level1"
    level2: ExampleModelLevel2
    value: int


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
