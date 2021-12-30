import re
import datetime
import pkgutil
import inspect
import pathlib

# catch block start
# ex. Args:, Returns:
_BLOCKSTART_LIST = re.compile(
    r"(Args:|Arg:|Arguments:|Parameters:|Kwargs:|Attributes:|Returns:|Yields:|Kwargs:|Raises:)",
    re.IGNORECASE,
)

_BLOCKSTART_TEXT = re.compile(r"(Examples:|Example:|Todo:)", re.IGNORECASE)

_QUOTE_TEXT = re.compile(r"(Notes:|Note:)", re.IGNORECASE)

# catch value context
_TYPED_ARGSTART = re.compile(r"([\w\[\]_]{1,}?)\s*?\((.*?)\):(.{2,})", re.IGNORECASE)

_ARGSTART = re.compile(r"(.{1,}?):(.{2,})", re.IGNORECASE)

_MODULE_TEMPLATE = """
{header}
{doc}{global_vars}{functions}{classes}
"""

_FUNC_TEMPLATE = """
### <kbd>function</kbd> `{header}`

```python
{definition}
```

{doc}
"""

_CLASS_TEMPLATE = """
### <kbd>class</kbd> `{header}`

{class_doc}
{init}{variables}{handlers}{methods}
"""


def generate_markdown(path):
    """generate markdown from package in path

    Args:
        path (str): package root dir path
    """
    output = f"# API\n\nUpdate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ignored_modules = []
    for loader, name, _ in pkgutil.walk_packages([path]):
        if _is_module_ignored(name, ignored_modules):
            # Add module to ignore list, so submodule will also be ignored
            ignored_modules.append(name)
            continue
        try:
            module = loader.find_module(name).load_module(name)
        except Exception as e:
            print(f"Error: Can't generate {name} doc. {e}")
            continue
        markdown = module_to_markdown(module)
        if not markdown:
            # Module md is empty -> ignore module and all submodules
            # Add module to ignore list, so submodule will also be ignored
            ignored_modules.append(name)
            continue
        output += markdown
    output = validate_output(output)
    output_path = pathlib.Path(path).parent / "docs"
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "doc.md", "w") as f:
        f.write(output)


def _is_module_ignored(module_name, ignored_modules) -> bool:
    """Checks if a given module is ignored."""
    if module_name.split(".")[-1].startswith("_"):
        return True

    for ignored_module in ignored_modules:
        if module_name == ignored_module:
            return True

        # Check is module is subpackage of an ignored package
        if module_name.startswith(ignored_module + "."):
            return True

    return False


def validate_output(output):
    """markdown validator

    ex. fix number of new line, period newline

    Args:
        output (str): input markdown text

    Returns:
        str: validated markdown
    """
    output = re.sub("\n+#", "\n\n#", output)
    output = re.sub("\n+$", "\n", output)
    return output


def get_docstring(module):
    """get docstring from module

    Args:
        module (obj): module had docstring or not

    Returns:
        str: return docstring or ""
    """
    docstring = inspect.getdoc(module)
    if docstring is None:
        return ""
    else:
        return docstring


def docstring_to_markdown(docstring):
    """parse google format docstring to markdown

    Args:
        docstring (str): google format docstring

    Returns:
        str: markdown text
    """
    block_indent = 0
    arg_indent = 0
    markdown_output = []
    args = False
    literal_block = False
    md_code_snippet = False
    quote_block = False

    for row in docstring.split("\n"):
        indent_depth = len(row) - len(row.lstrip())
        if not md_code_snippet and not literal_block:
            row = row.lstrip()

        if row.startswith(">>>"):
            # support for doctest
            row = row.replace(">>>", ">")

        if _BLOCKSTART_LIST.match(row) or _BLOCKSTART_TEXT.match(row) or _QUOTE_TEXT.match(row):
            block_indent = indent_depth
            if quote_block:
                quote_block = False
            if literal_block:
                markdown_output.append("```\n")
                literal_block = False
            markdown_output.append(f"#### {row.strip()}\n")
            args = _BLOCKSTART_LIST.match(row)
            if _QUOTE_TEXT.match(row):
                quote_block = True
                markdown_output.append("\n>")
        elif row.strip().startswith("```") or row.strip().startswith("`"):
            md_code_snippet = not md_code_snippet
            markdown_output.append("\n" + row)
        elif row.strip().endswith("::"):
            literal_block = True
            markdown_output.append(row.replace("::", ":\n```"))
        elif quote_block:
            markdown_output.append(row.strip())
        elif row.strip().startswith("-"):
            markdown_output.append("\n" + (" " * indent_depth) + row)
        elif indent_depth > block_indent:
            if args and not literal_block:
                if _TYPED_ARGSTART.match(row):
                    markdown_output.append("\n" + " " * block_indent + "- " + _TYPED_ARGSTART.sub(r"*`\1`*: \2", row))
                elif _ARGSTART.match(row):
                    markdown_output.append("\n" + " " * block_indent + "- " + _ARGSTART.sub(r"*`\1`*: \2", row))
                arg_indent = indent_depth
            elif indent_depth > arg_indent:
                markdown_output.append(f" {row}")
            else:
                markdown_output.append("\n" + row)
        else:
            if row.strip() and literal_block:
                row = "```\n" + row
                literal_block = False
            markdown_output.append(row)

        if md_code_snippet:
            markdown_output.append("\n")
        elif not row and not quote_block:
            markdown_output.append("\n\n")
        elif not row and quote_block:
            markdown_output.append("\n>")
    return "".join(markdown_output)


