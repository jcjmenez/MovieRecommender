import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

# Obtiene el titulo completo de la pelicula a partir de una parte de este
def get_full_title(movies_titles, title):
    found_movies = []
    try:
        for i in range(np.size(movies_titles)):
            if title.lower() in movies_titles[i].split(" (")[0].lower():
                found_movies.append(movies_titles[i])
    except:
        found_movies[0] = "Toy Story (1995)"
    return found_movies[0]

# Devuelve una lista de recomendaciones para la pelicula pasada por referencia
def recommendations(title, number_of_recommendations):
    pd.set_option('display.max_rows', None)
    movies = pd.read_csv('dataset/movies.csv')
    ratings = pd.read_csv('dataset/ratings.csv')
    # Rating minimo = 0.5
    # Rating maximo = 5

    movies_titles = movies['title'].values
    dataset = pd.merge(movies, ratings, how='left', on='movieId')
    #print(dataset)
    table = dataset.pivot_table(index='title', columns='userId', values='rating')
    # Si no ha valorado = NaN, lo cambiamos por 0
    table = table.fillna(0)
    # Creamos una matriz con las valoraciones utilizando csr_matrix de scipy
    matrix = csr_matrix(table.values)
    # Calculamos la similitud del coseno utilizando cosine similarity
    cosine = cosine_similarity(matrix, matrix)
    # Obtenemos el titulo completo
    full_title = get_full_title(movies_titles, title)
    table.reset_index()
    # Localizamos donde se encuentra la id de la pelicula en la tabla de pivote
    idx_movie_name = 0
    for idx in range(table.shape[0]):
        if table.iloc[idx].name == full_title:
            idx_movie_name = idx
    print("Recomendaciones para " + table.index[idx_movie_name])
    scores = list(enumerate(cosine[idx_movie_name]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    recommendations_arr = []
    # Añadimos las recomendaciones hasta llegar al numero deseado
    idx_score = 0
    while len(recommendations_arr) < number_of_recommendations:
        if scores[idx_score][0] != idx_movie_name:
            recommendations_arr.append(scores[idx_score])
        idx_score += 1
    print(recommendations_arr)
    print("")
    movie_indices = [i[0] for i in recommendations_arr]
    movie_names = []
    for i in range(len(movie_indices)):
        movie_names.append(table.iloc[movie_indices[i]].name)
    return movie_names
















