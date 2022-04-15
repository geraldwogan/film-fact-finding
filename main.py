import pandas as pd
import json
import requests

def data_cleaning(all_media):
    # Extract 'Movie' data from source dataset.
    films = all_media[all_media["Medium"]=="Movie"].copy()

    # Extract IMDB ID
    films.loc[:,"imdb_id"] = films["Standardised ID"].str.split('/').str[-2]

    # Create tidy df with just the relevant info
    tidy_films = films.loc[:,["Num", "Title", "Creator/Season", "Date Started", "Date Finished", "Days", "Month", "imdb_id"]]

    print(tidy_films.head())

    return tidy_films

def get_secrets():
    # api token info
    json_file = open("resources/secrets.json")
    secrets = json.load(json_file)
    json_file.close()

    return secrets

def test_connection(api_key):
    needed_headers = {'User-Agent': "film-fact-finding/1.0"}
    response = requests.get(f'https://api.themoviedb.org/3/movie/76341?api_key={api_key}', headers = needed_headers) # 76341 = Mad Max
    print(response.status_code)
    print(response.content)

    return response

if __name__ == '__main__':
    secrets = get_secrets()
    test_connection(secrets['api_key'])

    src_data = pd.read_excel('data/2021 GW Media Tracking.xlsx', sheet_name='media_tracking', engine='openpyxl')
    films = data_cleaning(src_data)