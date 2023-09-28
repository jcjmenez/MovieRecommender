import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
import nltk
from nltk.stem.porter import PorterStemmer
nltk.download('punkt')
warnings.filterwarnings('ignore')

# Funcion que tokeniza texto usando el stemmer PorterStemmer
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = []
    for item in tokens:
        stems.append(PorterStemmer().stem(item))
    return stems

# Funcion que pasa  texto a minuscula
def to_lower_case(text):
    text = text.lower()
    return text

def predict_from_user(user_path):
    # Carga de datos
    user = pd.read_csv(user_path, sep=";")
    movie = pd.read_csv("dataset/moviessynopsis.csv")
    ratings = pd.read_csv("dataset/ratings.csv")
    links = pd.read_csv("dataset/links.csv")
    tags = pd.read_csv("dataset/tags.csv")

    # Quitamos las timestamps debido a que no aportan ningun valor a la prediccion
    ratings.drop(columns='timestamp',inplace=True)
    tags.drop(columns=['timestamp', 'userId'],inplace=True)

    # Extraemos el año del titulo
    movie['Year'] = movie['title'].str.extract('.*\((.*)\).*',expand = False)
        
    # Añadimos los tags y juntamos todos los tags de cada pelicula en una columna   
    movie = pd.merge(movie, tags,how='outer',on='movieId')
    movie.fillna('', inplace=True)
    movie['tag'] = movie.groupby(['movieId', 'title', 'Year', 'genres'])['tag'].transform(lambda x: ' '.join(x))
    movie = movie.drop_duplicates(subset='movieId', keep="first")

    #print(movie.columns)
    # Juntamos todas las columnas en una general llamada tfidf a la que le aplicaremos PLN
    movie["tfidf"] = movie.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    # Reemplazamos los | por espacios a los generos dentro la columna tfidf
    movie["tfidf"] = movie["tfidf"].str.replace("|", " ")
    movie['tfidf'] = movie['tfidf'].apply(to_lower_case)
    #print(movie["tfidf"].iloc[0])
    # Eliminamos las demas colunmas (solo necesitamos tfidf)
    #movie.drop(['title', 'genres', 'Year'], axis=1, inplace=True)

    movie.drop(['genres', 'Year'], axis=1, inplace=True)

    # Pasamos el texto completo al usuario
    user = pd.merge(user,movie,how='inner',on='movieId')

    user.sort_index(inplace=True)   
    pd.set_option('display.max_columns', None) 
    #print(user)
    #from scraper import get_synopsis_from_id, get_imdbid_from_id
    #user['tfidf'] = user['tfidf'].apply(lambda x: "{} {}".format(get_synopsis_from_id(get_imdbid_from_id(x[0])), x))

    # Entrenamiento
    
    X = user["tfidf"]
    tfidf_vectorizer = TfidfVectorizer(tokenizer=tokenize, analyzer='word', ngram_range=(1,2), stop_words="english")
    X = tfidf_vectorizer.fit_transform(X)
    y = user["rating"]
    X_train , X_test , y_train , y_test = train_test_split(X ,y ,test_size=0.20 ,random_state = 1)
    rfregressor = RandomForestRegressor(random_state=1)
    rfregressor.fit(X_train,y_train)

    y_pred = rfregressor.predict(X_test)
    print(y_pred)
    print("Accuracy: ")
    print(rfregressor.score(X_test, y_test))
    print("Desviacion:")
    print(mean_absolute_error(y_test, y_pred))

    # Prediccion
    # Seleccionamos solo las peliculas que no haya valorado el usuario
    movie_X = pd.merge(movie,user, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
    # Obtenemos los titulos de las peliculas
    movie_X_titles = movie_X[["title"]]
    # Eliminamos los titulos y las valoraciones
    movie_X.drop(columns=["title", "rating"], inplace=True)
    # Vectorizamos las peliculas
    movies_to_tfidf = movie_X["tfidf"]
    tfidf_movies = tfidf_vectorizer.transform(movies_to_tfidf)
    y_pred = rfregressor.predict(tfidf_movies)
    #print(y_pred)
    movie_X_titles["pred"] = y_pred
  
    movie_title_X = movie_X_titles.sort_values(by="pred", ascending=False)
    results = {}
    results["name"] = movie_title_X["title"].tolist()
    results["score"] = movie_title_X["pred"].tolist()
    return results
    