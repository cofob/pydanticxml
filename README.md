# PydanticXML

PydanticXML is a Python library that provides a way to convert Pydantic models to XML and vice versa. It is built on top of the Pydantic library and extends it with XML-specific functionality.

## Installation

You can install PydanticXML with pip:

```bash
pip install pydantic-xmlmodel
```

## Usage

To use PydanticXML, you need to import the `XMLModel` class from the `pydanticxml` module:

```python
from pydantic_xmlmodel import XMLModel
```

## Examples

### Defining a Model

You can define a model by subclassing `XMLModel` and defining attributes with type annotations:

```python
class AnimalCharacteristics(XMLModel):
    color: str = "black"
    weight: int = 10
    is_friendly: bool = True
```

### Converting a Model to XML

You can convert a model to XML by calling the `to_xml()` method:

```python
class Cat(XMLModel):
    animal_characteristics: AnimalCharacteristics
    name: str = "Kitty"

cat = Cat(animal_characteristics=AnimalCharacteristics())
print(cat.to_xml(indent=4))
```

This will output:

```xml
<?xml version="1.0" ?>
<cat name="Kitty">
    <animalcharacteristics color="black" weight="10" is_friendly="True"/>
</cat>
```

### Converting XML to a Model

You can convert XML to a model by calling the `from_xml()` method:

```python
xml = """<?xml version="1.0" ?>
<cat name="Kitty">
    <animalcharacteristics color="black" is_friendly="true" weight="10"/>
</cat>
"""
cat = Cat.from_xml(xml)
print(cat)
```

This will output:

```python
animal_characteristics=AnimalCharacteristics(color='black', weight=10, is_friendly=True, xml_content=None) name='Kitty' xml_content='\n    '
```

*(Note that the `xml_content` attribute is not part of the model. It is used to store the XML content, like this `<element> xml_content <other_element /></element>`)*
