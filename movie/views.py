from django.shortcuts import render, redirect
from .models import CustomUser, MovieUser, WatchList
from .forms import SignupForm, LoginForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login as auth_login, logout
from .helper import authenticate
import requests
from functools import wraps
import os 
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


def index(request):
    return render(request, 'movie/index.html')

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data.get("username")
            em = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            if CustomUser.objects.filter(email = em).exists():
                messages.info(request, "User with this email already exists, Login instead.")
                return redirect('login')
            elif CustomUser.objects.filter(username = uname).exists():
                messages.warning(request, "User with this username already exists")
                return redirect('signup')
            else :
                user = CustomUser.objects.create_user(
                    username=uname,
                    password=password,
                    email=em
                )
                user.save()
                messages.info(request, "User created successfully, Please Login")
                return redirect("login")
        else:
            print(form.errors)
            messages.error(request, "Please enter a valid email address")
    else:
        form = SignupForm()
    return render(request, 'movie/signup.html', {'form':form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        # print(form.is_valid())
        # print(form.errors)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("username")
            user = authenticate(username, password)
            # print(user)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password")
                return redirect('login')
    else:
        form = LoginForm()
        return render(request, 'movie/login.html', {'form' : form})
    
def logOut(request):
    logout(request)
    return redirect('index')

genres = {28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction', 10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western'}

def get_movie(request):
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    if request.method == "POST":
        search_movie = request.POST.get('search_movie')
        url = f'https://api.themoviedb.org/3/search/movie?query={search_movie}&api_key={API_KEY}'

        response = requests.get(url)
        global movie_list
        counter = 0
        movie_list = []
        for i in response.json()['results']:
            movie = i['original_title'].lower().replace(' ', '-').replace( "'", '-')
            id = i['id']
            movie_list.append({
                'id' : counter,
                'unique_id' : id,
                'title' : i['original_title'],
                'overview' : i['overview'],
                'release_date' : i['release_date'],
                'link' : f"https://www.themoviedb.org/movie/{id}-{movie}",
                'poster_path' : f"https://image.tmdb.org/t/p/w500{i['poster_path']}",
                'rating' : i['vote_average'],
                'genre' : " ".join(genres[int(j)] for j in i['genre_ids'])
            })
            counter+=1

        if len(movie_list) != 0:
            return render(request, 'movie/index.html', {'card' : movie_list[0]})
        else:
            return render(request, 'movie/index.html')
    
def fetch(request, id, text):
    if text == 'next':
        if id < len(movie_list) - 1:
            next_id = id + 1
            return render(request, 'movie/index.html', {'card' : movie_list[next_id]})
        else: 
            return render(request, 'movie/index.html', {'card' : movie_list[id]})
    elif text == 'prev':
        if id > 0:
            prev_id = id - 1
            return render(request, 'movie/index.html', {'card' : movie_list[prev_id]})
        else: 
            return render(request, 'movie/index.html', {'card' : movie_list[id]})

def login_required(func):
    @wraps(func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            messages.error(request, "Login Required to perform this action!!!")
            return redirect('login')
    return wrapper_func


@login_required
def add_to_list(request, id, type):
    current_user = request.user
    uni = movie_list[id]['unique_id']
    fetch_movie = WatchList.objects.filter(u_id = current_user, m_id = uni).first()
    if fetch_movie:
        fetch_movie.show_type = type
        fetch_movie.save()
        return render(request, 'movie/index.html', {'card' : movie_list[id]})
    try:
        movie_to_add = MovieUser.objects.get(mid = uni)
    except MovieUser.DoesNotExist:
        movie_to_add = MovieUser(
            mid = movie_list[id]['unique_id'],
            title = movie_list[id]['title'],
            overview = movie_list[id]['overview'],
            release_date = movie_list[id]['release_date'],
            poster_path = movie_list[id]['poster_path'],
            link = movie_list[id]['link'],
            rating = movie_list[id]['rating'],
            genre = movie_list[id]['genre']
        )
    map_user_and_movie = WatchList (
        show_type = type,
        u_id = current_user,
        m_id = movie_to_add
    )
    movie_to_add.save()
    map_user_and_movie.save()
    return render(request, 'movie/index.html', {'card' : movie_list[id]})


@login_required
def watchlist(request, type):
    current_user = request.user
    fetch_watchlist = WatchList.objects.filter(u_id = current_user, show_type = type)
    movie_ids = [movie.m_id.mid for movie in fetch_watchlist]
    fetch_movies = MovieUser.objects.filter(mid__in= movie_ids)
    return render(request, 'movie/wishlist.html', {'cards' : fetch_movies, 'type' : type.capitalize()})


@login_required
def remove_from_watchlist(request, uni):
    current_user = request.user
    movie = MovieUser.objects.filter(mid = uni).first()
    remove_movie = WatchList.objects.filter(u_id = current_user, m_id = movie).first()
    print(remove_movie)
    type = remove_movie.show_type
    remove_movie.delete()
    if not WatchList.objects.filter(m_id = movie):
        movie.delete()
        messages.success(request, f"{movie.title} has been removed from your watchlist")
        return redirect('watchlist', type=type)
    else:
        messages.success(request, f"{movie.title} has been removed from your watchlist")
        return redirect('watchlist', type=type)


@login_required
def change_watchlist(request, uni, type):
    fetch_movie = WatchList.objects.filter(u_id = request.user, m_id = uni).first()
    fetch_movie.show_type = type
    fetch_movie.save()
    return redirect('watchlist', type=type)


def recommend_by_genre(request):
    if request.method == "POST":
        genres = request.POST.getlist('preferences')
        df = pd.read_csv('movie/data/top_100k_movies.csv').sample(100000)
        new_df = df.filter(['id', 'genres' ,'keywords' ,'overview' ,'original_title' ,'cast' ,'director', 'vote_average'])
        new_df['genres'] = new_df['genres'].str.replace('|', ' ')
        new_df['keywords'] = new_df['keywords'].str.replace('|', ' ')
        new_df['content'] = new_df['genres'] + ' ' + new_df['overview'] + ' ' + new_df['keywords'] + ' ' + new_df['original_title']
        tf_idf = TfidfVectorizer(stop_words='english')
        tf_idf_matrix = tf_idf.fit_transform(new_df['content'].values.astype('str'))
        keyword_vector = tf_idf.transform([str(genres)])
        keyword_sim_scores = cosine_similarity(keyword_vector, tf_idf_matrix)
        sim_scores = list(enumerate(keyword_sim_scores[0]))
        sim_scores = sorted(sim_scores, key=lambda x:x[1], reverse=True)
        movie_indices = [i[0] for i in sim_scores[:10]] 
        movies = new_df['original_title'].iloc[movie_indices]
        global movie_list
        movie_list = []         #recommended_movies
        counter = 0
        for movie in list(movies):
            response = requests.get(url=f"https://api.themoviedb.org/3/search/movie?query={movie}&api_key={os.getenv('API_KEY')}")
            try:
                m = response.json()['results'][0]
            except:
                pass
            else:
                movie_list.append({
                    'id' : counter,
                    'unique_id' : m['id'],
                    'title' : m['original_title'],
                    'overview' : m['overview'],
                    'release_date' : m['release_date'],
                    'link' : f"https://www.themoviedb.org/movie/{m['id']}-{movie}",
                    'poster_path' : f"https://image.tmdb.org/t/p/w500{m['poster_path']}",
                    'rating' : m['vote_average']
                })
                counter+=1
        if len(movie_list) != 0:
            return render(request, 'movie/index.html', {'card' : movie_list[0]})
        else:
            return redirect('index')

def recommend(request):
    user = request.user
    movies = WatchList.objects.filter(u_id=user.id)
    contents = []
    for movie in movies:
        m = MovieUser.objects.get(mid=movie.m_id_id)
        contents.append(f"{m.genre} {m.overview} {m.title}")
    if len(contents) >= 4:
        df = pd.read_csv('movie/data/top_100k_movies.csv').sample(100000)
        new_df = df.filter(['id', 'genres' ,'keywords' ,'overview' ,'original_title' ,'cast' ,'director', 'vote_average'])
        new_df['genres'] = new_df['genres'].str.replace('|', ' ')
        new_df['keywords'] = new_df['keywords'].str.replace('|', ' ')
        new_df['content'] = new_df['genres'] + ' ' + new_df['overview'] + ' ' + new_df['keywords']
        tf_idf = TfidfVectorizer(stop_words='english')
        tf_idf_matrix = tf_idf.fit_transform(new_df['content'].values.astype('str'))
        global movie_list
        movie_list = []         #recommended_movies
        counter = 0
        for m_detail in contents:
            keyword_vector = tf_idf.transform([m_detail])
            keyword_sim_scores = cosine_similarity(keyword_vector, tf_idf_matrix)
            sim_scores = list(enumerate(keyword_sim_scores[0]))
            sim_scores = sorted(sim_scores, key=lambda x:x[1], reverse=True)
            movie_indices = [i[0] for i in sim_scores[:10]] 
            movies = new_df['original_title'].iloc[movie_indices]
            
            for movie in list(movies):
                response = requests.get(url=f"https://api.themoviedb.org/3/search/movie?query={movie}&api_key={os.getenv('API_KEY')}")
                try:
                    m = response.json()['results'][0]
                except:
                    pass
                else:
                    movie_list.append({
                        'id' : counter,
                        'unique_id' : m['id'],
                        'title' : m['original_title'],
                        'overview' : m['overview'],
                        'release_date' : m['release_date'],
                        'link' : f"https://www.themoviedb.org/movie/{m['id']}-{movie}",
                        'poster_path' : f"https://image.tmdb.org/t/p/w500{m['poster_path']}",
                        'rating' : m['vote_average']
                    })
                    counter+=1
        if len(movie_list) != 0:
            return render(request, 'movie/index.html', {'card' : movie_list[0]})
        else:
            return redirect('index')
    else:
        messages.info(request, "Please at least have 4 movies in your Watchlist to get recommendations.")
        return redirect('index')