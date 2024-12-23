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


def extract_import_entries(data: DataFrame, days: int = 7):
    try:
        n_days_ago = datetime.now() - timedelta(days=days)
        data['date'] = pd.to_datetime(data['Read Date and End Time'], dayfirst=True)
        data['month_day'] = data['date'].dt.strftime('%m-%d')
        data['year'] = data['date'].dt.year
        last_n_days_data = data[data['date'] >= n_days_ago]
        last_n_days_data = last_n_days_data.drop(
            columns=['MPRN', 'Meter Serial Number', 'Read Date and End Time'])
        last_n_days_data = last_n_days_data.pivot_table(
            index=['month_day'],
            values='Read Value',
            columns=['Read Type', 'year'],
            aggfunc='sum')

        last_n_days_data = last_n_days_data.bfill(axis=0)

        columns_list = list(last_n_days_data.columns)

        for column in columns_list:
            # """ Add a diff column to the dataframe """
            last_n_days_data[str(column[0])+'_diff', column[1]] \
                = last_n_days_data[column[0], column[1]].diff()
            last_n_days_data[str(column[0])+'_diff', column[1]] \
                = last_n_days_data[str(column[0])+'_diff', column[1]].replace(0, np.nan)

        return last_n_days_data
    except Exception as e:
        logger.error(f"Error extracting last n days entries: {e}")
        return None


def main(file1: str, file2: str, days: int = 7):
    """Accept as input 2 csv files and a Google Form URL.
    The script reads the csv files, extracts the entries from the last week,
    and sends them to the Google Form."""

    logger.info("Script started")

    data1 = read_csv(file1)
    data2 = read_csv(file2)
    if data1.shape[1] > data2.shape[1]:
        logger.error("Data1 does not match columns of Data2")

    data = pd.concat([data1, data2.iloc[1:]])

    if data1 is not None:
        last_n_days_data = extract_import_entries(data, days)

        if last_n_days_data is not None:
            last_n_days_data.to_excel('last_n_days_data.xlsx')
            # send_to_google_form(last_n_days_data, form_url)

    logger.info("Script finished")


if __name__ == "__main__":
    """Add command line parameters to specify the csv files and the Google Form URL."""
    parser = argparse.ArgumentParser(description="Process CSV files and send data to Google Form.")
    parser.add_argument('dnpDailyCsv', type=str, help='Path to the Daily Day/Night/Peak CSV file')
    parser.add_argument('inexDailyCsv', type=str, help='Path to the Daily Import/Export CSV file')
    parser.add_argument('days', type=int, help='Number of days to consider', default=7)

    args = parser.parse_args()

    main(args.dnpDailyCsv, args.inexDailyCsv, args.days)
