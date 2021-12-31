# docstring2markdown

`docstring2markdown` is markdown generetor from Python google styled docstring.

Pythonパッケージのソースコードに書かれたDocstringから，APIドキュメントとなるmarkdownを生成します．

## Install

```bash
git clone https://github.com/mjun0812/docstring2markdown.git
cd docstring2markdown
pip install -e .
```

## Usage

```text
>>> doc-to-md [-h] path

positional arguments:
  path        package root dir

optional arguments:
  -h, --help  show this help message and exit
```

output markdown example is here -> [documantation](./docs/doc.md)

例えば，このリポジトリでドキュメントを作成するときは以下のコマンドを実行します．

```bash
doc-to-md ./docstring2markdown
```

すると，実行ディレクトリにdocsディレクトリが作成され，doc.mdに生成結果が表示されます．

markdownの例は[ここ](./docs/doc.md)です．

<!-- doc-to-md -->

## References

[ml-tooling/lazydocs](https://github.com/ml-tooling/lazydocs)
