import argparse

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from pandas import DataFrame


def read_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {e}")
        return None


def extract_import_entries(data: DataFrame, days: int = 7) -> DataFrame:
    """
    Takes a data frame with date, value and type columns and pivots it to
    day in year with type and year in columns.
    If there are more than one value for a date then take the maximum of the 2.
    This might be necessary when a later HDF file corrects an older one

    :param data: A data frame containing many concatenated files
    :param days: number of days old data to extract
    :return: A dataframe pivoted by day of year
    """
    n_days_ago = datetime.now() - timedelta(days=days)
    data['date'] = pd.to_datetime(data['Read Date and End Time'], dayfirst=True)
    data['month_day'] = data['date'].dt.strftime('%m-%d')
    data['year'] = data['date'].dt.year
    last_n_days_data = data[data['date'] >= n_days_ago]  # Filter out older than n days
    last_n_days_data = last_n_days_data.drop(
        columns=['MPRN', 'Meter Serial Number', 'Read Date and End Time'])

    last_n_days_data = last_n_days_data.pivot_table(
        index=['month_day'],
        values='Read Value',
        columns=['Read Type', 'year'],
        aggfunc='max')

    return last_n_days_data


def add_diff_columns(data: DataFrame) -> DataFrame:
    columns_list = list(data.columns)

    # Forward-fill any empty values cells with data from last good value
    data = data.ffill(axis=0)

    for column in columns_list:
        # Add a diff column to the dataframe
        data[str(column[0]) + '_diff', column[1]] \
            = data[column[0], column[1]].diff()
        data[str(column[0]) + '_diff', column[1]] \
            = data[str(column[0]) + '_diff', column[1]].replace(0, np.nan)

    return data


def concatenate_files(files: list[str]) -> DataFrame:
    """
    Accept multiple files and concatenate them into a single DataFrame.
    The files need to be of the same witdh and the same columns.
    The nature of smart meter files means that data can be missing from
    time to time, and so the script will fill the missing data from later files
    if it becomes available.
    """

    if len(files) < 1:
        logger.error("No files provided")
        raise ValueError("No files provided")

    data1 = read_csv(files[0])

    for file in files[1:]:
        data = read_csv(file)
        if data1.shape[1] > data.shape[1]:
            logger.error("Data does not match columns of Data1")

        # Concatenate the data, but leave out the first row of the new data
        data1 = pd.concat([data1, data])

    return data1


def main(files: list[str], days: int = 7):
    """Accept as input csv files and a number of days to extract the entries from.
    The script reads the csv files, extracts the entries from the n days,
    and saves them to an Excel file.

    The files can be a mix of Daily import/export files and Daily Day night peak files.
    """

    logger.info("Script started")

    data = concatenate_files(files)

    if data is not None:
        last_n_days_data = extract_import_entries(data, days)

        if last_n_days_data is not None:
            with_diff_cols = add_diff_columns(last_n_days_data)

            with_diff_cols.to_excel('last_n_days_data.xlsx')

    logger.info("Script finished")


if __name__ == "__main__":
    """Add command line parameters to specify the csv files and the Google Form URL."""
    parser = argparse.ArgumentParser(description="Process CSV files and send data to Google Form.")
    parser.add_argument('days', type=int, help='Number of days to consider', default=7)
    parser.add_argument('dailyCsv', type=str, nargs='+', help='Path to the Daily CSV file')

    args = parser.parse_args()

    main(args.dailyCsv, args.days)
