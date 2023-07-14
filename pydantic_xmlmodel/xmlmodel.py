"""A module that contains the XMLModel class."""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, no_type_check
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, fromstring, tostring

from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass

T = TypeVar("T", bound="XMLModel")


def _issubclass_safe(cls: Any, classinfo: Any) -> bool:
    """Safe version of issubclass that doesn't raise an exception if the first argument is not a class."""
    try:
        return issubclass(cls, classinfo)
    except TypeError:
        return False


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


class XMLModel(BaseModel, metaclass=XMLModelMeta):
    """A base class for XML models.

    It's useful for converting a model to XML string (e.g. for libvirt XML manifests). It allows you to specify the name of the XML element and its content
    and supports nested XML elements. See `XMLModel.to_xml()` for examples.

    It's a subclass of `pydantic.BaseModel` and can be used as a regular model (and can be nested in other models).

    It's currently missing support for lists and dictionaries (it will be added as json attribute to the XML element).

    It adds the following class attributes to XMLModel:
        - `__xml_name__`: The name of the XML element. If not specified, the name of the class is used.
        - `__xml_name_function__`: A function that used if `__xml_name__` is not specified.
        - `xml_content`: The content of the XML element inside `<element>{{xml_content}}</element>`. If not specified, the element will not have any content.
    """

    __xml_name__: Optional[str] = None
    """The name of the XML element. If not specified, the name of the class is used."""

    __xml_name_function__: Optional[Callable[[str], str]] = lambda x: x.lower()
    """A function that used if `__xml_name__` is not specified.

    The function takes the name of the class and returns the name of the XML element. It makes the name lowercase by default.

    If None, the name of the class is used.

    Example:
        >>> class NewXMLModel(XMLModel):
        ...     __xml_name_function__ = lambda x: x.upper() # make the name uppercase
        ...
        >>> class ExampleSchema(NewXMLModel):
        ...     pass
        ...
        >>> ExampleSchema._get_xml_name()
        'EXAMPLESCHEMA'
    """

    xml_content: Optional[Any] = None
    """The content of the XML element inside `<element>{{xml_content}}</element>`. If not specified, the element will not have any content."""

    @classmethod
    def _get_xml_name(cls) -> str:
        """Return the name of the XML element."""
        if cls.__xml_name__ is not None:
            return cls.__xml_name__
        else:
            if cls.__xml_name_function__ is not None:
                return cls.__xml_name_function__(cls.__name__)
            return cls.__name__

    def to_xml(
        self,
        indent: Optional[int] = None,
        include_xml_version: bool = True,
        exclude_none=False,
    ) -> str:
        """Convert the model to XML string.

        Args:
            indent: If specified, the XML will be indented with the specified number of spaces.

        Returns:
            The XML string.

        Example:
            >>> class AnimalCharacteristics(XMLModel):
            ...     color: str = "black"
            ...     weight: int = 10
            ...     is_friendly: bool = True
            ...
            >>> class Cat(XMLModel):
            ...     animal_characteristics: AnimalCharacteristics
            ...     name: str = "Kitty"
            ...
            >>> Cat(
            ...     animal_characteristics=AnimalCharacteristics(),
            ...     name="Kitty"
            ... ).to_xml(indent=4)
            <?xml version="1.0" ?>
            <cat name="Kitty">
                <animal_characteristics color="black" is_friendly="true" weight="10"/>
            </cat>
        """

        def to_xml_innner(e: Element, obj: Any) -> None:
            """Convert the model to XML recursively."""
            # Iterate over the fields of the model and convert them to XML
            for field, _ in obj.dict().items():
                # We skip the xml_content field because we handle it separately
                if field == "xml_content":
                    continue
                # We get the value of the field using getattr() because the we need subclass of BaseModel, not just dict
                value = getattr(obj, field)
                # If the value is a BaseModel, we convert it to XML recursively
                if (
                    _issubclass_safe(obj.__fields__[field].type_, BaseModel)
                    and obj.__fields__[field].sub_fields is None
                ):
                    if obj.__fields__[field].allow_none and value is None:
                        continue
                    # Get the name of the XML element
                    name = value.__class__.__name__
                    if isinstance(value, XMLModel):
                        name = value._get_xml_name()
                    # Create the XML element and add it to the parent element
                    sub = SubElement(e, name)
                    # Convert the BaseModel to XML recursively
                    to_xml_innner(sub, value)
                elif obj.__fields__[field].sub_fields is not None:
                    # If the field is a list-like field but not a list of BaseModel, we raise an error
                    if not _issubclass_safe(
                        obj.__fields__[field].sub_fields[0].type_, BaseModel
                    ):
                        raise ValueError(
                            f"Field {field} is a list-like field but not a list of BaseModel"
                        )
                    # Iterate over the list and convert each item to XML recursively
                    for item in value:
                        # Get the name of the XML element
                        name = item.__class__.__name__
                        if isinstance(item, XMLModel):
                            name = item._get_xml_name()
                        # Create the XML element and add it to the parent element
                        sub = SubElement(e, name)
                        # Convert the BaseModel to XML recursively
                        to_xml_innner(sub, item)
                # Else, we add the value as an attribute
                else:
                    # Get the name of the XML attribute
                    pydantic_field = obj.__fields__[field]
                    # If the field has an alias, we use it as the name of the XML attribute
                    name = pydantic_field.name
                    if pydantic_field.alias is not None:
                        name = pydantic_field.alias
                    if not (exclude_none and value is None):
                        # Add the attribute to the XML element
                        e.set(name, str(value))
            # If the model has content, we add it to the XML element
            if isinstance(obj, XMLModel) and obj.xml_content is not None:
                xml_content_field = obj.__fields__["xml_content"]
                # if field is a list-like field but not a list of BaseModel, we raise an error
                if xml_content_field.sub_fields is not None and not _issubclass_safe(
                    xml_content_field.sub_fields[0].type_, BaseModel
                ):
                    raise ValueError(
                        f"xml_content field of {obj.__class__.__name__} must be a List[BaseModel]"
                    )
                # if field is a list-like field, we add each item as a separate XML element
                if xml_content_field.sub_fields is not None:
                    type_ = xml_content_field.sub_fields[0].type_
                    name = type_.__name__
                    if _issubclass_safe(type_, XMLModel):
                        name = type_._get_xml_name()
                    for item in obj.xml_content:
                        sub = SubElement(e, name)
                        to_xml_innner(sub, item)
                # else, we add the content as a text
                else:
                    e.text = str(obj.xml_content)

        # Create the root XML element
        root = Element(self._get_xml_name())
        # Convert the model to XML recursively
        to_xml_innner(root, self)
        # Convert the XML element to string
        #
        # I know it's not the best way to do it, but it's the only way I found to convert
        # the Element to Document. If you know a better way, please let me know.
        xml = parseString(tostring(root, encoding="unicode"))

        if not include_xml_version:
            # See https://stackoverflow.com/a/65516230
            xml = xml.childNodes[0]

        xml_str: str
        if indent is not None:
            xml_str = xml.toprettyxml(indent=" " * indent)
        else:
            xml_str = xml.toxml()

        return xml_str

    @classmethod
    def from_xml(cls: Type[T], xml: str) -> T:
        """Convert XML string to a model.

        Args:
            xml: The XML string.

        Returns:
            The model.

        Example:
            >>> class AnimalCharacteristics(XMLModel):
            ...     color: str = "black"
            ...     weight: int = 10
            ...     is_friendly: bool = True
            ...
            >>> class Cat(XMLModel):
            ...     animal_characteristics: AnimalCharacteristics
            ...     name: str = "Kitty"
            ...
            >>> cat = Cat.from_xml('''
            ... <?xml version="1.0" ?>
            ... <cat name="Kitty">
            ...     <animal_characteristics color="black" is_friendly="true" weight="10"/>
            ... </cat>
            ... ''')
            >>> cat
            Cat(animal_characteristics=AnimalCharacteristics(color='black', weight=10, is_friendly=True), name='Kitty')
        """

        def from_element(element: Element, model: Type[BaseModel]) -> Any:
            data: Dict[str, Any] = {}
            for field in model.__fields__:
                if field == "xml_content":
                    continue
                field_type = model.__fields__[field].type_
                is_list_like = False
                # mypy doesn't understand that sub_fields is not None if is_list_like is True
                # so we use a typing and "or []" to tell mypy that sub_fields is not None
                sub_fields: List[ModelField] = model.__fields__[field].sub_fields or []
                if sub_fields:
                    is_list_like = True
                if is_list_like:
                    type_ = sub_fields[0].type_
                    # See below for the explanation of this comment
                    # field_info = sub_fields[0].field_info
                    if not _issubclass_safe(type_, BaseModel):
                        raise ValueError(
                            f"Field {field} is a list-like field but not a list of BaseModel"
                        )
                    if _issubclass_safe(type_, XMLModel):
                        xml_name = type_._get_xml_name()
                    # This is needed if we load a model with BaseModel
                    # But at the moment, it's not possible to load a model with BaseModel
                    # So we comment this part
                    # else:
                    #     xml_name = field_info.extra.get("__xml_name__")
                elif _issubclass_safe(field_type, XMLModel):
                    xml_name = field_type._get_xml_name()
                else:
                    xml_name = (
                        model.__fields__[field].field_info.extra.get("__xml_name__")
                        or model.__fields__[field].alias
                    )

                # Get the value of the field
                if xml_name in element.attrib and not _issubclass_safe(
                    field_type, BaseModel
                ):
                    data[xml_name] = element.attrib[xml_name]
                # If the field is a list-like field, we convert each XML element to a BaseModel
                elif is_list_like:
                    data[field] = []
                    for child in element.findall(xml_name):
                        data[field].append(from_element(child, type_))
                # If the field is a subelement, we convert it to XML recursively
                else:
                    child_find = element.find(xml_name)
                    if child_find is not None:
                        if _issubclass_safe(field_type, BaseModel):
                            data[field] = from_element(child_find, field_type)

            # Handle the xml_content field
            # Set the content of the XML element
            xml_content_meta = model.__fields__["xml_content"]
            xml_content_data: Any
            # if the field is a list-like field, we add each item as a separate XML element
            if xml_content_meta is not None and xml_content_meta.sub_fields is not None:
                if not _issubclass_safe(
                    xml_content_meta.sub_fields[0].type_, BaseModel
                ):
                    raise ValueError(
                        f"xml_content field of {model.__name__} must be a List[BaseModel]"
                    )
                xml_content_data = []
                name = xml_content_meta.sub_fields[0].type_.__name__
                if _issubclass_safe(xml_content_meta.sub_fields[0].type_, XMLModel):
                    name = xml_content_meta.sub_fields[0].type_._get_xml_name()
                for child in element:
                    if child.tag != name:
                        continue
                    xml_content_data.append(
                        from_element(child, xml_content_meta.sub_fields[0].type_)
                    )
            # else, we add the content as a text
            else:
                xml_content_data = element.text or ""
            data[xml_content_meta.alias] = xml_content_data

            # Convert the data to the model
            out = model(**data)

            return out

        root = fromstring(xml)
        return from_element(root, cls)  # type: ignore
