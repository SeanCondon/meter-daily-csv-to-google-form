import pandas as pd
import requests
from datetime import datetime, timedelta
from loguru import logger

def read_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {e}")
        return None

def extract_last_week_entries(data):
    try:
        one_week_ago = datetime.now() - timedelta(days=7)
        data['date'] = pd.to_datetime(data['date'])
        last_week_data = data[data['date'] >= one_week_ago]
        return last_week_data
    except Exception as e:
        logger.error(f"Error extracting last week entries: {e}")
        return None

def send_to_google_form(data, form_url):
    try:
        for index, row in data.iterrows():
            response = requests.post(form_url, data=row.to_dict())
            if response.status_code != 200:
                logger.error(f"Error sending data to Google Form: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending data to Google Form: {e}")

def main():
    logger.info("Script started")
    
    file1 = 'path/to/your/csvfile1.csv'
    file2 = 'path/to/your/csvfile2.csv'
    form_url = 'https://docs.google.com/forms/d/e/your-form-id/formResponse'
    
    data1 = read_csv(file1)
    data2 = read_csv(file2)
    
    if data1 is not None and data2 is not None:
        last_week_data1 = extract_last_week_entries(data1)
        last_week_data2 = extract_last_week_entries(data2)
        
        if last_week_data1 is not None:
            send_to_google_form(last_week_data1, form_url)
        
        if last_week_data2 is not None:
            send_to_google_form(last_week_data2, form_url)
    
    logger.info("Script finished")

if __name__ == "__main__":
    main()
