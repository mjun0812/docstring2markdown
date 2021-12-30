import argparse

from docstring2markdown import generate_markdown


def _arg_parse():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("path", help="package root dir")
    return parser.parse_args()


def _cli():
    args = _arg_parse()
    generate_markdown(args.path)
