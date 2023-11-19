"""Convertation between pydantic and xml."""

from logging import getLogger
from typing import (
    Any,
    Dict,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from xml.etree.ElementTree import Element, SubElement, fromstring, tostring

from pydantic import BaseModel

_T = TypeVar("_T", bound="BaseModel")

logger = getLogger(__name__)


def _issubclass_safe(cls: Any, classinfo: Any) -> bool:  # pragma: no cover
    """Safe version of issubclass that doesn't raise an exception if the first argument is not a class."""
    try:
        return issubclass(cls, classinfo)
    except TypeError:
        return False


def _get_basemodel_name(_class: Type[BaseModel]) -> str:
    """Get the name of the base model."""
    if hasattr(_class, "__xml_name__"):
        return _class.__xml_name__
    if hasattr(_class, "model_config"):
        name = _class.model_config.get("xml_name")
        if name is not None and isinstance(name, str):
            return name
    return _class.__name__


def _analyze_sequence(origin: Any, args: Tuple[Any, ...]) -> bool:
    """Analyze the sequence annotation of a field."""
    logger.debug("analyzing sequence: origin: %s, args: %s", origin, args)
    if _issubclass_safe(origin, Sequence):
        if not args:
            raise ValueError(
                "Invalid list type, must be a list of basemodels (no type args)"
            )
        for list_arg in args:
            if not _issubclass_safe(list_arg, BaseModel):
                raise ValueError(
                    "Invalid list type, must be a list of basemodels (type args is not a basemodel)"
                )
        return True
    return False


def _analyze_annotation(origin: Any, args: Tuple[Any, ...]) -> Tuple[bool, bool]:
    """Analyze the annotation of a field."""
    logger.debug("analyzing annotation: origin: %s, args: %s", origin, args)
    is_list = False
    is_basemodel = False
    if origin is Union:
        for union_arg in args:
            if _issubclass_safe(union_arg, BaseModel):
                is_basemodel = True
            elif _analyze_sequence(get_origin(union_arg), get_args(union_arg)):
                is_list = True
                is_basemodel = True
    elif _issubclass_safe(origin, str):
        pass
    elif _analyze_sequence(origin, args):
        is_list = True
        is_basemodel = True
    elif _issubclass_safe(origin, BaseModel):
        is_basemodel = True

    logger.debug("is_list: %s, is_basemodel: %s", is_list, is_basemodel)
    return is_list, is_basemodel


def _find_basemodel_types(origin: Any, args: Tuple[Any, ...]) -> Set[Type[BaseModel]]:
    """Find the basemodel types in an annotation."""
    ret = set()

    if origin is Union:
        for arg in args:
            if _issubclass_safe(arg, BaseModel):
                ret.add(arg)
        return ret
    elif _issubclass_safe(origin, Sequence):
        if not args:
            raise ValueError(
                "Invalid list type, must be a list of basemodels (no type args)"
            )
        for list_arg in args:
            if _issubclass_safe(list_arg, BaseModel):
                ret.add(list_arg)
        return ret
    elif _issubclass_safe(origin, BaseModel):
        return {origin}

    return ret


def model_dump_xml(
    model: BaseModel,
    include_xml_version: bool = False,
    by_alias: bool = False,
    submodel_by_alias: bool = False,
) -> str:
    """Convert a Pydantic model to XML.

    Args:
        model: The Pydantic model to convert.
        include_xml_version: Whether to include the XML version in the XML string.
        by_alias: Whether to use the alias in the XML string.
        submodel_by_alias: Whether to use the alias in the XML string for submodels.

    Returns:
        The XML string.
    """
    root = Element(_get_basemodel_name(type(model)))

    def select_name(name: str, alias: Optional[str]) -> str:
        if by_alias and alias is not None:
            return alias
        return name

    def select_submodel_name(name: str, alias: Optional[str]) -> str:
        if submodel_by_alias and alias is not None:
            return alias
        return name

    def convert_to_xml(element: Element, obj: BaseModel) -> None:
        """Inner function to convert a pydantic model to xml."""
        logger.debug("converting (%s) %s to xml", obj.__class__.__name__, obj)
        for name, field in obj.model_fields.items():
            value = getattr(obj, name)

            if field.annotation is None:
                raise ValueError(f"Field {name} has no annotation")
            origin: Any = get_origin(field.annotation)
            if origin is None:
                origin = field.annotation
            args: Tuple[Any, ...] = get_args(field.annotation)

            logger.debug(
                "field name: %(name)s, field: %(field)s, origin: %(origin)s, args: %(args)s",
                {"name": name, "field": field, "origin": origin, "args": args},
            )

            is_xml_content = name == "xml_content"
            is_list, _ = _analyze_annotation(origin, args)

            if is_list:
                if value is None:
                    continue
                for single_value in value:
                    if isinstance(single_value, BaseModel):
                        name = _get_basemodel_name(type(single_value))
                        sub_element = SubElement(
                            element,
                            select_submodel_name(name, field.serialization_alias),
                        )
                        convert_to_xml(sub_element, single_value)
            else:
                if isinstance(value, BaseModel):
                    name = _get_basemodel_name(type(value))
                    sub_element = SubElement(
                        element, select_submodel_name(name, field.serialization_alias)
                    )
                    convert_to_xml(sub_element, value)
                else:
                    if value is None:
                        continue
                    if is_xml_content:
                        element.text = str(value)
                    else:
                        element.set(
                            select_name(name, field.serialization_alias), str(value)
                        )

    convert_to_xml(root, model)
    xml_string = tostring(root, encoding="unicode")

    if include_xml_version:
        xml_string = '<?xml version="1.0" ?>' + xml_string

    return xml_string


def model_validate_xml(model: Type[_T], xml_string: str, by_alias: bool = True) -> _T:
    """Convert an XML string to a pydantic model.

    Args:
        model: The Pydantic model to convert.
        xml_string: The XML string.
        by_alias: Whether to use the alias in the XML string.

    Returns:
        The Pydantic model.
    """
    root = fromstring(xml_string)

    def convert_from_xml(element: Element, obj: Type[BaseModel]) -> Dict[str, Any]:
        """Inner function to convert an xml element to a pydantic model."""
        logger.debug("converting xml element to model: %s", element)
        logger.debug(
            "element.tag: %s, element.text: %s, element.attrib: %s",
            element.tag,
            element.text,
            element.attrib,
        )

        data: Dict[str, Any] = {}

        for name, field in obj.model_fields.items():
            if field.annotation is None:
                raise ValueError(f"Field {name} has no annotation")
            origin: Any = get_origin(field.annotation)
            if origin is None:
                origin = field.annotation
            args: Tuple[Any, ...] = get_args(field.annotation)

            logger.debug(
                "field name: %(name)s, field: %(field)s, origin: %(origin)s, args: %(args)s",
                {"name": name, "field": field, "origin": origin, "args": args},
            )

            is_list, is_basemodel = _analyze_annotation(origin, args)
            is_xml_content = name == "xml_content"

            if by_alias:
                temp_name = field.validation_alias or name
                if not isinstance(temp_name, str):
                    raise ValueError(f"Field {name} type is not a string")
                name = temp_name

            if is_basemodel and not is_list:
                logger.debug("is_basemodel and not is_list")
                basemodel_types = _find_basemodel_types(origin, args)
                if not basemodel_types:
                    raise ValueError(f"Field {name} has no basemodel types")
                for basemodel_type in basemodel_types:
                    sub_element = element.find(_get_basemodel_name(basemodel_type))
                    logger.debug("sub_element: %s", sub_element)
                    if sub_element is None:
                        continue
                    data[name] = convert_from_xml(sub_element, basemodel_type)
            elif is_basemodel and is_list:
                logger.debug("is_basemodel and is_list")
                basemodel_types = _find_basemodel_types(origin, args)
                if not basemodel_types:
                    raise ValueError(f"Field {name} has no basemodel type")
                data[name] = []
                for basemodel_type in basemodel_types:
                    logger.debug("searching basemodel type: %s", basemodel_type)
                    sub_elements = element.findall(_get_basemodel_name(basemodel_type))
                    data[name] += [
                        convert_from_xml(sub_element, basemodel_type)
                        for sub_element in sub_elements
                    ]
            else:
                logger.debug("not is_basemodel")
                if is_xml_content:
                    value = element.text
                else:
                    value = element.get(name)
                if value is None:
                    continue
                data[name] = value

        logger.debug("data: %s", data)
        return data

    obj = convert_from_xml(root, model)

    return model.model_validate(obj)
