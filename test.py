from main import main, concatenate_files

MPRN = 'MPRN'
METER_SERIAL_NUMBER = 'Meter Serial Number'
READ_VALUE = 'Read Value'
READ_TYPE = 'Read Type'
READ_DATE_AND_END_TIME = 'Read Date and End Time'

TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER = '24 Hr Active Import Register (kWh)'
TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER = '24 Hr Active Export Register (kWh)'
DAY_PEAK_IMPORT_REGISTER = 'Day Peak Import Register (kWh)'
DAY_OFF_PEAK_IMPORT_REGISTER = 'Day Off-Peak Import Register (kWh)'
NIGHT_IMPORT_REGISTER = 'Night Import Register (kWh)'

EXPECTED_IMPORT = 542
EXPECTED_EXPORT = 707
EXPECTED_NIGHT = 703
EXPECTED_DAY = 703
EXPECTED_PEAK = 703


def test_main():
    main(['test/HDF_DailyDNP_kWh_01234567890_20-12-2024.csv',
          'test/HDF_Daily_kWh_01234567890_20-12-2024.csv'], 1000)


def test_concatenate_2_files():
    df = concatenate_files(['test/HDF_DailyDNP_kWh_01234567890_20-12-2024.csv',
                            'test/HDF_Daily_kWh_01234567890_20-12-2024.csv'])

    assert df is not None

    assert df.shape[0] == 3358
    assert df.shape[1] == 5
    assert df.columns[0] == MPRN
    assert df.columns[1] == METER_SERIAL_NUMBER
    assert df.columns[2] == READ_VALUE
    assert df.columns[3] == READ_TYPE
    assert df.columns[4] == READ_DATE_AND_END_TIME

    # Import has some data missing
    assert (df[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER).sum() == EXPECTED_IMPORT
    assert (df[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER).sum() == EXPECTED_EXPORT
    assert (df[READ_TYPE] == DAY_PEAK_IMPORT_REGISTER).sum() == EXPECTED_PEAK
    assert (df[READ_TYPE] == DAY_OFF_PEAK_IMPORT_REGISTER).sum() == EXPECTED_DAY
    assert (df[READ_TYPE] == NIGHT_IMPORT_REGISTER).sum() == EXPECTED_NIGHT

    assert df.shape[0] == EXPECTED_IMPORT + EXPECTED_EXPORT + \
           EXPECTED_PEAK + EXPECTED_DAY + EXPECTED_NIGHT  # no stray rows

    import_row_19th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK]
    assert import_row_19th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER
    assert import_row_19th[READ_DATE_AND_END_TIME] == '19-12-2024 00:00'
    assert import_row_19th[READ_VALUE] == 34458.640

    export_row_19th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK + 1]
    assert export_row_19th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER
    assert export_row_19th[READ_DATE_AND_END_TIME] == '19-12-2024 00:00'
    assert export_row_19th[READ_VALUE] == 5448.502

    import_row_18th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK + 2]
    assert import_row_18th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER
    assert import_row_18th[READ_DATE_AND_END_TIME] == '18-12-2024 00:00'
    assert import_row_18th[READ_VALUE] == 34383.058

    export_row_18th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK + 3]
    assert export_row_18th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER
    assert export_row_18th[READ_DATE_AND_END_TIME] == '18-12-2024 00:00'
    assert export_row_18th[READ_VALUE] == 5448.502


def test_concatenate_3_file():
    """Load 3 files and test the concatenation of them
    Watch out for daily import:
    * Value of 18th is changed
    * Value of 19th is unchanged
    * Values for 20th to 26th are added on
    """

    df = concatenate_files(['test/HDF_DailyDNP_kWh_01234567890_20-12-2024.csv',
                            'test/HDF_Daily_kWh_01234567890_20-12-2024.csv',
                            'test/HDF_Daily_kWh_01234567890_26-12-2024.csv'])

    assert df is not None

    assert df.shape[0] == 3376
    assert df.shape[1] == 5

    # Import has some data missing
    assert (df[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER).sum() == EXPECTED_IMPORT + 9
    assert (df[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER).sum() == EXPECTED_EXPORT + 9
    assert (df[READ_TYPE] == DAY_PEAK_IMPORT_REGISTER).sum() == EXPECTED_PEAK
    assert (df[READ_TYPE] == DAY_OFF_PEAK_IMPORT_REGISTER).sum() == EXPECTED_DAY
    assert (df[READ_TYPE] == NIGHT_IMPORT_REGISTER).sum() == EXPECTED_NIGHT

    assert df.shape[0] == EXPECTED_IMPORT + EXPECTED_EXPORT + \
           EXPECTED_PEAK + EXPECTED_DAY + EXPECTED_NIGHT + 18  # no stray rows

    import_row_26th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK +
                              EXPECTED_IMPORT + EXPECTED_EXPORT]
    assert import_row_26th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER
    assert import_row_26th[READ_DATE_AND_END_TIME] == '26-12-2024 00:00'
    assert import_row_26th[READ_VALUE] == 34640.640

    export_row_26th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK +
                              EXPECTED_IMPORT + EXPECTED_EXPORT + 1]
    assert export_row_26th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER
    assert export_row_26th[READ_DATE_AND_END_TIME] == '26-12-2024 00:00'
    assert export_row_26th[READ_VALUE] == 5450.502

    import_row_19th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK +
                              EXPECTED_IMPORT + EXPECTED_EXPORT + 14]
    assert import_row_19th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER
    assert import_row_19th[READ_DATE_AND_END_TIME] == '19-12-2024 00:00'
    assert import_row_19th[READ_VALUE] == 34458.640

    export_row_19th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK +
                              EXPECTED_IMPORT + EXPECTED_EXPORT + 15]
    assert export_row_19th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER
    assert export_row_19th[READ_DATE_AND_END_TIME] == '19-12-2024 00:00'
    assert export_row_19th[READ_VALUE] == 5448.502

    import_row_18th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK +
                              EXPECTED_IMPORT + EXPECTED_EXPORT + 16]
    assert import_row_18th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_IMPORT_REGISTER
    assert import_row_18th[READ_DATE_AND_END_TIME] == '18-12-2024 00:00'
    assert import_row_18th[READ_VALUE] == 34400.0

    export_row_18th = df.iloc[EXPECTED_NIGHT + EXPECTED_DAY + EXPECTED_PEAK +
                              EXPECTED_IMPORT + EXPECTED_EXPORT + 17]
    assert export_row_18th[READ_TYPE] == TWENTYFOUR_HR_ACTIVE_EXPORT_REGISTER
    assert export_row_18th[READ_DATE_AND_END_TIME] == '18-12-2024 00:00'
    assert export_row_18th[READ_VALUE] == 5448.502
