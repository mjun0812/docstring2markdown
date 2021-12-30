# API

Update: 2021-12-31 00:43

## <kbd>module</kbd> parser

### <kbd>function</kbd> `parser.generate_markdown`

```python
generate_markdown(path)
```

generate markdown from package in path

#### Args:

- *`path`*: str

### <kbd>function</kbd> `parser.validate_output`

```python
validate_output(output)
```

markdown validator

ex. fix number of new line, period newline

#### Args:

- *`output`*: str

#### Returns:

- *`str`*:  validated markdown

### <kbd>function</kbd> `parser.get_docstring`

```python
get_docstring(module)
```

get docstring from module

#### Args:

- *`module`*: obj

#### Returns:

- *`str`*:  return docstring or ""

### <kbd>function</kbd> `parser.docstring_to_markdown`

```python
docstring_to_markdown(docstring)
```

parse google format docstring to markdown

#### Args:

- *`docstring`*: str

#### Returns:

- *`str`*:  markdown text

### <kbd>function</kbd> `parser.function_to_markdown`

```python
function_to_markdown(func, clsname='') → str
```

get markdown from function docstring

#### Args:

- *`func`*: obj
- *`clsname`*: str, optional

#### Returns:

- *`str`*:  markdown text from function.

### <kbd>function</kbd> `parser.class_to_markdown`

```python
class_to_markdown(cls) → str
```

get markdown from class docstring and class method.

#### Returns:

- *`str`*:  markdown about class

### <kbd>function</kbd> `parser.module_to_markdown`

```python
module_to_markdown(module) → str
```

get markdown from module

#### Args:

- *`module`*: obj

#### Returns:

- *`str`*:  markdown about module
