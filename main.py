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

def test_connection(api_key,  imdb_id):
    needed_headers = {'User-Agent': "film-fact-finding/1.0"}
    response = requests.get(f'https://api.themoviedb.org/3/find/{imdb_id}?api_key={api_key}&external_source=imdb_id', headers = needed_headers)
    
    print(response.status_code)
    content = response.json()
    # print(content['movie_results'][0]['popularity'])

    first_result = content['movie_results'][0]

    return first_result

if __name__ == '__main__':
    src_data = pd.read_excel('data/2021 GW Media Tracking.xlsx', sheet_name='media_tracking', engine='openpyxl')
    films = data_cleaning(src_data)
    test_id = films.iloc[0]['imdb_id'] # tt10872600 - Spider-Man: No Way Home
    secrets = get_secrets()
    film =  test_connection(secrets['api_key'], test_id)
    print(film)
