import argparse

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
        one_week_ago = datetime.now() - timedelta(days=days)
        data['date'] = pd.to_datetime(data['Read Date and End Time'])
        last_week_data = data[data['date'] >= one_week_ago]
        last_week_data = last_week_data.drop(
            columns=['MPRN', 'Meter Serial Number', 'Read Date and End Time'])
        last_week_data = last_week_data.pivot_table(
            index='date',
            values='Read Value',
            columns=['Read Type'],
            aggfunc='sum')
        return last_week_data
    except Exception as e:
        logger.error(f"Error extracting last week entries: {e}")
        return None


def send_to_google_form(data, form_url):
    try:
        for index, row in data.iterrows():
            # exp_kwh: float = row["24 Hr Active Export Register (kWh)"]
            night_kwh = row["Night Import Register (kWh)"]
            day_kwh = row["Day Off-Peak Import Register (kWh)"]
            peak_kwh = row["Day Peak Import Register (kWh)"]
            imp_total = round(night_kwh + day_kwh + peak_kwh, 3)
            logger.info(f'Processing {index} Import:{imp_total}')
            # response = requests.post(form_url, data=row.to_dict())
            # if response.status_code != 200:
            #     logger.error(f"Error sending data to Google: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending data to Google Form: {e}")


def main(file1: str, file2: str, form_url):
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
        last_week_data = extract_import_entries(data)

        if last_week_data is not None:
            send_to_google_form(last_week_data, form_url)

    logger.info("Script finished")


if __name__ == "__main__":
    """Add command line parameters to specify the csv files and the Google Form URL."""
    parser = argparse.ArgumentParser(description="Process CSV files and send data to Google Form.")
    parser.add_argument('csvfile1', type=str, help='Path to the first CSV file')
    parser.add_argument('csvfile2', type=str, help='Path to the second CSV file')
    parser.add_argument('form_url', type=str, help='Google Form URL',
                        default='https://docs.google.com/forms/d/e/your-form-id/formResponse')

    args = parser.parse_args()

    assert len(args) == 3, "Please provide 3 arguments: csvfile1, csvfile2, and form_url"

    main(args[0], args[1], args[2])
