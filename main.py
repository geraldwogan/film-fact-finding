import pandas as pd
import json
import logging
import os
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

    # print(tidy_films.head())

    log.info(f'Retrieving data for {len(tidy_films)} films.')
    log.debug(f'Films found in media tracking doc: \n{tidy_films.Title}')


    return pd.DataFrame(tidy_films)

def get_secrets():
    # api token info
    json_file = open("resources/secrets.json")
    secrets = json.load(json_file)
    json_file.close()

    return secrets

def get_genres_from_api(api_key):
    # Headers -> User-Agent
    needed_headers = {'User-Agent': "film-fact-finding/1.0"}

    # find/{imdb_id} endpoint
    response = requests.get(f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}', headers = needed_headers)

    if response.status_code != 200:
        sys.exit('Invalid API response {0}.'.format(response.status_code))

    # Get movie info from return content
    content = response.json()
    # print(content)

    return content['genres']

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
    # print(first_result)

    return first_result

def get_info_from_film(film, master):
    # Take info from retrieved movie and 
    # append it to existing data  
    film['Fan Rating'] = master['vote_average']
    film['Popularity'] = master['popularity']
    film['Release Date'] = master['release_date']

    film['Genre_IDs'] = master['genre_ids']
    film['Genres'] = get_genre_from_ids(film)

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

def get_genre_from_ids(film): # TODO: Change to list comprehension?
    # Initialize list
    genre_names = []

    # Get Name of Genre from ID for each ID
    for id in film['Genre_IDs']:
        genre_names.append(genres.get(id, {}).get('name'))
    
    # Return list of Genres e.g. [Action, Adventure, Science Fiction]
    return genre_names


if __name__ == '__main__':
    global genres 

    # Setup logging
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    log = logging.getLogger('film-logger')
    log.info('Starting...')

    src_data = pd.read_excel('data/2021 GW Media Tracking.xlsx', sheet_name='media_tracking', engine='openpyxl')
    films = data_cleaning(src_data)
    secrets = get_secrets()
    genres = get_genres_from_api(secrets['api_key'])
    # Re-index genres 
    genres = dict((item.get('id'), item) for item in genres)

    for idx, film in films.iterrows():
        print(type(film))
        master = get_data_from_api(secrets['api_key'], film['imdb_id'])
        print(get_info_from_film(film, master))