def _get_function_signature(
    function,
    owner_class=None,
    wrap_arguments=False,
    remove_package=False,
):
    """get function definition

    example:
    ```python
    def hoge(a: int) -> int
    ```

    Args:
        function (obj): function which you want definition.
        owner_class (class, optional): Input parent class when input function is class method. Defaults to None.
        wrap_arguments (bool, optional): Limited line num at 119 charactors. Defaults to False.
        remove_package (bool, optional): hoge.func -> func. Defaults to False.

    Returns:
        string: markdown code block about function definition.
    """
    isclass = inspect.isclass(function)

    # Get base name.
    name_parts = []
    if owner_class:
        name_parts.append(owner_class.__name__)
    if hasattr(function, "__name__"):
        name_parts.append(function.__name__)
    else:
        name_parts.append(type(function).__name__)
        name_parts.append("__call__")
        function = function.__call__  # type: ignore
    name = ".".join(name_parts)

    if isclass:
        function = getattr(function, "__init__", None)

    arguments = []
    return_type = ""
    if hasattr(inspect, "signature"):
        parameters = inspect.signature(function).parameters
        if inspect.signature(function).return_annotation != inspect.Signature.empty:
            return_type = str(inspect.signature(function).return_annotation)
            if return_type.startswith("<class"):
                # Base class -> get real name
                try:
                    return_type = inspect.signature(function).return_annotation.__name__
                except Exception:
                    pass
            # Remove all typing path prefixes
            return_type = return_type.replace("typing.", "")
            if remove_package:
                # Remove all package path return type
                return_type = re.sub(r"([a-zA-Z0-9_]*?\.)", "", return_type)

        for parameter in parameters:
            argument = str(parameters[parameter])
            # Reintroduce Optionals
            argument = re.sub(r"Union\[(.*?), NoneType\]", r"Optional[\1]", argument)

            # Remove package
            if remove_package:
                # Remove all package path from parameter signature
                if "=" not in argument:
                    argument = re.sub(r"([a-zA-Z0-9_]*?\.)", "", argument)
                else:
                    # Remove only from part before the first =
                    argument_split = argument.split("=")
                    argument_split[0] = re.sub(r"([a-zA-Z0-9_]*?\.)", "", argument_split[0])
                    argument = "=".join(argument_split)
            arguments.append(argument)
    else:
        print("Seems like function " + name + " does not have any signature")

    signature = name + "("
    if wrap_arguments:
        for i, arg in enumerate(arguments):
            signature += "\n    " + arg

            signature += "," if i is not len(arguments) - 1 else "\n"
    else:
        signature += ", ".join(arguments)

    signature += ")" + ((" → " + return_type) if return_type else "")

    return signature


def function_to_markdown(func, clsname="") -> str:
    """get markdown from function docstring

    Args:
        func (obj): function
        clsname (str, optional): if you input class method, this variable is class name. Defaults to "".

    Returns:
        str: markdown text from function.
    """
    funcname = func.__name__
    doc = get_docstring(func)

    escfuncname = "%s" % funcname if funcname.startswith("_") else funcname  # "`%s`"

    full_name = "%s%s" % ("%s." % clsname if clsname else "", escfuncname)
    header = full_name

    doc = docstring_to_markdown(doc)

    definition = _get_function_signature(func)

    # split the function definition if it is too long
    lmax = 119
    if len(definition) > lmax:
        definition = _get_function_signature(
            func,
            wrap_arguments=True,
        )

    # build the signature
    markdown = _FUNC_TEMPLATE.format(
        header=header,
        definition=definition,
        doc=doc if doc else "",
    )

    return markdown


