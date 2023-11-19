"""A module that contains the XMLModel class."""

from typing import Any, Optional, Type, TypeVar, no_type_check
import warnings

from pydantic import BaseModel, ConfigDict
from pydantic._internal._model_construction import ModelMetaclass
from typing_extensions import deprecated

from pydantic_xmlmodel.serde import model_dump_xml as convert_model_to_xml
from pydantic_xmlmodel.serde import model_validate_xml as convert_xml_to_model

_S = TypeVar("_S")


class XMLModelMeta(ModelMetaclass):
    """A metaclass for XMLModel.

    It's a subclass of `ModelMetaclass` (the metaclass of `pydantic.BaseModel`).

    It adds the following class attributes to XMLModel:
        - `__xml_name__`: The name of the XML element. If not specified, the name of the class is used.
    """

    @no_type_check
    def __new__(cls, name, bases, attrs, **kwargs):
        """Add the following class attributes to XMLModel.

        - xml_name: The name of the XML element. If not specified, the name of the class is used.
        """
        xml_name = kwargs.pop("xml_name", None)
        if xml_name is not None:
            attrs["__xml_name__"] = xml_name

        return super().__new__(cls, name, bases, attrs, **kwargs)


@deprecated("Use `BaseModelXML` instead.")
class XMLModel(BaseModel, metaclass=XMLModelMeta):
    """A Pydantic model that can be converted to and from XML.

    It's a subclass of `BaseModel` (the base model of `pydantic.BaseModel`).

    It adds the following class attributes to XMLModel:
        - `__xml_name__`: The name of the XML element. If not specified, the name of the class is used.
        - `xml_content`: The content of the XML element inside `<element>{{xml_content}}</element>`. If not
          specified, the element will not have any content.

    This class is deprecated. Use `BaseModelXML` instead, because it supports type checking with mypy.
    """

    __xml_name__: Optional[str] = None
    """The name of the XML element. If not specified, the name of the class is used."""

    xml_content: Optional[Any] = None
    """The content of the XML element inside `<element>{{xml_content}}</element>`. If not specified, the element will
    not have any content."""

    @deprecated("Use `model_dump_xml()` instead.")
    def to_xml(
        self,
        include_xml_version: bool = True,
        by_alias: bool = False,
        submodel_by_alias: bool = False,
        indent: Optional[int] = None,
    ) -> str:
        """Convert the model to XML string.

        Deprecated. Use `model_dump_xml()` instead.

        Args:
            include_xml_version: Whether to include the XML version in the XML string.
            by_alias: Whether to use the alias in the XML string.
            submodel_by_alias: Whether to use the alias in the XML string for submodels.
            indent: The indentation level. Deprecated and has no effect.

        Returns:
            The XML string.
        """
        if indent is not None:
            warnings.warn("`indent` is deprecated and is ignored.", DeprecationWarning)
        return convert_model_to_xml(
            self,
            include_xml_version=include_xml_version,
            by_alias=by_alias,
            submodel_by_alias=submodel_by_alias,
        )

    def model_dump_xml(
        self,
        include_xml_version: bool = True,
        by_alias: bool = False,
        submodel_by_alias: bool = False,
    ) -> str:
        """Convert the model to XML string.

        Args:
            include_xml_version: Whether to include the XML version in the XML string.
            by_alias: Whether to use the alias in the XML string.
            submodel_by_alias: Whether to use the alias in the XML string for submodels.

        Returns:
            The XML string.
        """
        return convert_model_to_xml(
            self,
            include_xml_version=include_xml_version,
            by_alias=by_alias,
            submodel_by_alias=submodel_by_alias,
        )

    @classmethod
    @deprecated("Use `model_validate_xml()` instead.")
    def from_xml(cls: Type[_S], xml_string: str, by_alias: bool = True) -> _S:
        """Convert an XML string to a model.

        Deprecated. Use `model_validate_xml()` instead.

        Args:
            xml_string: The XML string.
            by_alias: Whether to use the alias in the XML string.

        Returns:
            The model.
        """
        return convert_xml_to_model(cls, xml_string, by_alias=by_alias)  # type: ignore[type-var]

    @classmethod
    def model_validate_xml(cls: Type[_S], xml_string: str, by_alias: bool = True) -> _S:
        """Convert an XML string to a model.

        Args:
            xml_string: The XML string.
            by_alias: Whether to use the alias in the XML string.

        Returns:
            The model.
        """
        return convert_xml_to_model(cls, xml_string, by_alias=by_alias)  # type: ignore[type-var]


class XMLConfigDict(ConfigDict, total=False):
    """A ConfigDict for BaseModelXML.

    It's a subclass of `ConfigDict` (the config dict of `pydantic.BaseModel`).

    It adds the following class attributes to XMLConfigDict:
        - `xml_name`: The name of the XML element. If not specified, the name of the class is used.
    """

    xml_name: str


class BaseModelXML(BaseModel):
    """A Pydantic model that can be converted to and from XML.

    It's a subclass of `BaseModel` (the base model of `pydantic.BaseModel`).

    It adds the following class attributes to BaseModelXML:
        - `xml_content`: The content of the XML element inside `<element>{{xml_content}}</element>`. If not
          specified, the element will not have any content.

    You can change the name of the XML element using the `model_config` via the `XMLConfigDict`.
    """

    model_config = XMLConfigDict()
    """Model configuration."""

    xml_content: Optional[Any] = None
    """The content of the XML element inside `<element>{{xml_content}}</element>`. If not specified, the element will
    not have any content."""

    def model_dump_xml(
        self,
        include_xml_version: bool = True,
        by_alias: bool = False,
        submodel_by_alias: bool = False,
    ) -> str:
        """Convert the model to XML string.

        Args:
            include_xml_version: Whether to include the XML version in the XML string.
            by_alias: Whether to use the alias in the XML string.
            submodel_by_alias: Whether to use the alias in the XML string for submodels.

        Returns:
            The XML string.
        """
        return convert_model_to_xml(
            self,
            include_xml_version=include_xml_version,
            by_alias=by_alias,
            submodel_by_alias=submodel_by_alias,
        )

    @classmethod
    def model_validate_xml(cls: Type[_S], xml_string: str, by_alias: bool = True) -> _S:
        """Convert an XML string to a model.

        Args:
            xml_string: The XML string.
            by_alias: Whether to use the alias in the XML string.

        Returns:
            The model.
        """
        return convert_xml_to_model(cls, xml_string, by_alias=by_alias)  # type: ignore[type-var]
