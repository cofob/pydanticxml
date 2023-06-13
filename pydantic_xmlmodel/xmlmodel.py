"""A module that contains the XMLModel class."""

from typing import Any, Callable, Optional, Type, TypeVar, no_type_check
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, fromstring, tostring

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

T = TypeVar("T", bound="XMLModel")


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
        - `__xml_content__`: The content of the XML element inside `<element>{{__xml_content__}}</element>`. If not specified, the element will not have any content.
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

    __xml_content__: Optional[str] = None
    """The content of the XML element inside `<element>{{__xml_content__}}</element>`. If not specified, the element will not have any content."""

    def __init__(self, **data: Any) -> None:
        """Initialize the model."""
        xml_content = data.pop("__xml_content__", None)
        super().__init__(**data)
        if xml_content is not None:
            object.__setattr__(self, "__xml_content__", xml_content)

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
        self, indent: Optional[int] = None, include_xml_version: bool = True
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
                # We skip the __xml_content__ field because we handle it separately
                if field == "__xml_content__":
                    continue
                # We get the value of the field using getattr() because the we need subclass of BaseModel, not just dict
                value = getattr(obj, field)
                # If the value is a BaseModel, we convert it to XML recursively
                if isinstance(value, BaseModel):
                    # Get the name of the XML element
                    name = value.__class__.__name__
                    if isinstance(value, XMLModel):
                        name = value._get_xml_name()
                    # Create the XML element and add it to the parent element
                    sub = SubElement(e, name)
                    # Convert the BaseModel to XML recursively
                    to_xml_innner(sub, value)
                # Else, we add the value as an attribute
                else:
                    # Get the name of the XML attribute
                    pydantic_field = obj.__fields__[field]
                    # If the field has an alias, we use it as the name of the XML attribute
                    name = pydantic_field.name
                    if pydantic_field.alias is not None:
                        name = pydantic_field.alias
                    # Add the attribute to the XML element
                    e.set(name, str(value))
            # If the model has content, we add it to the XML element
            if isinstance(obj, XMLModel) and obj.__xml_content__ is not None:
                e.text = obj.__xml_content__

        # Create the root XML element
        root = Element(self._get_xml_name())
        # Convert the model to XML recursively
        to_xml_innner(root, self)
        # Convert the XML element to string
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
            data = {}
            for field in model.__fields__:
                field_type = model.__annotations__[field]
                if issubclass(field_type, XMLModel):
                    xml_name = field_type._get_xml_name()
                else:
                    xml_name = (
                        model.__fields__[field].field_info.extra.get("__xml_name__")
                        or field
                    )

                # Get the value of the field
                if xml_name in element.attrib and not issubclass(field_type, BaseModel):
                    data[field] = element.attrib[xml_name]
                # If the field is a subelement, we convert it to XML recursively
                else:
                    child = element.find(xml_name)
                    if child is not None:
                        if issubclass(field_type, BaseModel):
                            data[field] = from_element(child, field_type)
                        else:
                            data[field] = child.text or ""

            # Convert the data to the model
            out = model(**data)

            # Set the content of the XML element
            if isinstance(out, XMLModel):
                object.__setattr__(out, "__xml_content__", element.text)

            return out

        root = fromstring(xml)
        return from_element(root, cls)  # type: ignore

    def set_xml_content(self, value: Optional[str]) -> None:
        """Set the content of the XML element."""
        object.__setattr__(self, "__xml_content__", value)
