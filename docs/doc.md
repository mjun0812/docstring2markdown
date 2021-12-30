# API

Update: 2021-12-31 01:08

## <kbd>module</kbd> parser

### <kbd>function</kbd> `parser.generate_markdown`

```python
generate_markdown(path)
```

generate markdown from package dir path

#### Args:

 - <b>`path`</b> (str):  package root dir path

### <kbd>function</kbd> `parser.validate_output`

```python
validate_output(output)
```

markdown validator

fix number of new line and period newline.

#### Args:

 - <b>`output`</b> (str):  input markdown text

#### Returns:

- *`str`*:  validated markdown

### <kbd>function</kbd> `parser.get_docstring`

```python
get_docstring(module)
```

get docstring from module

#### Args:

 - <b>`module`</b> (obj):  module had docstring or not

#### Returns:

- *`str`*:  return docstring or ""

### <kbd>function</kbd> `parser.docstring_to_markdown`

```python
docstring_to_markdown(docstring)
```

parse google format docstring to markdown

#### Args:

 - <b>`docstring`</b> (str):  google format docstring

#### Returns:

- *`str`*:  markdown text

### <kbd>function</kbd> `parser.function_to_markdown`

```python
function_to_markdown(func, clsname='') → str
```

get markdown from function docstring

#### Args:

 - <b>`func`</b> (obj):  function
 - <b>`clsname`</b> (str, optional):  if you input class method, this variable is class name. Defaults to "".

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

 - <b>`module`</b> (obj):  module

#### Returns:

- *`str`*:  markdown about module
