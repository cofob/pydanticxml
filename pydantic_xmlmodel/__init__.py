"""Pydantic XML support.

Example:
    >>> from pydantic_xmlmodel import BaseModelXML
    >>> class MyModel(BaseModelXML):
    ...     data: str
    ...
    >>> model = MyModel(data="foo")
    >>> print(model.model_dump_xml())
    <data foo="foo" />
"""

from .serde import model_dump_xml, model_validate_xml
from .xmlmodel import BaseModelXML, XMLConfigDict, XMLModel

__all__ = [
    "XMLModel",
    "BaseModelXML",
    "XMLConfigDict",
    "model_dump_xml",
    "model_validate_xml",
]
