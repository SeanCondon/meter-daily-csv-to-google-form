# CSV to Google Form

![CI](https://github.com/SeanCondon/meter-daily-csv-to-google-form/actions/workflows/ci.yml/badge.svg)

This project is a Python script that reads two CSV files, extracts entries
from the last week, and posts the values to a Google Form.

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

1. Update the file paths and Google Form URL in `main.py`:

    ```python
    file1 = 'path/to/your/csvfile1.csv'
    file2 = 'path/to/your/csvfile2.csv'
    form_url = 'https://docs.google.com/forms/d/e/your-form-id/formResponse'
    ```

2. Run the script:

    ```sh
    poetry run python main.py
    ```

## CI Pipeline

This project uses a CI pipeline that includes a markdown linter to ensure the
quality and consistency of markdown files. The linter is configured to run on
all `.md` files in the repository.

## GitHub Pages

This repository is configured to publish a GitHub Pages site from the `docs` folder. You can access the site at the following URL:

[https://SeanCondon.github.io/meter-daily-csv-to-google-form](https://SeanCondon.github.io/meter-daily-csv-to-google-form)
