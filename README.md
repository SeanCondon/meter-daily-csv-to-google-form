# HDF to Spreadsheet

![CI](https://github.com/SeanCondon/meter-daily-csv-to-google-form/actions/workflows/ci.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project is a Python script that reads two CSV files, extracts entries
from the last N days, and saves them to a spreadsheet.

See more details in the [documentation](docs/index).

## GitHub Pages

This repository is configured to publish a GitHub Pages site from the `docs` folder.
You can access the site at the following URL:

[https://SeanCondon.github.io/meter-daily-csv-to-google-form](https://SeanCondon.github.io/meter-daily-csv-to-google-form)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/githubnext/workspace-blank.git
    cd workspace-blank
    ```

2. Install Poetry:

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install dependencies:

    ```sh
    poetry install
    ```

## Usage

1. Run the script:

    ```sh
    poetry run python main.py <days> <input_file(s)>
    ```

## CI Pipeline

This project uses a CI pipeline that includes a markdown linter to ensure the
quality and consistency of markdown files. The linter is configured to run on
all `.md` files in the repository.
