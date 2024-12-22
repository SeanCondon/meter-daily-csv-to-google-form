from main import main


def test_sample():
    assert 1 == 1


def test_main():
    main('test/HDF_DailyDNP_kWh_01234567890_20-12-2024.csv',
         'test/HDF_Daily_kWh_01234567890_20-12-2024.csv',
         'https://docs.google.com/forms/d/e/your-form-id/formResponse')
