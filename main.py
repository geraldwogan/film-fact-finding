import pandas as pd

# Connect to API
# Read source data from excel file
# Extract IMBD ID from data
# Fetch target data from API, using ID'S

src_data = pd.read_excel('data/2021 GW Media Tracking.xlsx', sheet_name='media_tracking', engine='openpyxl')