def class_to_markdown(cls) -> str:
    """get markdown from class docstring and class method.

    Returns:
        str: markdown about class
    """

    clsname = cls.__name__
    modname = cls.__module__
    doc = get_docstring(cls)
    header = clsname
    doc = docstring_to_markdown(doc)

    try:
        # object module should be the same as the calling module
        if hasattr(cls.__init__, "__module__") and cls.__init__.__module__ == modname:
            init = function_to_markdown(cls.__init__, get_docstring(cls.__init__), clsname=clsname)
        else:
            init = ""
    except (ValueError, TypeError):
        # this happens if __init__ is outside the repo
        init = ""

    variables = []
    for name, obj in inspect.getmembers(cls, lambda a: not (inspect.isroutine(a) or inspect.ismethod(a))):
        if not name.startswith("_") and type(obj) == property:
            comments = docstring_to_markdown(get_docstring(obj)) or inspect.getcomments(obj)
            comments = "\n\n%s" % comments if comments else ""
            property_name = f"{clsname}.{name}"
            variables.append(f"\n####  {property_name}{comments}\n")

    handlers = []
    for name, obj in inspect.getmembers(cls, inspect.ismethoddescriptor):
        if (
            not name.startswith("_")
            and hasattr(obj, "__module__")
            # object module should be the same as the calling module
            and obj.__module__ == modname
        ):
            handler_name = f"{clsname}.{name}"
            handlers.append(f"\n#### {handler_name}\n")

    methods = []
    # for name, obj in getmembers(cls, inspect.isfunction):
    for name, obj in inspect.getmembers(cls, lambda a: inspect.ismethod(a) or inspect.isfunction(a)):
        if (
            not name.startswith("_")
            and hasattr(obj, "__module__")
            and name not in handlers
            # object module should be the same as the calling module
            and obj.__module__ == modname
        ):
            function_md = function_to_markdown(obj, clsname=clsname)
            methods.append(function_md)

    markdown = _CLASS_TEMPLATE.format(
        header=header,
        class_doc=doc if doc else "",
        init=init,
        variables="".join(variables),
        handlers="".join(handlers),
        methods="".join(methods),
    )

    return markdown


def module_to_markdown(module) -> str:
    """get markdown from module

    Args:
        module (obj): module

    Returns:
        str: markdown about module
    """

    def _order_by_line_nos(objs, line_nos):
        """Orders the set of `objs` by `line_nos`."""
        ordering = sorted(range(len(line_nos)), key=line_nos.__getitem__)
        return [objs[i] for i in ordering]

    def _get_line_no(_obj):
        """Gets the source line number of this object. None if `obj` code cannot be found."""
        try:
            return inspect.getsourcelines(_obj)[1]
        except Exception:
            # no code found
            return None

    modname = module.__name__
    doc = get_docstring(module)
    found = []

    classes = []
    line_nos = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        # handle classes
        found.append(name)
        if not name.startswith("_") and hasattr(obj, "__module__") and obj.__module__ == modname:
            class_markdown = class_to_markdown(obj)
            if class_markdown:
                classes.append(class_markdown)
                line_nos.append(_get_line_no(obj) or 0)
    classes = _order_by_line_nos(classes, line_nos)

    functions = []
    line_nos = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        # handle functions
        found.append(name)
        if not name.startswith("_") and hasattr(obj, "__module__") and obj.__module__ == modname:
            function_md = function_to_markdown(obj, clsname=modname.split(".")[0])
            if function_md:
                functions.append(function_md)
                line_nos.append(_get_line_no(obj) or 0)
    functions = _order_by_line_nos(functions, line_nos)

    variables = []
    line_nos = []
    for name, obj in module.__dict__.items():
        if not name.startswith("_") and name not in found:
            if hasattr(obj, "__module__") and obj.__module__ != modname:
                continue
            if hasattr(obj, "__name__"):
                continue
            comments = inspect.getcomments(obj)
            comments = ": %s" % comments if comments else ""
            variables.append("- **%s**%s" % (name, comments))
            line_nos.append(_get_line_no(obj) or 0)
    variables = _order_by_line_nos(variables, line_nos)
    if variables:
        new_list = ["\n### Global Variables\n", *variables]
        variables = new_list

    header = f"## <kbd>module</kbd> {modname}"
    if len(modname.split(".")) >= 2:
        split_name = modname.split(".")
        if split_name[0] == split_name[1]:
            header = ""
            variables = []

    markdown = _MODULE_TEMPLATE.format(
        header=header,
        doc=doc,
        global_vars="\n".join(variables) if variables else "",
        functions="\n".join(functions) if functions else "",
        classes="".join(classes) if classes else "",
    )

    return markdown
