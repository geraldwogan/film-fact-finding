import pandas as pd
import json
import re
import requests
import sys

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

def get_data_from_api(api_key, imdb_id):
    # Headers -> User-Agent
    needed_headers = {'User-Agent': "film-fact-finding/1.0"}

    # find/{imdb_id} endpoint
    response = requests.get(f'https://api.themoviedb.org/3/find/{imdb_id}?api_key={api_key}&external_source=imdb_id', headers = needed_headers)

    if response.status_code != 200:
        sys.exit('Invalid API response {0}.'.format(response.status_code))

    # Get movie info from return content
    content = response.json()
    first_result = content['movie_results'][0]
    print(first_result)

    return first_result

def get_info_from_film(film, master):
    # Take info from retrieved movie and 
    # append it to existing data  
    film['Fan Rating'] = master['vote_average']
    film['Popularity'] = master['popularity']
    film['Release Date'] = master['release_date']
    film['Genres'] = master['genre_ids']
    film['Poster Image Source'] = f"https://image.tmdb.org/t/p/original{master['poster_path']}"
    img_type = re.findall(r'[^.]+$', film['Poster Image Source'])[0] # Get file type of image (.jpeg, .png, etc.)
    film['Poster Image Local'] = 'film_posters/' + film['imdb_id'] + '.' + img_type

    try:
        img_data = requests.get(film['Poster Image Source']).content
        with open(film['Poster Image Local'], 'wb') as handler:
            handler.write(img_data)

    except Exception as e:
        film['Poster Image Local'] = 'Download Failure'
        sys.exit(f"Unable to download image {film['Poster Image Source']}, error {e}")

    return film


if __name__ == '__main__':
    src_data = pd.read_excel('data/2021 GW Media Tracking.xlsx', sheet_name='media_tracking', engine='openpyxl')
    films = data_cleaning(src_data)
    test_id = films.iloc[0]['imdb_id'] # tt10872600 - Spider-Man: No Way Home
    
    secrets = get_secrets()
    master =  get_data_from_api(secrets['api_key'], test_id)
    print(get_info_from_film(films.iloc[0], master))


