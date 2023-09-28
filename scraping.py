import requests
from bs4 import BeautifulSoup
import pandas as pd

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
headers = {"user-agent": USER_AGENT, 'Accept-Language': 'en-US, en;q=0.5'}

# Parametro se pasa com string porque no admite leading zeros
def get_image_from_id(imdb_id):
    url = "https://www.imdb.com/title/tt" + imdb_id
    
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    imgs = soup.find_all('a', class_="ipc-lockup-overlay")
    href_link = imgs[0].get("href")
    url = "https://www.imdb.com/" + href_link
    img_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(img_data.text, 'html.parser')
    href_divs = soup.find_all('div', class_="kEDMKk")
    img_link = ""
    for img in href_divs[0]:
        img_link = img.get("src")
    return img_link
       

# Obtiene la sinopsis de la pelicula a partir de la id en imdb
def get_synopsis_from_id(imdb_id):
    synopsis_text = ""
    try:
        print(imdb_id)
        if len(imdb_id) > 5:
            url = "https://www.imdb.com/title/tt" + imdb_id
            data = requests.get(url, headers=headers)
            soup = BeautifulSoup(data.text, 'html.parser')
            synopsis = soup.find_all('span', class_="qqCya")
            synopsis_text = synopsis[0].text
            print(synopsis_text)
    except Exception as e:
        print(e)
    return synopsis_text
    

# Obtiene la id de imdb a partir de la id de la pelicula en movielens
def get_imdb_id(name):
    links = pd.read_csv('dataset/links.csv', dtype=str)
    movies = pd.read_csv('dataset/movies.csv')
    movie_id = movies[movies['title'] == name]['movieId'].values[0]
    #print(movie_id)
    
    # movies['movieId'] = pd.to_numeric(movies['movieId'])
    # links_movies = pd.merge(movies, links, how='outer', on='movieId')
    link_id = links[links['movieId'] == str(movie_id)]
    id = link_id['imdbId'].values[0]
    return id

# Funcion para extraer y guardar la sinopsis de IMDB en las peliculas
def save_synopsis():
    links = pd.read_csv("dataset/links.csv", dtype=str)
    moviessynopsis = pd.read_csv("dataset/movies.csv", dtype=str)
    moviessynopsis["sinopsis"] = links.apply(lambda row : get_synopsis_from_id(row[1]), axis=1)
    moviessynopsis.to_csv('dataset/sinopsis.csv', index=False)



