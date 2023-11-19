from typing import Optional

import pytest
from pydantic import ValidationError

from pydantic_xmlmodel.xmlmodel import XMLModel


class InnerModel(XMLModel, xml_name="inner"):
    pass


class OuterModel(XMLModel, xml_name="outer"):
    inner: Optional[InnerModel] = None


class OuterModelRequired(XMLModel, xml_name="outer"):
    inner: Optional[InnerModel]


def test_none_with_none() -> None:
    # Arrange
    model = OuterModel(inner=None)

    # Act
    result = model.to_xml()

    # Assert
    assert '<?xml version="1.0" ?><outer />' == result


def test_none_filled() -> None:
    # Arrange
    model = OuterModel(inner=InnerModel())

    # Act
    result = model.to_xml()

    # Assert
    assert '<?xml version="1.0" ?><outer><inner /></outer>' == result


def test_none_with_none_load() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><outer/>'

    # Act
    model = OuterModel.from_xml(xml)

    # Assert
    assert model.inner is None


def test_none_with_none_load_required() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><outer/>'

    # Act
    with pytest.raises(ValidationError):
        OuterModelRequired.from_xml(xml)


def test_none_filled_load() -> None:
    # Arrange
    xml = '<?xml version="1.0" ?><outer><inner/></outer>'

    # Act
    model = OuterModel.from_xml(xml)

    # Assert
    assert model.inner is not None
    assert isinstance(model.inner, InnerModel)
