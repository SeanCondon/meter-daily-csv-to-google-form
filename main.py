import argparse

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from pandas import DataFrame

dtype_spec = {
    'MPRN': str,
    'Meter Serial Number': str,
}


def read_csv(file_path):
    try:
        data = pd.read_csv(file_path, dtype=dtype_spec)
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

    We expect only one MPRN and one Meter Serial Number in the data frame.
    We remove them from the columns and add them as an attribute.

    :param data: A data frame containing many concatenated files
    :param days: number of days old data to extract
    :return: A dataframe pivoted by day of year
    """
    mprns = data['MPRN'].unique()
    assert len(mprns) == 1, "More than one MPRN in the data"

    msns = data['Meter Serial Number'].unique()
    assert len(msns) == 1, "More than one Meter Serial Number in the data"

    n_days_ago = datetime.now() - timedelta(days=days)
    data['date'] = pd.to_datetime(data['Read Date and End Time'], dayfirst=True)
    data['month_day'] = data['date'].dt.strftime('%m-%d')
    data['year'] = data['date'].dt.year
    last_n_days_data = data[data['date'] >= n_days_ago]  # Filter out older than n days
    last_n_days_data = last_n_days_data.drop(
        columns=['Read Date and End Time', 'MPRN', 'Meter Serial Number'])

    last_n_days_data = last_n_days_data.pivot_table(
        index=['month_day'],
        values='Read Value',
        columns=['Read Type', 'year'],
        aggfunc='max')

    last_n_days_data.attrs['MPRN'] = mprns[0]
    last_n_days_data.attrs['Meter Serial Number'] = msns[0]

    return last_n_days_data


def by_month(data: DataFrame) -> DataFrame:
    data['month'] = data.index.str.split('-').str[0]

    data['month'] = data['month'].replace(
        {
            '01': 'January',
            '02': 'February',
            '03': 'March',
            '04': 'April',
            '05': 'May',
            '06': 'June',
            '07': 'July',
            '08': 'August',
            '09': 'September',
            '10': 'October',
            '11': 'November',
            '12': 'December'
        }
    )

    data_by_month = data.groupby('month').max()
    data_by_month = data_by_month.reindex(['January', 'February', 'March', 'April', 'May', 'June',
                                           'July', 'August', 'September', 'October', 'November',
                                           'December'])

    return data_by_month


def add_diff_columns(data: DataFrame, zero_to_nan: bool = True) -> DataFrame:
    columns_list = list(data.columns)

    # Forward-fill any empty values cells with data from last good value
    data = data.ffill(axis=0)

    for column in columns_list:
        # Add a diff column to the dataframe
        # This uses the pandas diff function to calculate the difference
        # between the current and previous value in the column
        # This does no work where the data is wrapped over from the previous
        # year - that requires an extra function.
        data.loc[:, (str(column[0]) + '_diff', column[1])] \
            = data.loc[:, (column[0], column[1])].diff()

        try:
            _ = columns_list.index((column[0], column[1] - 1))
            first_index = data.index[0]
            last_index = data.index[-1]
            end_last_year = data.loc[last_index, (column[0], column[1] - 1)]
            start_this_year = data.loc[first_index, (column[0], column[1])]
            data.loc[first_index, (str(column[0]) + '_diff', column[1])] =\
                start_this_year - end_last_year
        except ValueError:
            pass  # No previous year data

        if zero_to_nan:
            # Zero difference means there's no difference in a day
            # Usually only possible for export, as everything else will
            # change daily
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


def main(files: list[str], days: int = 10e6):
    """Accept as input csv files and a number of days to extract the entries from.
    The script reads the csv files, extracts the entries from the n days,
    and saves them to an Excel file.

    The files can be a mix of Daily import/export files and Daily Day night peak files.
    """

    logger.info(f"Script started. Processing {len(files)} files...")

    data = concatenate_files(files)

    outfile = 'output.xlsx'
    if data is not None:
        last_n_days_data = extract_import_entries(data, days)

        if last_n_days_data is not None:
            with_diff_cols = add_diff_columns(last_n_days_data)

            monthly_data = by_month(last_n_days_data)
            monthly_with_diff_cols = add_diff_columns(monthly_data, zero_to_nan=False)

            outfile = '%s_%s_%d_data.xlsx' % (
                with_diff_cols.attrs['MPRN'],
                with_diff_cols.attrs['Meter Serial Number'],
                days)

            with pd.ExcelWriter(outfile) as writer:
                with_diff_cols.to_excel(writer, sheet_name='Daily')
                monthly_with_diff_cols.to_excel(writer, sheet_name='Monthly')

    logger.info(f"Script finished. Wrote out to {outfile}")


if __name__ == "__main__":
    """Add command line parameters to specify the csv files and the Google Form URL."""
    parser = argparse.ArgumentParser(description="Process CSV files and send data to Google Form.")
    parser.add_argument('days', type=int, help='Number of days to consider', default=7)
    parser.add_argument('dailyCsv', type=str, nargs='+', help='Path to the Daily CSV file')

    args = parser.parse_args()

    main(args.dailyCsv, args.days)
