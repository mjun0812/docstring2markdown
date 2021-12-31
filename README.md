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

## Github Actions

下記のGithub Actionsスクリプトを既存のリポジトリに導入すると，push時にAPI Documentが自動で作成されます．

If you introduce the following Github Actions script to an existing repository, an API Document will be automatically created when you push.

```yaml
name: Generate API Document Markdown from Python Package

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  docstring-to-markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8

      - name: Install Package
        run: |
          pip install git+https://github.com/mjun0812/docstring2markdown.git
          # Package Dependency
          pip install hoge

      - name: Generate Doc
        run: doc-to-md hoge

      - name: Git commit and push
        run: |
          git add -N .
          if ! git diff --exit-code --quiet
          then
            git config user.name github-actions
            git config user.email github-actions@github.com
            git add .
            git commit -m "Update doc.md"
            git push
          fi
```

## References

[ml-tooling/lazydocs](https://github.com/ml-tooling/lazydocs)
