#!/bin/bash

# Need to update generated content separately using poetry env:
# python scripts/json_schema_to_md_doc.py
# python scripts/generate_dialect_comparison_docs.py

deactivate
python3 -m venv docs-venv
source docs-venv/bin/activate
pip install --upgrade pip
pip install -r scripts/docs-requirements.txt
# if you haven't run generate_dialect_comparison_docs.py, then install the splink dependencies and run
if [[ ! -f "docs/includes/generated_files/comparison_level_library_dialect_table.md" ]]
then
    pip install poetry
    poetry install
    python3 scripts/generate_dialect_comparison_docs.py
    python3 scripts/generate_dataset_docs.py
fi
# manually preprocess include files as include-markdown plugin clashes with mknotebooks
# make sure not to commit changes to files with inclusions!
python3 scripts/preprocess_markdown_includes.py

# can remove verbose flag if needed
mkdocs serve -v
