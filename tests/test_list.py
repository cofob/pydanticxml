from typing import List

import pytest

from pydantic_xmlmodel.xmlmodel import XMLModel


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


class XmlListNonBaseModel(XMLModel, xml_name="test"):
    data: List[int]


class XmlContentListNonBaseModel(XMLModel, xml_name="test"):
    xml_content: List[int]


class XmlListEmptyModel(XMLModel, xml_name="test"):
    data: List


class XmlContentListEmptyModel(XMLModel, xml_name="test"):
    xml_content: List


def test_xml_list_empty() -> None:
    # Arrange
    model = XmlListEmptyModel(data=[1])

    # Act
    with pytest.raises(ValueError):
        model.to_xml()


def test_xml_list_empty_load() -> None:
    # Arrange
    xml = "<test><data>1</data></test>"

    # Act
    with pytest.raises(ValueError):
        XmlListEmptyModel.from_xml(xml)


def test_xml_content_list_empty():
    # Arrange
    model = XmlContentListEmptyModel(xml_content=[1])

    # Act
    with pytest.raises(ValueError):
        model.to_xml()


def test_xml_content_list_empty_load():
    # Arrange
    xml = "<test><data>1</data></test>"

    # Act
    with pytest.raises(ValueError):
        XmlContentListEmptyModel.from_xml(xml)


def test_raise_error_if_list_is_not_base_model() -> None:
    # Arrange
    model = XmlListNonBaseModel(data=[1, 2, 3])

    # Act
    with pytest.raises(ValueError):
        model.to_xml()


def test_raise_error_if_list_is_not_base_model_load() -> None:
    # Arrange
    xml = "<test><data>1</data><data>2</data><data>3</data></test>"

    # Act
    with pytest.raises(ValueError):
        XmlListNonBaseModel.from_xml(xml)


def test_raise_error_if_list_is_not_base_model_content() -> None:
    # Arrange
    model = XmlContentListNonBaseModel(xml_content=[1, 2, 3])

    # Act
    with pytest.raises(ValueError):
        model.to_xml()


def test_raise_error_if_list_is_not_base_model_content_load() -> None:
    # Arrange
    xml = "<test><data>1</data><data>2</data><data>3</data></test>"

    # Act
    with pytest.raises(ValueError):
        XmlContentListNonBaseModel.from_xml(xml)


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
