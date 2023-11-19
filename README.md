# PydanticXML

PydanticXML is a Python library that provides a way to convert Pydantic models to XML and vice versa. It is built on top of the Pydantic library and extends it with XML-specific functionality.

## Features

- Based on Pydantic 2
- Convert Pydantic models to XML and vice versa
- Support for XML attributes, elements, content, lists.
- Compatible with most Pydantic features (e.g. default values, aliases, validators, `Field` etc.)
- Very easy to use. Extends Pydantic's API with only a few methods.
- Has no dependencies other than Pydantic
- Fully tested (almost 100% coverage)
- Supports mypy

## Installation

You can install PydanticXML with pip:

```bash
pip install pydantic-xmlmodel
```

## Usage

To use PydanticXML, you need to import the `BaseModelXML` class from the `pydanticxml` module:

```python
from pydantic_xmlmodel import BaseModelXML
```

Or if your models is not based on BaseModelXML class you can use these functions:

```python
from pydantic_xmlmodel import model_dump_xml, model_validate_xml
```

## Examples

### Defining a Model

You can define a model by subclassing `BaseModelXML` and defining attributes with type annotations:

```python
class AnimalCharacteristics(BaseModelXML):
    color: str = "black"
    weight: int = 10
    is_friendly: bool = True
```

### Converting a Model to XML

You can convert a model to XML by calling the `model_dump_xml()` method:

```python
class Cat(BaseModelXML):
    animal_characteristics: AnimalCharacteristics
    name: str = "Kitty"

cat = Cat(animal_characteristics=AnimalCharacteristics())
print(cat.model_dump_xml())
```

This will output:

```xml
<?xml version="1.0" ?><Cat name="Kitty"><AnimalCharacteristics color="black" weight="10" is_friendly="True" /></Cat>
```

### Converting XML to a Model

You can convert XML to a model by calling the `model_validate_xml()` method:

```python
xml = '<?xml version="1.0" ?><Cat name="Kitty"><AnimalCharacteristics color="black" weight="10" is_friendly="True" /></Cat>'
cat = Cat.model_validate_xml(xml)
print(cat)
```

This will output:

```python
xml_content=None animal_characteristics=AnimalCharacteristics(xml_content=None, color='black', weight=10, is_friendly=True) name='Kitty'
```

*(Note that the `xml_content` attribute is not part of the model. It is used to store the XML content, like this `<element> xml_content <other_element /></element>`)*
